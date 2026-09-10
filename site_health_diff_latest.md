# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 188` | `WARN 4` | `FAIL 2` | `ERROR 0` | `SKIP 3`
- Previous: `PASS 190` | `WARN 3` | `FAIL 2` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `0`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `2`
- Step regressions: `1`

## Persistent Failures

- **porn4k**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr solved challenge but got HTTP 304 from website
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **awmnet** `search`: `SKIP -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 404 from website
