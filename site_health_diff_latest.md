# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 177` | `WARN 2` | `FAIL 4` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 180` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `2`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `3`
- Step regressions: `3`

## New Failures

- **analdin**: `PASS -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **pornez**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://pornezoo.net: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Persistent Failures

- **hypnotube**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (NETWORK) | List URL unavailable in harness (HTTP 503)
- **awmnet** `search`: `SKIP -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 404 from website
- **pornez** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://pornezoo.net: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
