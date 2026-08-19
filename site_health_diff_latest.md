# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 183` | `WARN 1` | `FAIL 3` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 181` | `WARN 2` | `FAIL 3` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `1`
- Resolved failures: `1`
- Persistent failures: `2`
- Site regressions: `1`
- Step regressions: `2`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Resolved Failures

- **pornez**: `FAIL -> PASS`

## Persistent Failures

- **hypnotube**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **pornhoarder** `search`: `SKIP -> FAIL` (BLOCKED) | HTTPError: HTTP Error 403: Forbidden

## Improvements

- **pornslash**: `WARN -> PASS`
- **spankbang**: `SKIP -> PASS`
