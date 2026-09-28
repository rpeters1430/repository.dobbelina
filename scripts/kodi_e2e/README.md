# Kodi E2E — test Cumination the way users use it

Runs the addon inside a **real, headless Kodi** and walks every site like a
person with a remote would, then reports what's broken. Nothing is mocked:
Kodi runs the plugin, Kodi's texture loader fetches the thumbnails, Kodi's
player plays the video.

For each site it:

1. opens **Cumination → Sites → the site** (sites that fail to import and
   silently vanish from the list are reported too);
2. checks the video list: empty lists, nameless folders, junk in titles
   (`&amp;`, HTML tags, durations/ids/view counts, `@handles`, URL slugs,
   duplicates), too few items, a full page with **no Next Page**;
3. loads a sample of **thumbnails through Kodi** (`/image/` endpoint, same
   path the skin uses, `|Referer=` pipes included): dead, missing,
   placeholder (every item the same picture) and tiny/low-res images;
4. follows **Next Page** once (empty? same items again?);
5. **plays a video** until the playhead actually moves; if it fails, tries a
   second one so "one bad video" is told apart from "playback broken", and
   records why (the addon's own popup text, Kodi error dialogs, Python
   tracebacks, HTTP errors, resolution);
6. opens a **category** folder and two entries in it;
7. runs a **search** the way `utils.oneSearch` does after the user types.

While any of this runs, a watcher answers dialogs like a user: picks the
first source in a select dialog, types the search term into the keyboard,
dismisses confirmations — and records every popup the user would have seen.

Each site ends up **fail** (a feature is broken), **warn** (works but looks
wrong) or **pass**, with a *likely cause* when the network is the problem
(unreachable, Cloudflare → needs FlareSolverr, 403/5xx, page gone).

## Run it

Linux (Ubuntu/Debian; any distro with Kodi + Xvfb works):

```bash
bash scripts/kodi_e2e/install_kodi.sh            # your distro's Kodi (Debian 13: 21, Ubuntu 24.04: 20.5)
pip install Pillow

python -m scripts.kodi_e2e selftest              # ~1 min, local fake sites: proves the harness works
python -m scripts.kodi_e2e crawl                 # every site
python -m scripts.kodi_e2e crawl --site pornhub,xvideos --deep
python -m scripts.kodi_e2e crawl --workers 4 --flaresolverr http://127.0.0.1:8191/v1
```

Open `results/kodi_e2e/report.html`. Each run keeps the previous
`summary.json` and reports what **newly broke** or **got fixed**.

Want to watch it drive Kodi? On a desktop, add `--no-xvfb`.

### Docker (home server / NAS)

```bash
docker compose -f scripts/kodi_e2e/docker/compose.yml run --rm kodi-e2e
docker compose -f scripts/kodi_e2e/docker/compose.yml run --rm kodi-e2e \
    crawl --site spankbang --flaresolverr http://flaresolverr:8191/v1
```

