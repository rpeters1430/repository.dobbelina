# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 188` | `WARN 4` | `FAIL 5` | `ERROR 0` | `SKIP 3`
- Previous: `PASS 187` | `WARN 4` | `FAIL 6` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `1`
- Resolved failures: `2`
- Persistent failures: `4`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **mangoporn**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://mangoporn.net/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Resolved Failures

- **archivebate**: `FAIL -> PASS`
- **pornez**: `FAIL -> PASS`

## Persistent Failures

- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **mangoporn** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://mangoporn.net/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
