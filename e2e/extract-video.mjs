import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

function nowIsoSafe() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function parseAllowDomains() {
  const raw = (process.env.ALLOW_DOMAINS || "").trim();
  if (!raw) return [];
  return raw.split(",").map(s => s.trim()).filter(Boolean);
}

function hostnameOf(u) {
  try { return new URL(u).hostname; } catch { return ""; }
}

function allowedByDomain(u, allowDomains) {
  if (!allowDomains.length) return true; // no allowlist => allow all
  const h = hostnameOf(u);
  return allowDomains.some(d => h === d || h.endsWith("." + d));
}

function isNoisyLowLatency(u) {
  return /_HLS_(msn|part)=/i.test(u);
}

function isSegmentLike(u) {
  // chunk/segment-ish URLs; keep them in "all", but don't pick as "best"
  return /(_init_|_part\d+\.mp4\b)|(\.ts(\?|$))|(\.m4s(\?|$))/i.test(u);
}

function isCandidateMediaUrl(u) {
  return /(\.m3u8|\.mp4|\.ts|\.m4s)(\?|$)/i.test(u) || /\/hls\//i.test(u);
}

async function validateM3U8(page, url) {
  const isAdLike = (text) => {
    if (!text) return false;
    return (
      /#EXT-X-MOUFLON-ADVERT/i.test(text) ||
      /\/cpa\/v2\//i.test(text) ||
      /vast|vmap|doubleclick|adserver|tracking|analytics/i.test(text)
    );
  };

  const firstPlaylistUrls = (text) => {
    if (!text) return [];
    const out = [];
    for (const raw of text.split("\n")) {
      const line = raw.trim();
      if (!line || line.startsWith("#")) continue;
      if (/\.m3u8(\?|$)/i.test(line)) out.push(line);
      if (out.length >= 2) break;
    }
    return out;
  };

  try {
    const resp = await page.request.get(url, { timeout: 15000 });
    if (!resp.ok()) return { ok: false, why: `HTTP ${resp.status()}` };

    const headers = resp.headers();
    const ct = (headers["content-type"] || "").toLowerCase();
    const text = await resp.text();

    const hasExtM3u = text.includes("#EXTM3U");
    const isMaster = text.includes("#EXT-X-STREAM-INF");
    const isMedia = text.includes("#EXTINF") || text.includes("#EXT-X-PART");
    const adHints = isAdLike(text);
    let childAdHints = false;
    let childChecked = 0;

    if (hasExtM3u && isMaster) {
      const childUrls = firstPlaylistUrls(text);
      for (const child of childUrls) {
        const childUrl = new URL(child, url).toString();
        try {
          const cResp = await page.request.get(childUrl, { timeout: 15000 });
          if (!cResp.ok()) continue;
          const cText = await cResp.text();
          childChecked += 1;
          if (isAdLike(cText)) {
            childAdHints = true;
            break;
          }
        } catch {
          // ignore child fetch failure and keep evaluating other children
        }
      }
    }

    const ok = hasExtM3u && (isMaster || isMedia) && !adHints && !childAdHints;

    return {
      ok,
      why: `ct=${ct || "?"} extm3u=${hasExtM3u} master=${isMaster} media=${isMedia} adHints=${adHints} childAdHints=${childAdHints} childChecked=${childChecked}`,
      isMaster,
      isMedia,
      adHints,
      childAdHints,
    };
  } catch (e) {
    return { ok: false, why: `fetch error: ${String(e)}` };
  }
}

function scoreUrl(u, meta, validation) {
  let score = 0;

  // Prefer stable playlists
  if (/\.m3u8(\?|$)/i.test(u)) score += 50;
  if (u.includes("/master/")) score += 30;

  // Prefer "media" resource type if we saw it as such
  if (meta?.types?.has("media")) score += 15;

  // Penalize noisy low-latency params (moment-in-time)
  if (isNoisyLowLatency(u)) score -= 50;

  // Penalize segment-like URLs
  if (isSegmentLike(u)) score -= 40;

  // Validation boosts
  if (validation?.ok) score += 25;
  if (validation && validation.ok === false) score -= 15;

  // Some extra heuristics
  if (/blob:/i.test(u)) score -= 100;

  return score;
}

