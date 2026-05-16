# Site Health Delta

- Current report: `live_smoke_20260516_071101.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 154` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 15`
- Previous: `PASS 151` | `WARN 1` | `FAIL 3` | `ERROR 0` | `SKIP 16`

## Delta Summary

- New failures: `0`
- Resolved failures: `1`
- Persistent failures: `2`
- Site regressions: `0`
- Step regressions: `0`

## Resolved Failures

- **speedporn**: `FAIL -> PASS`

## Persistent Failures

- **analdin**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **hentaidude**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1

## Improvements

- **motherless**: `SKIP -> PASS`
- **xfreehd**: `WARN -> PASS`
