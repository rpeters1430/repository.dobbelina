# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 187` | `WARN 4` | `FAIL 7` | `ERROR 0` | `SKIP 3`
- Previous: `PASS 186` | `WARN 4` | `FAIL 8` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `0`
- Resolved failures: `1`
- Persistent failures: `7`
- Site regressions: `1`
- Step regressions: `1`

## Resolved Failures

- **justfullporn**: `FAIL -> PASS`

## Persistent Failures

- **camcaps**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://camcaps.tv/videos: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **mangoporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **netflixporno**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **awmnet** `search`: `SKIP -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 404 from website

## Improvements

- **cumlouder**: `WARN -> PASS`
