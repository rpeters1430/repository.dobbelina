# Site Tooling Guide

Use `scripts/site_tool.py` as the starting point for site maintenance. It wraps
the existing scripts without removing their old paths, so CI and older notes can
keep using the specialized files directly.

## Start Here

```powershell
python scripts/site_tool.py --workflows
python scripts/site_tool.py --list
```

## Common Tasks

| Task | Recommended command |
| --- | --- |
| Add or evaluate a new site | `python scripts/site_tool.py candidates-rank` then `python scripts/site_tool.py candidates-validate --limit 10` |
| Inspect a JavaScript-heavy site | `python scripts/site_tool.py playwright-inspect <url> --sniff` |
| Probe a listing page with Playwright | `python scripts/site_tool.py playwright-listing --url <listing-url>` |
| Run generated pytest smoke tests | `python scripts/site_tool.py smoke-unit --site <site>` |
| Run live Kodi-style smoke test | `python scripts/site_tool.py smoke-live --site <site> --steps main,list,categories,search,play` |
| Generate smoke test files | `python scripts/site_tool.py smoke-generate --site <site>` |
| List implemented sites | `python scripts/site_tool.py sites-list` |
| Refresh status metrics | `python scripts/site_tool.py sites-status` |
| Validate logos | `python scripts/site_tool.py logos-validate` |
| Dry-run logo fixes | `python scripts/site_tool.py logos-fix --dry-run` |

## Which Script Should I Use?

Use these canonical entry points first:

- `scripts/site_tool.py`: human-facing dispatcher for common maintenance tasks.
- `scripts/live_smoke_test.py`: live site behavior through Kodi-style stubs.
- `scripts/run_smoke_tests.py`: generated pytest smoke files.
- `scripts/generate_smoke_tests.py`: smoke test generator.
- `scripts/rank_new_sites.py`: new site candidate ranking.
- `scripts/validate_candidate_sites.py`: live validation for ranked candidates.
- `scripts/codegen.py`: headed Playwright browser with ad blocking and optional stream sniffing.
- `scripts/playwright_listing_probe.py`: targeted listing-card inspection.
- `list_implemented_sites.py`: implemented site inventory.
- `validate_logos.py` and `fix_all_logos.py`: logo validation and repair.

For the full inventory of every script in `scripts/` and the repo root — what
it does, whether CI depends on it, and when to reach for it — see
[`scripts/README.md`](../../scripts/README.md).

## Monthly Full-Repo Review

`scripts/live_smoke_test.py` already simulates the whole Kodi user journey for
every site in-process (via Kodi stubs, no real Kodi install needed): it opens
`Main`, follows into `List` (hopping up to 3 "next page" navigations),
opens `Categories`, runs `Search`, and resolves a `Playvid` URL — the same
five things you'd check by hand once a month. Run it against every site with:

```powershell
python scripts/live_smoke_test.py --out results
```

With no `--site` given it discovers and runs all ~190 site modules
sequentially, so budget real time for it (each site gets up to 140s before
being force-timed-out; a full run is commonly 30-90 minutes depending on how
many sites are slow/unreachable). Start it and let it run in the background;
it's read-only against the live sites.

Notes:
- Install/enable FlareSolverr first (`FLARESOLVERR_URL` env var, defaults to
  `http://localhost:8191/v1`) so Cloudflare-protected sites get a fair shot —
  without it, those sites SKIP instead of FAIL.
- Output is written to `results/live_smoke_<timestamp>.{json,md}`. Read the
  `.md` file first — it has a per-site PASS/WARN/FAIL/SKIP table across all
  five steps, a `## Failures` section with the actual error per failing step,
  a `## Failure Classification Summary` that separates real bugs from harness
  noise (blocked/webcam/network issues you can ignore), and a
  `## Missing Thumbnails` section flagging sites where videos were found but
  none had an image.
- To recheck a handful of sites you already suspect are broken:
  `python scripts/site_tool.py smoke-live --site <name> --steps main,list,categories,search,play`.
- `strict_site_monitor.py` (run daily by CI) checks a stricter subset of
  "priority" sites against machine-checkable contracts — useful for
  comparison, but `live_smoke_test.py` with no `--site` filter is the one
  that covers every site for a full manual review.

## New Site Workflow

1. Rank likely candidates:
   ```powershell
   python scripts/site_tool.py candidates-rank
   ```
2. Live-check the best candidates:
   ```powershell
   python scripts/site_tool.py candidates-validate --limit 10
   ```
3. Inspect selectors and media requests when plain HTTP is not enough:
   ```powershell
   python scripts/site_tool.py playwright-inspect https://example.com --sniff
   ```
4. Add the site module under `plugin.video.cumination/resources/lib/sites/`.
5. Add focused tests under `tests/sites/`.
6. Run narrow tests and live smoke:
   ```powershell
   python -m pytest tests/sites/test_<site>.py
   python scripts/site_tool.py smoke-live --site <site> --steps main,list,categories,search,play
   ```

## Cleanup Rule

Do not add new top-level one-off scripts for normal site work. Add reusable
workflow commands to `scripts/site_tool.py` instead. If you need a throwaway
investigation script, delete it once the investigation is done (or fold the
useful part into an existing script/test) rather than leaving it in the repo —
`scripts/audit_debug/` and `scripts/debug/` used to hold ~190 of these and were
removed in the August 2026 cleanup.
