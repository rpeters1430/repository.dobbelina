# Site Health Delta

- Current report: `live_smoke_20260523_072315.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 155` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 14`
- Previous: `PASS 157` | `WARN 0` | `FAIL 1` | `ERROR 0` | `SKIP 14`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos ⚠️ [FLAKY: 40.0%]

## Persistent Failures

- **hentaidude**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
