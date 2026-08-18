# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 181` | `WARN 2` | `FAIL 3` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 178` | `WARN 3` | `FAIL 3` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `2`
- Site regressions: `3`
- Step regressions: `2`

## New Failures

- **pornez**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://pornezoo.net: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Resolved Failures

- **analdin**: `FAIL -> PASS`

## Persistent Failures

- **hypnotube**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **pornez** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://pornezoo.net: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **pornslash** `play`: `PASS -> FAIL` (CODE) | ValueError: No video stream found!

## Improvements

- **awmnet**: `WARN -> PASS`
- **javguru**: `WARN -> PASS`
