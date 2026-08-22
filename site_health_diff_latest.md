# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 185` | `WARN 2` | `FAIL 2` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 183` | `WARN 1` | `FAIL 1` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `0`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `1`
- Step regressions: `1`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **camwhorestv** `play`: `PASS -> FAIL` (CODE) | TypeError: run_site_child.<locals>.FakeVideoPlayer.play_from_kt_player() got an unexpected keyword argument 'user_agent'

## Improvements

- **longvideos**: `SKIP -> PASS`
- **porntrex**: `SKIP -> PASS`
