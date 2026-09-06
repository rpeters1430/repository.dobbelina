# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 187` | `WARN 6` | `FAIL 2` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 185` | `WARN 6` | `FAIL 1` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `3`
- Step regressions: `3`

## New Failures

- **pornmz**: `WARN -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://pornmz.com/page/1?filter=latest: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Persistent Failures

- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **cumlouder** `play`: `PASS -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **pornmz** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://pornmz.com/page/1?filter=latest: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla** `play`: `SKIP -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://xtapes.la/videos/step-son-cum-inside-me-8-2025-full-movie/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Improvements

- **xozilla**: `WARN -> PASS`
