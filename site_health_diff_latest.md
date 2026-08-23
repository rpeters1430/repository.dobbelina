# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 186` | `WARN 3` | `FAIL 1` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 185` | `WARN 2` | `FAIL 2` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `1`
- Persistent failures: `1`
- Site regressions: `1`
- Step regressions: `1`

## Resolved Failures

- **xtapesla**: `FAIL -> PASS`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **porndoe** `play`: `SKIP -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://porndoe.com/watch/pd1t0r9o8u4w: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
