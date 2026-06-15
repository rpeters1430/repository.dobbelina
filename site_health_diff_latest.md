# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 177` | `WARN 1` | `FAIL 1` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 175` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `0`
- Resolved failures: `1`
- Persistent failures: `1`
- Site regressions: `1`
- Step regressions: `1`

## Resolved Failures

- **analdin**: `FAIL -> PASS`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **cumlouder** `play`: `PASS -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)

## Improvements

- **noodlemagazine**: `WARN -> PASS`
