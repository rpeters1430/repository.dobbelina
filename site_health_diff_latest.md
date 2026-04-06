# Site Health Delta

- Current report: `live_smoke_20260406_070622.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 159` | `WARN 5` | `FAIL 3` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 162` | `WARN 3` | `FAIL 2` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `1`
- Resolved failures: `0`
- Persistent failures: `2`
- Site regressions: `3`
- Step regressions: `3`

## New Failures

- **porndoe**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177545

## Step Regressions

- **eroticage** `play`: `PASS -> FAIL` (CODE) | AttributeError: 'NoneType' object has no attribute 'get'
- **porndoe** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **xhamster** `play`: `PASS -> FAIL` (CODE) | AttributeError: 'NoneType' object has no attribute 'get'
