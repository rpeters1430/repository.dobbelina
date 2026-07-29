# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 177` | `WARN 1` | `FAIL 3` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 178` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **thothub**: `PASS -> FAIL` (UNKNOWN) | list: List URL unavailable in harness (HTTP 521)

## Persistent Failures

- **motherless**: `FAIL -> FAIL` (UNKNOWN) | list: List URL unavailable in harness (HTTP 502) ⚠️ [FLAKY: 30.0%]
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **thothub** `list`: `PASS -> FAIL` (UNKNOWN) | List URL unavailable in harness (HTTP 521)
