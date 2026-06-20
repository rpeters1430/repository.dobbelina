# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 179` | `WARN 0` | `FAIL 1` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 176` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `0`
- Resolved failures: `1`
- Persistent failures: `1`
- Site regressions: `0`
- Step regressions: `0`

## Resolved Failures

- **analdin**: `FAIL -> PASS`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Improvements

- **motherless**: `SKIP -> PASS`
- **rlc**: `SKIP -> PASS`
