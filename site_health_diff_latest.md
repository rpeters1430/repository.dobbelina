# Site Health Delta

- Current report: `live_smoke_20260419_070156.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 164` | `WARN 3` | `FAIL 3` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 166` | `WARN 1` | `FAIL 3` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `2`
- Site regressions: `3`
- Step regressions: `3`

## New Failures

- **motherless**: `PASS -> FAIL` (UNKNOWN) | list: List URL unavailable in harness (HTTP 502)

## Resolved Failures

- **whereismyporn**: `FAIL -> PASS`

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **noodlemagazine**: `FAIL -> FAIL` (PARSER) | list: List returned no videos

## Step Regressions

- **eroticage** `play`: `PASS -> FAIL` (CODE) | AttributeError: 'NoneType' object has no attribute 'get'
- **motherless** `list`: `PASS -> FAIL` (UNKNOWN) | List URL unavailable in harness (HTTP 502)
- **xhamster** `play`: `PASS -> FAIL` (CODE) | AttributeError: 'NoneType' object has no attribute 'get'
