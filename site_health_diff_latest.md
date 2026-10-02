# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 185` | `WARN 3` | `FAIL 9` | `ERROR 0` | `SKIP 3`
- Previous: `PASS 189` | `WARN 3` | `FAIL 5` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `4`
- Resolved failures: `0`
- Persistent failures: `5`
- Site regressions: `4`
- Step regressions: `4`

## New Failures

- **awmnet**: `PASS -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://www.ixxx.com/new?pricing=free: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **justfullporn**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://justfullporn.net/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **mangoporn**: `PASS -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **pornmz**: `PASS -> FAIL` (UNKNOWN) | list: List URL unavailable in harness (HTTP 500)

## Persistent Failures

- **camcaps**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://camcaps.tv/videos: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **awmnet** `list`: `SKIP -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://www.ixxx.com/new?pricing=free: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **justfullporn** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://justfullporn.net/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **mangoporn** `list`: `SKIP -> FAIL` (NETWORK) | List URL unavailable in harness (HTTP 503)
- **pornmz** `list`: `PASS -> FAIL` (UNKNOWN) | List URL unavailable in harness (HTTP 500)