The repo is mounted into the container, so it always tests your working tree.
Add it to cron for a nightly run on your own IP (some sites geo-block or
rate-limit GitHub's runners).

### GitHub Actions (`.github/workflows/kodi-e2e.yml`)

- **Pull requests** touching the addon: unit tests + the self-test in real
  Kodi against local fake sites. Deterministic: no live sites involved (it
  only needs GitHub to fetch Kodi's script modules, cached after the first
  run).
- **Nightly / manual**: the live crawl, sharded across jobs, with FlareSolverr.
  The Markdown summary is on the run page; `kodi-e2e-report` has the HTML.
  Manual runs can pick sites, `deep`, shard count and Kodi build.

## Options worth knowing

| flag | |
|---|---|
| `--site a,b` / `--skip a,b` | limit the run |
| `--deep` | also play from a category and from search results |
| `--workers N` | N Kodi instances in parallel (own profile + port each) |
| `--source zip` | install from release ZIPs built by `build_repo_addons.py` (what users get) instead of the working tree |
| `--search-term` | default `blonde` |
| `--thumbs N` | thumbnails loaded per list (default 8) |
| `--site-budget S` | max seconds per site (default 420) |
| `--baseline file` | diff against a specific `summary.json` |
| `--fail-on-regression` | exit 1 when a site newly breaks |

Per-site behaviour comes from `config/site_profiles.json` (shared with the
Site Health checks): `supports.play/search/categories: false`,
`harness.playback_not_testable`, `harness.search_results_optional`,
`harness.categories_optional`, and `harness.search_term` for sites where the
default term finds nothing.

## Findings

| area | codes |
|---|---|
| listing | `LISTING_ERROR` `LISTING_EMPTY` `NO_VIDEOS` `FEW_VIDEOS` `BLANK_FOLDERS` `DUPLICATE_ITEMS` `BLOCKED_PAGE` |
| titles | `BLANK_TITLES` `TITLE_HTML_ENTITIES` `TITLE_HTML_TAGS` `TITLE_NUMBER_NOISE` `TITLE_HANDLE` `TITLE_SLUG` `TITLE_WHITESPACE` `TITLE_TOO_LONG` `TITLE_MOSTLY_DIGITS` `DUPLICATE_TITLES` |
| images | `THUMBS_MISSING` `THUMBS_SOME_MISSING` `THUMBS_BROKEN` `THUMBS_SOME_BROKEN` `THUMBS_PLACEHOLDER` `THUMBS_LOW_RES` |
| pagination | `NO_NEXT_PAGE` `NEXT_PAGE_ERROR` `NEXT_PAGE_EMPTY` `NEXT_PAGE_SAME` |
| playback | `PLAYBACK_FAILED` `PLAYBACK_FLAKY` `NOTHING_TO_PLAY` `LOW_QUALITY_STREAM` |
| categories / search | `CATEGORY_BROKEN` `CATEGORY_EMPTY` `SEARCH_BROKEN` `SEARCH_EMPTY` |
| errors | `PYTHON_EXCEPTION` `SITE_IMPORT_ERROR` `KODI_CRASHED` `UNEXPECTED_DIALOG` |

Title checks only fire when a pattern is systematic (a parser problem), not
for one odd title. Site JSON files also carry `passed / item_count /
playback_started / message`, so `scripts/merge_kodi_results.py` accepts them.

## How it fits together

```
profile.py   throwaway Kodi home: addon (+resolveurl) from the tree or ZIPs, deps
             resolved from xbmc/repo-scripts on GitHub, web server on, age gate
             and changelog pre-accepted, FlareSolverr wired in
runner.py    Kodi under Xvfb, JSON-RPC readiness, enables addons, per-step kodi.log
driver.py    user actions over JSON-RPC + dialog watcher + image/playback probes
logparse.py  kodi.log → tracebacks, addon notifications, HTTP errors, player errors
checks.py    pure heuristics → findings (unit tested in tests/test_kodi_e2e.py)
crawler.py   the per-site walk
report.py    summary.json, report.md, report.html, baseline diff
selftest/    two local fake sites (one healthy, one with every defect planted)
```

`utils.notify()` now also writes the toast text to `kodi.log` (Kodi doesn't
log notifications). That's how the harness knows *why* something failed,
and it helps with user-submitted logs too.

## Limits

- Live sites change hourly; treat one failure as a lead and a failure that
  persists across nightly runs as a bug. The baseline diff helps with that.
- It judges what Kodi reports (items, images, player state), not what a
  frame looks like. A stream of the wrong video would still "play".
- Kodi version matters: GitHub runners (Ubuntu 24.04) test Kodi 20.5; the
  Docker image (Debian 13) tests Kodi 21. The team-xbmc PPA has no build for
  Ubuntu 24.04, so `install_kodi.sh ppa` falls back to the distro's Kodi.
