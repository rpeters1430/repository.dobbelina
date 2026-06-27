# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 178` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 178` | `WARN 1` | `FAIL 1` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos

## Improvements

- **perverzija**: `WARN -> PASS`
