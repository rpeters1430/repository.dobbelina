# Site Health Delta

- Current report: `live_smoke_20260525_080806.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 156` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 15`
- Previous: `PASS 155` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 14`

## Delta Summary

- New failures: `0`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `1`
- Step regressions: `0`

## Persistent Failures

- **hentaidude**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1 ⚠️ [FLAKY: 0.0%]
- **speedporn**: `FAIL -> FAIL` (NETWORK) | Site process timed out after 140s ⚠️ [FLAKY: 50.0%]
