# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 194` | `WARN 3` | `FAIL 6` | `ERROR 0` | `SKIP 3`
- Previous: `PASS 193` | `WARN 3` | `FAIL 7` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `1`
- Resolved failures: `2`
- Persistent failures: `5`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **mangoporn**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Resolved Failures

- **camcaps**: `FAIL -> PASS`
- **justfullporn**: `FAIL -> PASS`

## Persistent Failures

- **hentai2w**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **mangoporn** `list`: `SKIP -> FAIL` (PARSER) | List returned no videos
