# Site Health Delta

- Current report: `live_smoke_20260511_040723.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 152` | `WARN 0` | `FAIL 4` | `ERROR 0` | `SKIP 15`
- Previous: `PASS 150` | `WARN 1` | `FAIL 4` | `ERROR 0` | `SKIP 16`

## Delta Summary

- New failures: `0`
- Resolved failures: `0`
- Persistent failures: `4`
- Site regressions: `0`
- Step regressions: `0`

## Persistent Failures

- **analdin**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **hentaidude**: `FAIL -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **motherless**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)

## Improvements

- **kissjav**: `SKIP -> PASS`
- **xfreehd**: `WARN -> PASS`
