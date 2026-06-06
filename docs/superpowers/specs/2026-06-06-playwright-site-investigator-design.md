# Playwright Site Investigator Skill — Design

**Date:** 2026-06-06
**Status:** Approved

## Problem

The project has six existing skills covering addon dev, site maintenance, test patterns, BS4 migration, repo management, and upstream sync. There is no skill for Playwright-based site investigation.

The primary pain point: a site's pytest test passes (fixtures still match) but Kodi playback is broken. The developer needs to figure out which investigation tool to run and with what arguments — not how to fix the scraper afterward.

## Skill Identity

- **Name:** `playwright-site-investigator`
- **File:** `skills/playwright-site-investigator/SKILL.md`
- **Trigger:** Use when a site's test passes but Kodi playback is broken and the stream URL needs to be re-identified.

## Structure

Decision-tree dispatcher with three branches:

| Branch | Trigger | Primary tool |
|--------|---------|--------------|
| 1 (primary) | Test passes, playback broken | `playwright_sniff.py` → `playwright_listing_probe.py` |
| 2 (stub) | New site, no scraper yet | `playwright_listing_probe.py` + `codegen.py` |
| 3 (stub) | Cloudflare/JS-blocked site | `playwright_sniff.py` with Cloudflare notes |

Branches 2 and 3 are intentionally short stubs — they route to the right tool and defer to `kodi-site-maintenance` for the full workflow.

## Branch 1 — Detailed Flow

1. **Confirm test still passes** — `pytest tests/sites/test_<site>.py -v`
2. **Sniff live stream** — `python scripts/playwright_sniff.py <video-page-url>`
   - Intercepts network requests, filters for stream indicators (`.m3u8`, `.mp4`, `/manifest`, known CDNs)
3. **Fallback if sniff returns nothing** — `python scripts/playwright_listing_probe.py <video-page-url>`
   - Dumps full rendered HTML for manual player embed inspection
4. **Identify the delta** — compare sniff output to what the scraper currently extracts
   - Common causes: domain change, new API endpoint, token/hash added to URL, iframe redirect layer added
5. **Hand off** — skill ends here; fixing the scraper is `kodi-site-maintenance`

## Scope Boundaries

- Does NOT cover how to update the scraper (→ `kodi-site-maintenance`)
- Does NOT cover writing new test fixtures (→ `kodi-test-patterns`)
- Does NOT cover full Cloudflare bypass setup (→ `kodi-site-maintenance`)
- Playwright must never be used in site modules — skill reinforces this constraint

## Success Criteria

After following the skill, the developer knows:
- Which URL the site now serves the stream from
- Why the current scraper is returning the wrong URL
- Which script produced the answer and how to re-run it
