# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 185` | `WARN 2` | `FAIL 2` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 185` | `WARN 2` | `FAIL 2` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `1`
- Site regressions: `2`
- Step regressions: `3`

## New Failures

- **hentaidude**: `WARN -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Resolved Failures

- **analdin**: `FAIL -> PASS`

## Persistent Failures

- **xtheatre**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://pornxtheatre.com/?filter=latest&filter=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **awmnet** `search`: `SKIP -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 404 from website
- **hentaidude** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtheatre** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://pornxtheatre.com/?filter=latest&filter=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
