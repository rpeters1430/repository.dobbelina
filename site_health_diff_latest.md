# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 187` | `WARN 6` | `FAIL 5` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 190` | `WARN 5` | `FAIL 2` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `3`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `4`
- Step regressions: `5`

## New Failures

- **justfullporn**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://justfullporn.net/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **xtapesla**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Persistent Failures

- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **awmnet** `categories`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://www.4tube.com/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **justfullporn** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://justfullporn.net/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **naughtyblog** `categories`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://www.naughtyblog.org/categories/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn** `list`: `SKIP -> FAIL` (PARSER) | List returned no videos
- **xtapesla** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Improvements

- **longvideos**: `SKIP -> PASS`
