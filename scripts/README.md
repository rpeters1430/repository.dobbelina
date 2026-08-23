# Scripts Index

Every standalone script in this repo lives either at the repo root (logo
pipeline + build/test entry points) or in `scripts/` (everything else). This
file is the map: what each one does, whether CI depends on it, and where to
start for a given task. If you're not sure which script to reach for, start
here before writing a new one.

For the day-to-day "how do I add/check a site" workflow, see
[`docs/development/SITE_TOOLING.md`](../docs/development/SITE_TOOLING.md) —
`scripts/site_tool.py` wraps most of the site-dev scripts below into one
dispatcher.

## Repo root

| Script | Purpose |
| --- | --- |
| `run_tests.py` | Cross-platform pytest runner. Use this over raw `pytest` for the full suite. |
| `build_repo_addons.py` | Builds addon ZIPs and (with `--update-index`) regenerates `addons.xml`/`addons.xml.md5`. Used by CI (`build-addons.yml`). |
| `setup.sh` / `setup_unified.sh` | One-shot environment setup (system deps + venv). |
| `six.py` | Vendored `six` stub. The repo root is on `sys.path` ahead of site-packages, so `import six` in `basics.py` resolves here — do not delete. |

### Logo pipeline

Documented in full in
[`docs/logos/LOGO_SCRIPTS_README.md`](../docs/logos/LOGO_SCRIPTS_README.md).
Run in this order when standardizing logos:

| Script | Purpose |
| --- | --- |
| `analyze_logos.py` | Assessment/report: formats, sizes, missing/orphaned logos. |
| `get_logo_dimensions.py` | Dimension inspection without needing PIL. |
| `process_logos.py` | Main processing tool — download, convert, resize to 256x256 PNG. |
| `update_site_modules.py` | Rewrites site modules to reference local logo files instead of remote URLs. |
| `validate_logos.py` | Pass/fail validation against the logo standards. |
| `fix_all_logos.py` | Batch repair for logos failing validation. |
| `list_implemented_sites.py` | Inventory of implemented site modules (also wrapped by `site_tool.py sites-list`). |

## `scripts/`

### Site development (start with `site_tool.py`)

| Script | Purpose |
| --- | --- |
| `site_tool.py` | Human-facing dispatcher — run `python scripts/site_tool.py --list` to see every subcommand it wraps. Prefer this over calling the scripts below directly. |
| `codegen.py` | Headed Playwright browser with ad-blocking + optional stream sniffing, for scaffolding a new site module. Dev/debug only — never used at runtime. |
| `playwright_listing_probe.py` | Targeted inspection of a listing page's video cards via Playwright. |
| `playwright_sniff.py` | Playwright-based network sniffing for Cloudflare-protected sites. |
| `playwright_sniff_bridge.py` | Bridges a Node-side sniff script into Python; invoked by the `/pw-sniff` Gemini CLI extension. |
| `playwright_smoke_runner.py` | Runs a live smoke pass through a headed/headless browser; invoked by the `/pw-smoke` Gemini CLI extension. |
| `playwright_test_env.py` | Verifies the local Playwright/browser install; invoked by the `/pw-test-env` Gemini CLI extension. |
| `sniff_stripchat.py` | Stripchat-specific stream/API probing. |
| `rank_new_sites.py` | Ranks new-site candidates (used by `track_and_test_new_sites.py` and `site_tool.py candidates-rank`). |
| `validate_candidate_sites.py` | Live HTTP validation for ranked candidates (`site_tool.py candidates-validate`). |
| `track_and_test_new_sites.py` | Pulls candidate sites from Fluffle, cross-references against implemented/tracked sites, and test-probes the new ones. |
| `analyze_sites.py` | Static analysis across all site modules — entry points, BS4 vs regex, webcam vs tube, etc. Emits JSON used by other tooling. |
| `check_site_status.py` | Combines `analyze_sites.py` output with test results to report what's broken in one specific site. |

