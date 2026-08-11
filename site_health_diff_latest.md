# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 180` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 176` | `WARN 2` | `FAIL 4` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `0`
- Resolved failures: `2`
- Persistent failures: `2`
- Site regressions: `0`
- Step regressions: `0`

## Resolved Failures

- **fpoxxx**: `FAIL -> PASS`
- **myporntape**: `FAIL -> PASS`

## Persistent Failures

- **hypnotube**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Improvements

- **awmnet**: `WARN -> PASS`
- **spankbang**: `SKIP -> PASS`
