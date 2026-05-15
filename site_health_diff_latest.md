# Site Health Delta

- Current report: `live_smoke_20260515_073807.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 151` | `WARN 1` | `FAIL 3` | `ERROR 0` | `SKIP 16`
- Previous: `PASS 153` | `WARN 0` | `FAIL 3` | `ERROR 0` | `SKIP 15`

## Delta Summary

- New failures: `2`
- Resolved failures: `2`
- Persistent failures: `1`
- Site regressions: `3`
- Step regressions: `2`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos ⚠️ [FLAKY: 66.7%]
- **speedporn**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s

## Resolved Failures

- **josporn**: `FAIL -> PASS`
- **motherless**: `FAIL -> SKIP`

## Persistent Failures

- **hentaidude**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **xfreehd** `play`: `SKIP -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
