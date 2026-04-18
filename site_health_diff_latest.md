# Site Health Delta

- Current report: `live_smoke_20260418_065242.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 166` | `WARN 1` | `FAIL 3` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 167` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `2`
- Resolved failures: `1`
- Persistent failures: `1`
- Site regressions: `2`
- Step regressions: `1`

## New Failures

- **noodlemagazine**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **whereismyporn**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s

## Resolved Failures

- **javgg**: `FAIL -> PASS`

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)

## Step Regressions

- **noodlemagazine** `list`: `SKIP -> FAIL` (PARSER) | List returned no videos
