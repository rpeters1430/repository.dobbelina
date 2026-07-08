# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 177` | `WARN 2` | `FAIL 2` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 180` | `WARN 0` | `FAIL 1` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `3`
- Step regressions: `2`

## New Failures

- **supjav**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **cumlouder** `play`: `PASS -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **hanime** `play`: `SKIP -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://hanime.tv/api/v8/video?id=https://hanime.tv/nuki-nuki-zupposism-1: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
