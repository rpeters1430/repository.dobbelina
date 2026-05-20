# Site Health Delta

- Current report: `live_smoke_20260520_074408.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 155` | `WARN 0` | `FAIL 3` | `ERROR 0` | `SKIP 14`
- Previous: `PASS 153` | `WARN 2` | `FAIL 3` | `ERROR 0` | `SKIP 14`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `2`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos ⚠️ [FLAKY: 50.0%]

## Resolved Failures

- **pornhat**: `FAIL -> PASS`

## Persistent Failures

- **hentaidude**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `FAIL -> FAIL` (NETWORK) | Site process timed out after 140s

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos

## Improvements

- **okxxx**: `WARN -> PASS`
- **porngo**: `WARN -> PASS`
