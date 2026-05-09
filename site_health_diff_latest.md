# Site Health Delta

- Current report: `live_smoke_20260509_071931.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 150` | `WARN 1` | `FAIL 4` | `ERROR 0` | `SKIP 16`
- Previous: `PASS 152` | `WARN 0` | `FAIL 3` | `ERROR 0` | `SKIP 16`

## Delta Summary

- New failures: `2`
- Resolved failures: `1`
- Persistent failures: `2`
- Site regressions: `3`
- Step regressions: `3`

## New Failures

- **porngo**: `PASS -> FAIL` (NETWORK) | list: TimeoutError: The read operation timed out
- **pornhoarder**: `PASS -> FAIL` (UNKNOWN) | list: HTTPError: HTTP Error 520: <none>

## Resolved Failures

- **motherless**: `FAIL -> PASS`

## Persistent Failures

- **jizzbunker**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)

## Step Regressions

- **porngo** `list`: `PASS -> FAIL` (NETWORK) | TimeoutError: The read operation timed out
- **pornhd3x** `search`: `SKIP -> FAIL` (NETWORK) | TimeoutError: The read operation timed out
- **pornhoarder** `list`: `PASS -> FAIL` (UNKNOWN) | HTTPError: HTTP Error 520: <none>
