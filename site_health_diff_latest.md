# Site Health Delta

- Current report: `live_smoke_20260408_070037.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 162` | `WARN 2` | `FAIL 3` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 161` | `WARN 3` | `FAIL 3` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `0`
- Persistent failures: `3`
- Site regressions: `0`
- Step regressions: `0`

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **peachurnet**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177563

## Improvements

- **heavyr**: `WARN -> PASS`
