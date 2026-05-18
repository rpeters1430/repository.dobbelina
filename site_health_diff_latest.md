# Site Health Delta

- Current report: `live_smoke_20260518_153710.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 154` | `WARN 1` | `FAIL 3` | `ERROR 0` | `SKIP 14`
- Previous: `PASS 154` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 15`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `2`
- Step regressions: `1`

## New Failures

- **speedporn**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s

## Persistent Failures

- **analdin**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **hentaidude**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **porndig** `play`: `PASS -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)

## Improvements

- **erogarga**: `SKIP -> PASS`
