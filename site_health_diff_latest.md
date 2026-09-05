# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 185` | `WARN 6` | `FAIL 1` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 187` | `WARN 3` | `FAIL 1` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `0`
- Site regressions: `5`
- Step regressions: `5`

## New Failures

- **xsharings**: `PASS -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Resolved Failures

- **jizzbunker**: `FAIL -> PASS`

## Step Regressions

- **awmnet** `search`: `SKIP -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 404 from website
- **pornmz** `play`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://pornmz.com/wp-content/plugins/clean-tube-player/public/player-x.php?q=cG9zdF9pZD0yNjAwMTEmdHlwZT12aWRlbyZ0YWc9JTNDdmlkZW8lMjBpZCUzRCUyMndwc3QtdmlkZW8lMjIlMjBjbGFzcyUzRCUyMnZpZGVvLWpzJTIwdmpzLWJpZy1wbGF5LWNlbnRlcmVkJTIyJTIwY29udHJvbHMlMjBwcmVsb2FkJTNEJTIyYXV0byUyMiUyMHdpZHRoJTNEJTIyNjQwJTIyJTIwaGVpZ2h0JTNEJTIyMjY0JTIyJTIwcG9zdGVyJTNEJTIyaHR0cHMlM0ElMkYlMkZwb3JubXouY29tJTJGd3AtY29udGVudCUyRnVwbG9hZHMlMkYyMDI2JTJGMDIlMkZCcmF6emVyc0V4eHRyYS1LaXJhLU5vaXItTWFyaW5hLUdvbGQtQ3VtLVBsYXktV2l0aC1Vcy02NDB4MzYwLmpwZyUyMiUzRSUzQ3NvdXJjZSUyMHNyYyUzRCUyMmh0dHBzJTNBJTJGJTJGdmlkZW8udHdpbWcuY29tJTJGYW1wbGlmeV92aWRlbyUyRjIwMjEwMjg5NzkxNDMyNTgxMTIlMkZwbCUyRmdHVE9ZaXR0OEFUaUlrdW8ubTN1OCUyMiUyMHR5cGUlM0QlMjJ2aWRlbyUyRm0zdTglMjIlM0UlM0MlMkZ2aWRlbyUzRQ==: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xoxo** `play`: `PASS -> FAIL` (CODE) | ValueError: No videolink found!
- **xozilla** `play`: `PASS -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **xsharings** `list`: `SKIP -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Improvements

- **spankbang**: `SKIP -> PASS`
- **xtapesla**: `WARN -> PASS`