async function main() {
  if (process.argv.length < 3) {
    console.error("Usage: node extract-video.mjs <URL>");
    process.exit(1);
  }

  const targetUrl = process.argv[2];
  const navTimeoutMs = Number(process.env.NAV_TIMEOUT_MS || "60000");
  const dumpN = Number(process.env.DUMP_N || "30");
  const allowDomains = parseAllowDomains();

  const outDir = process.env.OUT_DIR || ".";
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await context.newPage();

  // url -> { count, types:Set, firstSeen, lastSeen }
  const seen = new Map();

  function noteUrl(u, type) {
    if (!u || typeof u !== "string") return;
    if (!isCandidateMediaUrl(u)) return;

    const entry = seen.get(u) ?? {
      url: u,
      count: 0,
      types: new Set(),
      firstSeen: Date.now(),
      lastSeen: Date.now(),
    };
    entry.count += 1;
    if (type) entry.types.add(type);
    entry.lastSeen = Date.now();
    seen.set(u, entry);
  }

  page.on("request", (req) => {
    noteUrl(req.url(), req.resourceType());
  });

  page.on("response", (resp) => {
    // response doesn’t expose resourceType; keep it anyway
    noteUrl(resp.url(), "response");
  });

  try {
    console.log(`Navigating to ${targetUrl} (timeout ${navTimeoutMs}ms)...`);
    try {
      await page.goto(targetUrl, { waitUntil: "domcontentloaded", timeout: navTimeoutMs });
    } catch (err) {
      console.warn("Navigation did not fully complete, continuing with partial page.");
      console.warn(String(err));
    }

    // Let network/media settle a bit
    await page.waitForTimeout(3000);

    // Best-effort age gate click (if shown).
    const ageButtons = [
      "button:has-text(\"I'm Over\")",
      "button:has-text(\"I am over 18\")",
      "button:has-text(\"Enter\")",
      "button:has-text(\"Continue\")",
    ];
    for (const selector of ageButtons) {
      const btn = page.locator(selector).first();
      if (await btn.isVisible().catch(() => false)) {
        await btn.click().catch(() => {});
        await page.waitForTimeout(1500);
        break;
      }
    }

    // Screenshot (full page)
    const imagePath = path.join(outDir, "site-latest.png");
    await page.screenshot({ path: imagePath, fullPage: true });
    console.log(`Screenshot saved to ${imagePath}`);

    // Also scrape DOM for video/src + any .m3u8 strings in HTML
    const pageData = await page.evaluate(() => {
      const urls = new Set();

      document.querySelectorAll("video").forEach((video) => {
        if (video.src) urls.add(video.src);
        video.querySelectorAll("source").forEach((src) => {
          if (src.src) urls.add(src.src);
        });
      });

      const html = document.documentElement?.innerHTML || "";
      for (const match of html.matchAll(/https?:\/\/[^"'\\s]+\.m3u8[^"'\\s]*/gi)) {
        if (match[0]) urls.add(match[0]);
      }
      return Array.from(urls);
    });

    for (const u of pageData) noteUrl(u, "dom");

    // Convert map to array and sort
    const all = Array.from(seen.values())
      .map(e => ({
        url: e.url,
        count: e.count,
        types: Array.from(e.types),
        host: hostnameOf(e.url),
        firstSeen: e.firstSeen,
        lastSeen: e.lastSeen,
      }))
      .sort((a, b) => a.url.localeCompare(b.url));

    // Write all candidates
    fs.writeFileSync(path.join(outDir, "candidates.json"), JSON.stringify(all, null, 2));
    fs.writeFileSync(path.join(outDir, "candidates_all.txt"), all.map(x => x.url).join("\n") + "\n");

    // Build shortlist for “best”
    const shortlist = all
      .filter(x => !/^blob:/i.test(x.url))
      .filter(x => allowedByDomain(x.url, allowDomains))
      .filter(x => /\.m3u8(\?|$)/i.test(x.url))         // pick stream playlists only
      .filter(x => !isNoisyLowLatency(x.url));          // avoid _HLS_part/_HLS_msn

    // Validate each shortlist entry (cap to avoid hammering)
    const maxValidate = Number(process.env.MAX_VALIDATE || "12");
    const toValidate = shortlist.slice(0, maxValidate);

    const validations = new Map();
    for (const item of toValidate) {
      const v = await validateM3U8(page, item.url);
      validations.set(item.url, v);
    }

    // Score and choose best
    const scored = shortlist.map(item => {
      const meta = { types: new Set(item.types) };
      const v = validations.get(item.url);
      return { ...item, validation: v || null, score: scoreUrl(item.url, meta, v) };
    }).sort((a, b) => b.score - a.score);

    const best = scored.find(x => x.validation?.ok) || null;

    console.log("\n=== SUMMARY ===");
    console.log(`Total candidates captured: ${all.length}`);
    console.log(`Shortlisted (.m3u8, stable, domain-allowed): ${shortlist.length}`);
    if (allowDomains.length) console.log(`Allowlist domains: ${allowDomains.join(", ")}`);

    if (best) {
      console.log("\nBEST STREAM URL:");
      console.log("  " + best.url);
      console.log("Score:", best.score);
      if (best.validation) console.log("Validation:", best.validation.why);
    } else {
      console.warn("\nNo BEST stream found (all shortlisted streams failed validation or shortlist is empty).");
    }

    // Dump sample URLs for quick testing (as requested)
    const sample = all
      .filter(x => allowedByDomain(x.url, allowDomains))
      .slice(0, dumpN)
      .map(x => x.url);

    fs.writeFileSync(path.join(outDir, "candidates_sample.txt"), sample.join("\n") + "\n");
    console.log(`\nWrote sample URLs (${sample.length}) to ${path.join(outDir, "candidates_sample.txt")}`);

    // Also dump “top picks” for convenience
    const topPicks = scored.slice(0, Math.min(10, scored.length))
      .map(x => `${x.score}\t${x.url}${x.validation ? `\t[${x.validation.ok ? "ok" : "bad"}]` : ""}`)
      .join("\n") + "\n";

    fs.writeFileSync(path.join(outDir, "top_picks.txt"), topPicks);
    console.log(`Wrote top picks to ${path.join(outDir, "top_picks.txt")}`);
  } catch (err) {
    console.error("Error:", err);
  } finally {
    await browser.close();
  }
}

main();
