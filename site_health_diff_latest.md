# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 190` | `WARN 3` | `FAIL 2` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 191` | `WARN 3` | `FAIL 1` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `1`
- Step regressions: `2`

## New Failures

- **porn4k**: `PASS -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr solved challenge but got HTTP 304 from website

## Persistent Failures

- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **porn4k** `main`: `PASS -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 304 from website
- **porn4k** `search`: `SKIP -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 404 from website
