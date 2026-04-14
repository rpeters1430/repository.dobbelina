# Site Health Delta

- Current report: `live_smoke_20260414_071621.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 164` | `WARN 2` | `FAIL 4` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 164` | `WARN 2` | `FAIL 4` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `0`
- Resolved failures: `1`
- Persistent failures: `3`
- Site regressions: `0`
- Step regressions: `0`

## Resolved Failures

- **analdin**: `FAIL -> PASS`

## Persistent Failures

- **cloudbate**: `FAIL -> FAIL` (CODE) | main: TypeError: URL_Dispatcher.add_dir() got an unexpected keyword argument 'lp'
- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177615
