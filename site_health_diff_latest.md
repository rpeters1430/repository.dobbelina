# Site Health Delta

- Current report: `live_smoke_20260512_072909.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 153` | `WARN 0` | `FAIL 3` | `ERROR 0` | `SKIP 15`
- Previous: `PASS 153` | `WARN 0` | `FAIL 3` | `ERROR 0` | `SKIP 15`

## Delta Summary

- New failures: `0`
- Resolved failures: `0`
- Persistent failures: `3`
- Site regressions: `0`
- Step regressions: `0`

## Persistent Failures

- **hentaidude**: `FAIL -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **motherless**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
