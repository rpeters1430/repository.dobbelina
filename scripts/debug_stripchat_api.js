const { chromium } = require('@playwright/test');

const UA =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
  '(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36';

function shortHeaders(headers) {
  const keep = new Set([
    'user-agent',
    'referer',
    'origin',
    'accept',
    'cookie',
    'sec-fetch-site',
    'sec-fetch-mode',
  ]);
  const out = {};
  for (const [key, value] of Object.entries(headers || {})) {
    const lower = key.toLowerCase();
    if (!keep.has(lower)) continue;
    if (lower === 'cookie' && typeof value === 'string' && value.length > 200) {
      out[key] = value.slice(0, 200) + '...<trimmed>';
    } else {
      out[key] = value;
    }
  }
  return out;
}

function shouldCapture(url) {
  const lower = String(url || '').toLowerCase();
  if (!['.m3u8', '.mp4', '.m4s'].some((ext) => lower.includes(ext))) return false;
  if (['/thumbs/', '/images/', '.jpg', '.png', '/image/', '/thumb/'].some((x) => lower.includes(x))) return false;
  return true;
}

async function run(url) {
  console.log(`[*] Analyzing browser traffic for: ${url}`);
  console.log('[*] This runs outside Kodi and prints the real browser media requests.');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    userAgent: UA,
  });
  const page = await context.newPage();

  const seen = new Set();
  const mediaEvents = [];
  const targetHost = new URL(url).host.toLowerCase();
  let stopEarly = false;

  function logMediaEvent(kind, request, response = null, bodyText = null) {
    const reqUrl = request.url();
    if (seen.has(`${kind}:${reqUrl}`)) return;
    if (!shouldCapture(reqUrl)) return;
    seen.add(`${kind}:${reqUrl}`);

    const event = {
      kind,
      url: reqUrl,
      method: request.method(),
      resource_type: request.resourceType(),
      headers: shortHeaders(request.headers()),
    };
    if (response) {
      event.status = response.status();
      event.response_headers = shortHeaders(response.headers());
    }
    if (bodyText) {
      event.body_preview = bodyText.slice(0, 800);
    }
    mediaEvents.push(event);
    if (response && response.status() === 200) {
      stopEarly = true;
    }

    console.log(`\n[MEDIA ${kind.toUpperCase()}] ${reqUrl}`);
    console.log(`  method=${event.method} type=${event.resource_type}`);
    if (typeof event.status !== 'undefined') {
      console.log(`  status=${event.status}`);
    }
    if (Object.keys(event.headers).length) {
      console.log(`  request_headers=${JSON.stringify(event.headers, null, 2)}`);
    }
    if (event.response_headers && Object.keys(event.response_headers).length) {
      console.log(`  response_headers=${JSON.stringify(event.response_headers, null, 2)}`);
    }
    if (bodyText) {
      if (bodyText.includes('#EXT-X-MOUFLON')) {
        console.log('  manifest_type=MOUFLON');
      } else if (bodyText.includes('#EXTM3U')) {
        console.log('  manifest_type=STANDARD');
      }
      console.log(`  body_preview=${bodyText.slice(0, 400).replace(/\n/g, '\\n')}`);
    }
  }

  page.on('request', (request) => {
    const lower = request.url().toLowerCase();
    if (lower.includes(targetHost) && lower.includes('widget')) {
      console.log(`\n[API REQUEST] ${request.url()}`);
    }
    if (shouldCapture(request.url())) {
      logMediaEvent('request', request);
    }
  });

  page.on('response', async (response) => {
    const request = response.request();
    try {
      const lower = response.url().toLowerCase();
      const headers = response.headers();
      const ct = String(headers['content-type'] || '').toLowerCase();

      if (lower.includes(targetHost) && ct.includes('application/json')) {
        try {
          const data = await response.json();
          const asText = JSON.stringify(data);
          if (asText.toLowerCase().includes('stream') || asText.toLowerCase().includes('hls')) {
            console.log(`\n[API JSON] ${response.url()}`);
            console.log(JSON.stringify(data, null, 2).slice(0, 1500));
          }
        } catch (_) {}
      }

      let bodyText = null;
      if (lower.includes('.m3u8')) {
        try {
          bodyText = await response.text();
        } catch (_) {}
      }

      if (shouldCapture(response.url())) {
        logMediaEvent('response', request, response, bodyText);
      }
    } catch (err) {
      console.log(`[!] response handler error: ${err}`);
    }
  });

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    console.log('[*] Page loaded');
    await page.waitForTimeout(3000);

    const playSelectors = [
      'video',
      'button',
      '.vjs-big-play-button',
      '.play-button',
      "[data-test='video-play-button']",
    ];
    for (const selector of playSelectors) {
      try {
        const locator = page.locator(selector).first();
        if (await locator.isVisible({ timeout: 1000 })) {
          console.log(`[*] Clicking ${selector}...`);
          await locator.click({ force: true, timeout: 3000 });
          await page.waitForTimeout(2000);
        }
      } catch (_) {}
    }

    console.log('[*] Waiting up to 15s for media traffic...');
    for (let i = 0; i < 15; i++) {
      await page.waitForTimeout(1000);
      if (stopEarly) {
        console.log('[*] Captured successful media response, stopping early.');
        break;
      }
    }

    console.log(`\n[*] Media event count: ${mediaEvents.length}`);
    console.log('[*] Unique media URLs captured:');
    for (const event of mediaEvents) {
      const status = typeof event.status === 'undefined' ? '' : `${event.status}`;
      console.log(` - ${event.kind.toUpperCase()} ${status} ${event.url}`.trim());
    }
  } finally {
    await browser.close();
  }
}

const target = process.argv[2] || 'https://stripchat.com/RussianWoman';
run(target).catch((err) => {
  console.error(err);
  process.exit(1);
});
