# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 197` | `WARN 1` | `FAIL 6` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 195` | `WARN 1` | `FAIL 8` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `0`
- Resolved failures: `2`
- Persistent failures: `6`
- Site regressions: `0`
- Step regressions: `0`

## Resolved Failures

- **archivebate**: `FAIL -> PASS`
- **hobbyporn**: `FAIL -> PASS`

## Persistent Failures

- **hentai2w**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **pornez**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://pornezoo.net: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
