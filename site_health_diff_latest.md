# Site Health Delta

- Current report: `live_smoke_20260501_072533.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 153` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 16`
- Previous: `PASS 155` | `WARN 0` | `FAIL 1` | `ERROR 0` | `SKIP 15`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `2`
- Step regressions: `1`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
