# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 179` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 181` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `2`
- Step regressions: `1`

## Persistent Failures

- **pornez**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://pornezoo.net: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **yrprno** `play`: `PASS -> FAIL` (NETWORK) | TimeoutError: The read operation timed out
