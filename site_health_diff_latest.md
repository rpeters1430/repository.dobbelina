# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 178` | `WARN 2` | `FAIL 2` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 178` | `WARN 3` | `FAIL 1` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **myporntape**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://myporntape.com/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **myporntape** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://myporntape.com/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Improvements

- **ikisoda**: `WARN -> PASS`
