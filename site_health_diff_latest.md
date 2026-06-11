# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 176` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 176` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `1`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **animeidhentai**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Resolved Failures

- **analdin**: `FAIL -> PASS`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **animeidhentai** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
