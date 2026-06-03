# Site Health Delta

- Current report: `live_smoke_20260603_081533.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 172` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 172` | `WARN 0` | `FAIL 3` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `1`
- Resolved failures: `2`
- Persistent failures: `1`
- Site regressions: `2`
- Step regressions: `2`

## New Failures

- **hanime**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Resolved Failures

- **analdin**: `FAIL -> PASS`
- **anysex**: `FAIL -> PASS`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 50.0%]

## Step Regressions

- **hanime** `list`: `SKIP -> FAIL` (PARSER) | List returned no videos
- **perverzija** `play`: `SKIP -> FAIL` (CODE) | IndexError: list index out of range
