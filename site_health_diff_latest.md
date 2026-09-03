# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 188` | `WARN 3` | `FAIL 1` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 187` | `WARN 2` | `FAIL 3` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `1`
- Resolved failures: `3`
- Persistent failures: `0`
- Site regressions: `2`
- Step regressions: `2`

## New Failures

- **pornmz**: `PASS -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://pornmz.com/page/1?filter=popular: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Resolved Failures

- **analdin**: `FAIL -> PASS`
- **javseen**: `FAIL -> PASS`
- **xtapesla**: `FAIL -> PASS`

## Step Regressions

- **awmnet** `search`: `SKIP -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 404 from website
- **pornmz** `list`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://pornmz.com/page/1?filter=popular: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
