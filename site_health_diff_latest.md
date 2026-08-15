# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 179` | `WARN 2` | `FAIL 2` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 178` | `WARN 3` | `FAIL 2` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `0`
- Step regressions: `0`

## Persistent Failures

- **hypnotube**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]

## Improvements

- **pornhd3x**: `WARN -> PASS`
