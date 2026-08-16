# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 180` | `WARN 1` | `FAIL 3` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 179` | `WARN 2` | `FAIL 2` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `1`
- Step regressions: `2`

## New Failures

- **pornez**: `PASS -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://pornezoo.net/page/2/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Persistent Failures

- **hypnotube**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **pornez** `list`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://pornezoo.net/page/2/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **pornhoarder** `search`: `SKIP -> FAIL` (BLOCKED) | HTTPError: HTTP Error 403: Forbidden

## Improvements

- **awmnet**: `WARN -> PASS`
