# Site Health Delta

- Current report: `live_smoke_20260415_070325.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 163` | `WARN 2` | `FAIL 5` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 164` | `WARN 2` | `FAIL 4` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `2`
- Resolved failures: `0`
- Persistent failures: `3`
- Site regressions: `2`
- Step regressions: `1`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **javgg**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s

## Persistent Failures

- **cloudbate**: `FAIL -> FAIL` (CODE) | main: TypeError: URL_Dispatcher.add_dir() got an unexpected keyword argument 'lp'
- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177623

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
