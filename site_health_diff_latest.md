# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 183` | `WARN 1` | `FAIL 1` | `ERROR 0` | `SKIP 3`
- Previous: `PASS 183` | `WARN 1` | `FAIL 3` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `2`
- Persistent failures: `1`
- Site regressions: `2`
- Step regressions: `0`

## Resolved Failures

- **hypnotube**: `FAIL -> PASS`
- **pornobae**: `FAIL -> PASS`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]
