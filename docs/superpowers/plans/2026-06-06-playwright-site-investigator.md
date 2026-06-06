# Playwright Site Investigator Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a `playwright-site-investigator` skill that routes developers to the right Playwright investigation tool with the right arguments when a site's test passes but Kodi playback is broken.

**Architecture:** A single `SKILL.md` file in `skills/playwright-site-investigator/` containing a three-branch decision tree. Branch 1 (test passes, playback broken) is the primary path with full detail; branches 2 and 3 are stubs. No code changes — this is a documentation skill only.

**Tech Stack:** Markdown, existing scripts `scripts/playwright_sniff.py` and `scripts/playwright_listing_probe.py`

---

### Task 1: Create the skill directory and SKILL.md

**Files:**
- Create: `skills/playwright-site-investigator/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p skills/playwright-site-investigator
```

Expected: directory created, no output.

- [ ] **Step 2: Write the skill file**

Create `skills/playwright-site-investigator/SKILL.md` with this exact content:

```markdown
---
name: playwright-site-investigator
description: Decision-tree workflow for Playwright-based site investigation. Use when a site's pytest test passes but Kodi playback is broken, a new site needs probing before a scraper is written, or a Cloudflare-blocked site needs investigation.
---

# Playwright Site Investigator

> **Playwright is a dev/debug tool only.** Never use it inside site modules — it is not available in the Kodi runtime. For site module fixes, use `kodi-site-maintenance` after this investigation is complete.

## Which branch are you in?

| Situation | Go to |
|-----------|-------|
| Test passes but Kodi playback is broken | [Branch 1](#branch-1-test-passes-playback-broken) |
| New site — no scraper exists yet | [Branch 2](#branch-2-new-site-no-scraper-yet) |
| Site blocks urllib/requests (Cloudflare/JS) | [Branch 3](#branch-3-cloudflare--js-rendered-site) |

---

## Branch 1: Test passes, playback broken

The scraper runs without error and your test still passes against saved fixtures — but the URL it returns no longer plays in Kodi. The site changed its stream delivery; you need to find the new URL pattern.

### Step 1 — Confirm the test still passes

```bash
.venv/bin/pytest tests/sites/test_<site>.py -v
```

Expected: all tests PASS. If tests are failing, stop — use `kodi-site-maintenance` instead.

### Step 2 — Sniff the live stream URL

Navigate to a video page on the site in your browser and copy a video URL. Then run:

```bash
python scripts/playwright_sniff.py <video-page-url>
```

Playwright will launch Chromium headlessly, navigate to the page, click any visible play button, and intercept all network responses. Lines prefixed with `[>>]` are stream candidates.

**Example output:**
```
[*] Starting Playwright sniffer for: https://example.com/videos/12345
[*] Navigating...
[*] Found play button (button.vjs-big-play-button), clicking...
[*] Waiting 10s for more network activity...
[>>] Found Video/Stream URL: https://cdn.example.com/hls/12345/master.m3u8
[*] Finished.
```

The `[>>]` lines are what the site actually serves. Compare these to what your scraper currently extracts.

### Step 3 — If sniff returns no `[>>]` lines

The stream URL was not captured via network interception. This usually means the player uses a blob URL, a DRM token, or renders the source only after a deeper interaction. Fall back to inspecting the rendered HTML:

```bash
python scripts/playwright_listing_probe.py --url <video-page-url> --selector "video,source,[data-src],[data-video-url]"
```

This dumps a count and summary of matched elements. Look for `src`, `data-src`, or `data-video-url` attributes on `<video>` or `<source>` tags in the output.

If neither tool returns a usable URL, the site likely requires a signed token or API call — check the browser's Network tab manually (DevTools → Network → filter by `.m3u8` or `.mp4`).

### Step 4 — Identify the delta

Compare the URL `playwright_sniff.py` found with what the current scraper extracts. Common causes of breakage:

| Symptom | Likely cause |
|---------|-------------|
| Scraper returns a page URL, not a stream | Domain change — site moved video hosting to a new CDN |
| Scraper returns a URL that 404s | API endpoint version bumped (e.g. `/api/v2/` → `/api/v3/`) |
| Scraper returns a URL but Kodi says "invalid" | Token or hash parameter added to stream URL |
| Scraper returns nothing | New iframe redirect layer wrapping the player |

### Step 5 — Hand off

You now know what URL the site serves. To update the scraper to extract it, use the `kodi-site-maintenance` skill.

---

## Branch 2: New site, no scraper yet

Use `playwright_listing_probe.py` to inspect the listing structure before writing any scraper code. Pass the main listing URL and adjust `--selector` to match the card container:

```bash
python scripts/playwright_listing_probe.py --url <listing-url> --selector ".video-item,.thumb,.item"
```

For the full new-site workflow (creating the scraper, registering it, writing tests), use `kodi-site-maintenance`.

---

## Branch 3: Cloudflare / JS-rendered site

If `utils.getHtml` returns a Cloudflare challenge page or empty content, confirm Playwright can get through:

```bash
python scripts/playwright_sniff.py <site-listing-url>
```

If Playwright succeeds (returns page content or stream URLs), the site requires `flaresolverr` or Playwright-based fetching in the scraper. For setup and integration details, use `kodi-site-maintenance`.
```

- [ ] **Step 3: Verify the file was written correctly**

```bash
head -5 skills/playwright-site-investigator/SKILL.md
```

Expected output:
```
---
name: playwright-site-investigator
description: Decision-tree workflow for Playwright-based site investigation. Use when a site's pytest test passes but Kodi playback is broken, a new site needs probing before a scraper is written, or a Cloudflare-blocked site needs investigation.
---
```

- [ ] **Step 4: Commit**

```bash
git add skills/playwright-site-investigator/SKILL.md docs/superpowers/specs/2026-06-06-playwright-site-investigator-design.md docs/superpowers/plans/2026-06-06-playwright-site-investigator.md
git commit -m "feat: add playwright-site-investigator skill"
```

Expected: commit created on master branch.

---

### Task 2: Verify skill is discoverable

- [ ] **Step 1: Reload skills and confirm it appears**

In Claude Code, run `/reload-skills` and check that `playwright-site-investigator` appears in the skill list.

Expected: skill listed with name `playwright-site-investigator` and description matching the frontmatter.

- [ ] **Step 2: Confirm no other skills were broken**

Run `/skills` and verify all previously listed skills still appear (upstream-sync, kodi-addon-dev, kodi-site-maintenance, kodi-test-patterns, bs4-migration-toolkit, kodi-repo-manager).
