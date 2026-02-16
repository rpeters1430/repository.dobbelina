const { chromium } = require('@playwright/test');

async function fetch(url, waitFor = 'networkidle', waitForSelector = null, timeout = 30000, headers = {}) {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        extraHTTPHeaders: headers
    });
    const page = await context.newPage();

    try {
        await page.goto(url, { waitUntil: waitFor, timeout: timeout });
        
        if (waitForSelector) {
            await page.waitForSelector(waitForSelector, { timeout: timeout });
        }

        const html = await page.content();
        process.stdout.write(html);
    } catch (e) {
        console.error(e.message);
        process.exit(1);
    } finally {
        await browser.close();
    }
}

const args = JSON.parse(process.argv[2]);
fetch(args.url, args.waitFor, args.waitForSelector, args.timeout, args.headers);
