# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 175` | `WARN 0` | `FAIL 3` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 176` | `WARN 0` | `FAIL 2` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `1`
- Step regressions: `0`

## New Failures

- **hdporn92**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s

## Persistent Failures

- **animeidhentai**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **pornhoarder**: `FAIL -> FAIL` (BLOCKED) | main: HTTPError: HTTP Error 403: Forbidden ⚠️ [FLAKY: 0.0%]
