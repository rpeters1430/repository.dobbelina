# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 177` | `WARN 1` | `FAIL 3` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 180` | `WARN 0` | `FAIL 1` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `2`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `3`
- Step regressions: `2`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **supjav**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **familypornhd** `play`: `SKIP -> FAIL` (CODE) | JSONDecodeError: Expecting value: line 1 column 1 (char 0)
