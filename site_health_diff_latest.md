# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 172` | `WARN 2` | `FAIL 1` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 172` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `0`
- Resolved failures: `1`
- Persistent failures: `1`
- Site regressions: `2`
- Step regressions: `2`

## Resolved Failures

- **analdin**: `FAIL -> PASS`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 30.0%]

## Step Regressions

- **perverzija** `play`: `SKIP -> FAIL` (CODE) | IndexError: list index out of range
- **pornmz** `categories`: `PASS -> FAIL` (NETWORK) | Timed out after 35s

## Improvements

- **tokyomotion**: `WARN -> PASS`
