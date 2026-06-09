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

Treat these as support/debug scripts unless a specific investigation needs them:

- `scripts/audit_debug/debug_*.py`
- `scripts/debug/debug_*.py`
- one-off root files named `check_*`, `compare_*`, `repro_*`, or `test_*`

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
workflow commands to `scripts/site_tool.py`, or put temporary investigations
under `scripts/debug/` or `scripts/audit_debug/`.
