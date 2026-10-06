# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 186` | `WARN 4` | `FAIL 8` | `ERROR 0` | `SKIP 3`
- Previous: `PASS 184` | `WARN 5` | `FAIL 8` | `ERROR 0` | `SKIP 4`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `7`
- Site regressions: `1`
- Step regressions: `2`

## New Failures

- **justfullporn**: `PASS -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://justfullporn.net/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Resolved Failures

- **pornmz**: `FAIL -> PASS`

## Persistent Failures

- **camcaps**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://camcaps.tv/videos: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **mangoporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **netflixporno**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **justfullporn** `list`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://justfullporn.net/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **mangoporn** `categories`: `SKIP -> FAIL` (NETWORK) | TimeoutError: The read operation timed out

## Improvements

- **awmnet**: `WARN -> PASS`
- **reallifecam**: `SKIP -> PASS`
