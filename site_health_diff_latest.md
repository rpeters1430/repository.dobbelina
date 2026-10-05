# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 184` | `WARN 5` | `FAIL 8` | `ERROR 0` | `SKIP 4`
- Previous: `PASS 188` | `WARN 4` | `FAIL 6` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `2`
- Resolved failures: `0`
- Persistent failures: `6`
- Site regressions: `4`
- Step regressions: `3`

## New Failures

- **netflixporno**: `PASS -> FAIL` (UNKNOWN) | list: List URL unavailable in harness (HTTP 500)
- **pornmz**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://pornmz.com/page/1?filter=latest: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Persistent Failures

- **camcaps**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://camcaps.tv/videos: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **mangoporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **cumlouder** `play`: `PASS -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **netflixporno** `list`: `SKIP -> FAIL` (UNKNOWN) | List URL unavailable in harness (HTTP 500)
- **pornmz** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://pornmz.com/page/1?filter=latest: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
