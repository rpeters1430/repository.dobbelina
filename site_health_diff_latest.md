# Site Health Delta

- Current report: `live_smoke_20260602_081028.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 172` | `WARN 0` | `FAIL 3` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 173` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `2`
- Resolved failures: `1`
- Persistent failures: `1`
- Site regressions: `2`
- Step regressions: `1`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos ⚠️ [FLAKY: 40.0%]
- **anysex**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s

## Resolved Failures

- **txxx**: `FAIL -> PASS`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 60.0%]

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
