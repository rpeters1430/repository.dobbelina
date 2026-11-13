# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 194` | `WARN 3` | `FAIL 7` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 194` | `WARN 2` | `FAIL 8` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `0`
- Resolved failures: `1`
- Persistent failures: `7`
- Site regressions: `0`
- Step regressions: `1`

## Resolved Failures

- **sextb**: `FAIL -> WARN`

## Persistent Failures

- **hentai2w**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **hitprn**: `FAIL -> FAIL` (CODE) | main: AttributeError: 'AdultSite' object has no attribute 'img_tags'
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **watchporn**: `FAIL -> FAIL` (CODE) | main: AttributeError: 'AdultSite' object has no attribute 'img_channels'
- **watchpornx**: `FAIL -> FAIL` (CODE) | main: AttributeError: 'AdultSite' object has no attribute 'img_movies'
- **xsharings**: `FAIL -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://twitter.com/xsharings: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **sextb** `play`: `PASS -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
