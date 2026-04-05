# Site Health Delta

- Current report: `live_smoke_20260405_064929.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 162` | `WARN 3` | `FAIL 2` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 161` | `WARN 3` | `FAIL 3` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `1`
- Persistent failures: `2`
- Site regressions: `0`
- Step regressions: `1`

## Resolved Failures

- **javgg**: `FAIL -> PASS`

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177537

## Step Regressions

- **heavyr** `categories`: `PASS -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177537
