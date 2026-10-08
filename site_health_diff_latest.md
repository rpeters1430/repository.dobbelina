# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 185` | `WARN 10` | `FAIL 8` | `ERROR 0` | `SKIP 3`
- Previous: `PASS 187` | `WARN 4` | `FAIL 7` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `7`
- Site regressions: `2`
- Step regressions: `2`

## New Failures

- **pornez**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://pornezoo.net: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Persistent Failures

- **camcaps**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://camcaps.tv/videos: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **mangoporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **netflixporno**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **pornez** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://pornezoo.net: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xoxostream** `play`: `PASS -> FAIL` (CODE) | ValueError: No videolink found!
