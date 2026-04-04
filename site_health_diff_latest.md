# Site Health Delta

- Current report: `live_smoke_20260404_064640.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 161` | `WARN 3` | `FAIL 3` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 161` | `WARN 4` | `FAIL 2` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `1`
- Step regressions: `0`

## New Failures

- **javgg**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177528

## Improvements

- **eroticage**: `WARN -> PASS`
