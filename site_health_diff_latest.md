# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 194` | `WARN 3` | `FAIL 7` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 196` | `WARN 3` | `FAIL 5` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `3`
- Resolved failures: `1`
- Persistent failures: `4`
- Site regressions: `4`
- Step regressions: `4`

## New Failures

- **justfullporn**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://justfullporn.net/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **mangoporn**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **netflixporno**: `PASS -> FAIL` (UNKNOWN) | list: List URL unavailable in harness (HTTP 525)

## Resolved Failures

- **animeidhentai**: `FAIL -> PASS`

## Persistent Failures

- **hentai2w**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **justfullporn** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://justfullporn.net/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **mangoporn** `list`: `SKIP -> FAIL` (PARSER) | List returned no videos
- **netflixporno** `list`: `SKIP -> FAIL` (UNKNOWN) | List URL unavailable in harness (HTTP 525)
- **sextb** `play`: `PASS -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)

## Improvements

- **seaporn**: `WARN -> PASS`
