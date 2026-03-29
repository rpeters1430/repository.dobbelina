# Site Health Delta

- Current report: `live_smoke_20260329_065009.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 154` | `WARN 5` | `FAIL 8` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 159` | `WARN 6` | `FAIL 1` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `6`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `6`
- Step regressions: `4`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **ask4porn**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s
- **eporner**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **hdporn92**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s
- **peachurnet**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **porndoe**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Persistent Failures

- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177476

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **eporner** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **peachurnet** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **porndoe** `list`: `PASS -> FAIL` (PARSER) | List returned no videos

## Improvements

- **playvids**: `WARN -> PASS`
