# Site Health Delta

- Current report: `live_smoke_20260506_072038.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 152` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 17`
- Previous: `PASS 153` | `WARN 0` | `FAIL 1` | `ERROR 0` | `SKIP 17`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
