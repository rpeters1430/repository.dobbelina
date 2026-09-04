# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 187` | `WARN 3` | `FAIL 1` | `ERROR 0` | `SKIP 3`
- Previous: `PASS 188` | `WARN 3` | `FAIL 1` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `0`
- Site regressions: `3`
- Step regressions: `2`

## New Failures

- **jizzbunker**: `PASS -> FAIL` (UNKNOWN) | list: List URL unavailable in harness (HTTP 500)

## Resolved Failures

- **pornmz**: `FAIL -> PASS`

## Step Regressions

- **jizzbunker** `list`: `PASS -> FAIL` (UNKNOWN) | List URL unavailable in harness (HTTP 500)
- **xtapesla** `play`: `SKIP -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://xtapes.la/videos/ramming-into-her-2026-full-movie/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Improvements

- **awmnet**: `WARN -> PASS`
