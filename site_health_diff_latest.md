# Site Health Delta

- Current report: `live_smoke_20260410_070053.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 160` | `WARN 3` | `FAIL 4` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 159` | `WARN 2` | `FAIL 6` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `2`
- Persistent failures: `4`
- Site regressions: `1`
- Step regressions: `1`

## Resolved Failures

- **analdin**: `FAIL -> PASS`
- **eporner**: `FAIL -> PASS`

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **peachurnet**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porndoe**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177580

## Step Regressions

- **pmvhaven** `search`: `SKIP -> FAIL` (NETWORK) | RuntimeError: Failed to connect to FlareSolverr at http://localhost:8191/v1: HTTPConnectionPool(host='localhost', port=8191): Read timed out. (read timeout=10). Please check if FlareSolverr is running and configured correctly in addon settings.
