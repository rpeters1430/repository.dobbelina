# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 179` | `WARN 0` | `FAIL 3` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 178` | `WARN 0` | `FAIL 3` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `0`
- Persistent failures: `3`
- Site regressions: `0`
- Step regressions: `0`

## Persistent Failures

- **analdin**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **pornez**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://pornezoo.net: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Improvements

- **motherless**: `SKIP -> PASS`
