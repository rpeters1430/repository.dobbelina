# Site Health Delta

- Current report: `live_smoke_20260601_081503.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 173` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 171` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `1`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **txxx**: `PASS -> FAIL` (CODE) | main: AttributeError: 'NoneType' object has no attribute 'strip'

## Resolved Failures

- **analdin**: `FAIL -> PASS`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden

## Step Regressions

- **txxx** `main`: `PASS -> FAIL` (CODE) | AttributeError: 'NoneType' object has no attribute 'strip'