### Smoke testing / CI health checks

| Script | Purpose |
| --- | --- |
| `generate_smoke_tests.py` | Regenerates `tests/smoke_generated/` from the current site inventory. |
| `run_smoke_tests.py` | Runs the generated pytest smoke tests. |
| `smoke_check.py` | Quick wrapper: runs smoke tests and prints an actionable pass/fail summary. |
| `live_smoke_test.py` | Live-fetches real sites through Kodi-style stubs. Used directly by CI (`site-health.yml`). |
| `generate_smoke_matrix.py` | Emits the GitHub Actions job matrix for `site-health.yml`. |
| `merge_smoke_reports.py` | Merges per-shard `live_smoke_test.py` JSON output into one report. Used by CI. |
| `smoke_report_diff.py` | Diffs two smoke result files to spot regressions. Used by CI. |
| `strict_site_monitor.py` | Runs the strict (contract-based) per-site health check. Used by CI. |
| `strict_health_history.py` | Appends strict monitor results to the rolling health history. Used by CI. |
| `generate_strict_triage_requests.py` | Turns strict health history into GitHub triage request actions. Used by CI. |
| `generate_triage_requests.py` | Older/simpler triage-request generator from health regressions (has its own test: `tests/test_generate_triage_requests.py`). |
| `automate_triage.py` | Applies generated triage requests (labels/issues) via the GitHub API. Used by CI. |
| `ensure_labels.py` | Ensures the GitHub labels used by triage automation exist. Used by CI. |
| `site_health_types.py` | Shared dataclasses/enums (`ValidationResult`, `HealthState`, URL redaction) used by the validator and monitoring scripts below. Not a standalone script. |
| `listing_validator.py` | Validates a fetched listing page against health contracts (Cloudflare challenge detection, structure checks, etc.). |
| `media_validator.py` | Validates that a resolved playback URL actually serves media (not an HTML error page). |

### Kodi runtime probing

Built for the priority-site-monitoring feature
(`docs/superpowers/plans/2026-07-29-priority-site-monitoring.md`); each has a
matching test under `tests/`.

| Script | Purpose |
| --- | --- |
| `kodi_jsonrpc.py` | Transport-only Kodi JSON-RPC client. |
| `kodi_site_probe.py` | Drives a real Kodi instance over JSON-RPC to probe a site end-to-end. |
| `merge_kodi_results.py` | Merges Kodi runtime probe results into the strict site monitoring reports. |

### Release / upstream maintenance

| Script | Purpose |
| --- | --- |
| `auto_bump_versions.py` | Auto-bumps `addon.xml` versions. Used by CI (`build-addons.yml`). |
| `update_changelog.py` | Updates changelog entries alongside a version bump. Used by CI. |
| `generate_status_metrics.py` | Recomputes `docs/status/STATUS_METRICS.md`. |
| `sync_manager.py` | The upstream commit triage tool — see the "Upstream Commit Triage" section in the root `CLAUDE.md`. |
| `update_venv.py` | Upgrades `.venv` to the latest allowed versions in `requirements-test.txt`. Run manually, not from CI. |

## What's not here anymore

`scripts/audit_debug/` (178 files) and `scripts/debug/` (8 files) were one-off
per-site debug harnesses from early BeautifulSoup-migration work, unreferenced
by anything else in the repo. They — along with ~35 similar one-off
`analyze_*`/`check_*`/`compare_*`/`repro_*`/`sniff_*`/`test_*` scripts at the
root and in `scripts/`, two stray backup site-module copies, a vendored JS
bundle, and duplicate Playwright/CI config files — were deleted in the August
2026 cleanup. All of it is still recoverable from git history if needed; none
of it was referenced by CI, docs, or other code.

If you write a throwaway investigation script for a specific site issue,
delete it once you're done rather than leaving it in the repo — that's how
this pile built up the first time.
