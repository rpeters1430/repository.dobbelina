# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 179` | `WARN 2` | `FAIL 2` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 177` | `WARN 2` | `FAIL 4` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `2`
- Persistent failures: `2`
- Site regressions: `1`
- Step regressions: `2`

## Resolved Failures

- **analdin**: `FAIL -> PASS`
- **pornez**: `FAIL -> PASS`

## Persistent Failures

- **hypnotube**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **cumlouder** `play`: `PASS -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **pornhoarder** `search`: `SKIP -> FAIL` (BLOCKED) | HTTPError: HTTP Error 403: Forbidden

## Improvements

- **awmnet**: `WARN -> PASS`
