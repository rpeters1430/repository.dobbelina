# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 197` | `WARN 1` | `FAIL 6` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 197` | `WARN 2` | `FAIL 5` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `5`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **thothub**: `PASS -> FAIL` (UNKNOWN) | list: List URL unavailable in harness (HTTP 521)

## Persistent Failures

- **hentai2w**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `FAIL -> FAIL` (NETWORK) | main: TimeoutError: The read operation timed out
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **thothub** `list`: `PASS -> FAIL` (UNKNOWN) | List URL unavailable in harness (HTTP 521)

## Improvements

- **pornslash**: `WARN -> PASS`
