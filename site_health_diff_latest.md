# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 178` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 178` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `0`
- Step regressions: `0`

## Persistent Failures

- **motherless**: `FAIL -> FAIL` (UNKNOWN) | list: List URL unavailable in harness (HTTP 502) ⚠️ [FLAKY: 50.0%]
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]
