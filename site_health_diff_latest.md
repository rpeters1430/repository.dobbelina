# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 188` | `WARN 5` | `FAIL 2` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 188` | `WARN 4` | `FAIL 2` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `0`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `2`
- Step regressions: `2`

## Persistent Failures

- **porn4k**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr solved challenge but got HTTP 304 from website
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **celebsroulette** `search`: `SKIP -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 404 from website
- **xtapesla** `play`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://xtapes.la/videos/massage-parlor-5-2026-full-movie/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Improvements

- **awmnet**: `WARN -> PASS`
- **porndish**: `SKIP -> PASS`
