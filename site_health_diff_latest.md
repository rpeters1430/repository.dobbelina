# Site Health Delta

- Current report: `live_smoke_20260508_070732.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 152` | `WARN 0` | `FAIL 3` | `ERROR 0` | `SKIP 16`
- Previous: `PASS 153` | `WARN 0` | `FAIL 1` | `ERROR 0` | `SKIP 17`

## Delta Summary

- New failures: `2`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `2`
- Step regressions: `1`

## New Failures

- **jizzbunker**: `SKIP -> FAIL` (PARSER) | list: List returned no videos
- **motherless**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)

## Step Regressions

- **jizzbunker** `list`: `SKIP -> FAIL` (PARSER) | List returned no videos
