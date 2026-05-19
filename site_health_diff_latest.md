# Site Health Delta

- Current report: `live_smoke_20260519_075830.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 153` | `WARN 2` | `FAIL 3` | `ERROR 0` | `SKIP 14`
- Previous: `PASS 154` | `WARN 1` | `FAIL 3` | `ERROR 0` | `SKIP 14`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `2`
- Site regressions: `3`
- Step regressions: `3`

## New Failures

- **pornhat**: `PASS -> FAIL` (NETWORK) | main: Timed out after 35s

## Resolved Failures

- **analdin**: `FAIL -> PASS`

## Persistent Failures

- **hentaidude**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn**: `FAIL -> FAIL` (NETWORK) | Site process timed out after 140s

## Step Regressions

- **okxxx** `play`: `PASS -> FAIL` (NETWORK) | Timed out after 35s
- **porngo** `search`: `SKIP -> FAIL` (NETWORK) | Timed out after 35s
- **pornhat** `main`: `PASS -> FAIL` (NETWORK) | Timed out after 35s

## Improvements

- **porndig**: `WARN -> PASS`
