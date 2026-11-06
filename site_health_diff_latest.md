# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 195` | `WARN 3` | `FAIL 6` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 197` | `WARN 3` | `FAIL 4` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `2`
- Resolved failures: `0`
- Persistent failures: `4`
- Site regressions: `2`
- Step regressions: `2`

## New Failures

- **tokyomotion**: `PASS -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **xmegadrive**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://www.xmegadrive.com/latest-updates/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Persistent Failures

- **hentai2w**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **tokyomotion** `list`: `PASS -> FAIL` (NETWORK) | List URL unavailable in harness (HTTP 503)
- **xmegadrive** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://www.xmegadrive.com/latest-updates/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
