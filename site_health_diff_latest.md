# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 176` | `WARN 2` | `FAIL 4` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 178` | `WARN 2` | `FAIL 2` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `2`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `2`
- Step regressions: `2`

## New Failures

- **fpoxxx**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **hypnotube**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Persistent Failures

- **myporntape**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://myporntape.com/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **fpoxxx** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **hypnotube** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
