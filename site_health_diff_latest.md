# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 172` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 172` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `1`
- Site regressions: `2`
- Step regressions: `2`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos ⚠️ [FLAKY: 50.0%]

## Resolved Failures

- **hanime**: `FAIL -> PASS`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 40.0%]

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **tokyomotion** `play`: `PASS -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)

## Improvements

- **perverzija**: `WARN -> PASS`
