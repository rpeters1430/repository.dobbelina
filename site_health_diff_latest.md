# Site Health Delta

- Current report: `live_smoke_20260524_074048.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 155` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 14`
- Previous: `PASS 155` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 14`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `1`
- Site regressions: `1`
- Step regressions: `0`

## New Failures

- **speedporn**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s ⚠️ [FLAKY: 60.0%]

## Resolved Failures

- **analdin**: `FAIL -> PASS`

## Persistent Failures

- **hentaidude**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1 ⚠️ [FLAKY: 0.0%]
