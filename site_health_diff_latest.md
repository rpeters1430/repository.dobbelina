# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 178` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 179` | `WARN 0` | `FAIL 1` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `2`
- Step regressions: `2`

## New Failures

- **motherless**: `SKIP -> FAIL` (UNKNOWN) | list: List URL unavailable in harness (HTTP 502) ⚠️ [FLAKY: 60.0%]

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **beemtube** `play`: `PASS -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **motherless** `list`: `SKIP -> FAIL` (UNKNOWN) | List URL unavailable in harness (HTTP 502)
