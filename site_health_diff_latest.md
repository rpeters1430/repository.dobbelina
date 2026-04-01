# Site Health Delta

- Current report: `live_smoke_20260401_070106.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 156` | `WARN 4` | `FAIL 7` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 157` | `WARN 5` | `FAIL 5` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `3`
- Resolved failures: `1`
- Persistent failures: `4`
- Site regressions: `3`
- Step regressions: `1`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **hdporn92**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s
- **supjav**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s

## Resolved Failures

- **ask4porn**: `FAIL -> PASS`

## Persistent Failures

- **eporner**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **peachurnet**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **porndoe**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177502

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos

## Improvements

- **xhamster**: `WARN -> PASS`
