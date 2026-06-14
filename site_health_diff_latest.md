# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 175` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 176` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `0`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `1`
- Step regressions: `1`

## Persistent Failures

- **analdin**: `FAIL -> FAIL` (PARSER) | list: List returned no videos ⚠️ [FLAKY: 60.0%]
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **noodlemagazine** `play`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://noodlemagazine.com/watch/-209133387_456241982: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
