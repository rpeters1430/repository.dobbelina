# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 187` | `WARN 4` | `FAIL 6` | `ERROR 0` | `SKIP 3`
- Previous: `PASS 189` | `WARN 4` | `FAIL 4` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `2`
- Resolved failures: `0`
- Persistent failures: `4`
- Site regressions: `2`
- Step regressions: `3`

## New Failures

- **archivebate**: `PASS -> FAIL` (NETWORK) | main: ReadTimeout: HTTPSConnectionPool(host='archivebate.com', port=443): Read timed out. (read timeout=15)
- **pornez**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://pornezoo.net: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Persistent Failures

- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **archivebate** `list`: `PASS -> FAIL` (NETWORK) | ReadTimeout: HTTPSConnectionPool(host='archivebate.com', port=443): Read timed out. (read timeout=15)
- **archivebate** `main`: `PASS -> FAIL` (NETWORK) | ReadTimeout: HTTPSConnectionPool(host='archivebate.com', port=443): Read timed out. (read timeout=15)
- **pornez** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://pornezoo.net: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
