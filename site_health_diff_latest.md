# Site Health Delta

- Current report: `live_smoke_20260411_064406.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 162` | `WARN 2` | `FAIL 3` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 160` | `WARN 3` | `FAIL 4` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `1`
- Resolved failures: `2`
- Persistent failures: `2`
- Site regressions: `1`
- Step regressions: `1`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Resolved Failures

- **peachurnet**: `FAIL -> PASS`
- **porndoe**: `FAIL -> PASS`

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177588

## Step Regressions

- **analdin** `list`: `SKIP -> FAIL` (PARSER) | List returned no videos

## Improvements

- **pmvhaven**: `WARN -> PASS`
