# Project Status Report

## Last validated
- **Timestamp (UTC):** 2026-04-23T18:19:04Z
- **Canonical sources:**
  - `plugin.video.cumination/addon.xml`
  - `plugin.video.cumination/changelog.txt`
  - `plugin.video.cumination/resources/lib/sites/`
  - `tests/`

## Current release baseline

- **Addon ID:** `plugin.video.cumination`
- **Current version:** **1.1.373**
- **Latest changelog section:** **Version 1.1.373**
- **Status date for this report:** **2026-04-23**

## Unified project metrics (source-of-truth snapshot)

| Metric | Value |
|---|---:|
| Site inventory Python files (`resources/lib/sites/*.py`) | 172 |
| Site modules (excluding `__init__.py`, `soup_spec.py`) | 170 |
| API-first site modules (from current roadmap classification) | 6 |
| Non-API site modules | 164 |
| Total files under `tests/` | 714 |
| Python files under `tests/` | 395 |
| Site test files (`tests/sites/test_*.py`) | 181 |
| Generated smoke files (`tests/smoke_generated/test_smoke_*.py`) | 169 |
| Fixture files (`tests/fixtures/**`) | 319 |
| Site modules with direct `tests/sites/test_<site>.py` | 169 / 170 |
| Site modules with generated smoke test file | 169 / 170 |

## Notable inventory gaps

- Missing direct site test file for: `hentai-moon`.
- Missing generated smoke test file for: `sunporno`.

## Notes

This document is intentionally aligned with:
- `docs/development/MODERNIZATION.md`
- `docs/testing/TESTING_STATUS.md`
- `docs/audit/COMPREHENSIVE_AUDIT_SUMMARY.md`

All four documents should carry the same version/date/metrics block above unless a newer validation run is performed.
