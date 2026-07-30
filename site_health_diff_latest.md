# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 176` | `WARN 2` | `FAIL 2` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 177` | `WARN 1` | `FAIL 3` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `1`
- Resolved failures: `2`
- Persistent failures: `1`
- Site regressions: `2`
- Step regressions: `2`

## New Failures

- **freepornvideos**: `PASS -> FAIL` (NETWORK) | main: TimeoutError: The read operation timed out

## Resolved Failures

- **motherless**: `FAIL -> SKIP`
- **thothub**: `FAIL -> PASS`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **cumlouder** `play`: `PASS -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **freepornvideos** `main`: `PASS -> FAIL` (NETWORK) | TimeoutError: The read operation timed out
