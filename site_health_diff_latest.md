# Site Health Delta

- Current report: `live_smoke_20260326_065127.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 156` | `WARN 6` | `FAIL 4` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 154` | `WARN 5` | `FAIL 7` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `3`
- Persistent failures: `4`
- Site regressions: `1`
- Step regressions: `1`

## Resolved Failures

- **hdporn92**: `FAIL -> PASS`
- **speedporn**: `FAIL -> PASS`
- **xhamster**: `FAIL -> PASS`

## Persistent Failures

- **analdin**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **eporner**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porndoe**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177450

## Step Regressions

- **xfreehd** `play`: `SKIP -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
