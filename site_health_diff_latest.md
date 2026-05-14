# Site Health Delta

- Current report: `live_smoke_20260514_052718.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 152` | `WARN 0` | `FAIL 4` | `ERROR 0` | `SKIP 15`
- Previous: `PASS 153` | `WARN 0` | `FAIL 3` | `ERROR 0` | `SKIP 15`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `3`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Persistent Failures

- **hentaidude**: `FAIL -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **motherless**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
