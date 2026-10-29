# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 196` | `WARN 3` | `FAIL 5` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 197` | `WARN 2` | `FAIL 5` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `4`
- Site regressions: `2`
- Step regressions: `2`

## New Failures

- **animeidhentai**: `PASS -> FAIL` (UNKNOWN) | list: List URL unavailable in harness (HTTP 504)

## Resolved Failures

- **mangoporn**: `FAIL -> PASS`

## Persistent Failures

- **hentai2w**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **animeidhentai** `list`: `PASS -> FAIL` (UNKNOWN) | List URL unavailable in harness (HTTP 504)
- **seaporn** `play`: `PASS -> FAIL` (NETWORK) | Timed out after 35s
