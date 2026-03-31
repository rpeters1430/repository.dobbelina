# Site Health Delta

- Current report: `live_smoke_20260331_065444.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 157` | `WARN 5` | `FAIL 5` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 160` | `WARN 4` | `FAIL 3` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `3`
- Resolved failures: `1`
- Persistent failures: `2`
- Site regressions: `4`
- Step regressions: `4`

## New Failures

- **ask4porn**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s
- **eporner**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **porndoe**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Resolved Failures

- **anysex**: `FAIL -> PASS`

## Persistent Failures

- **peachurnet**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177493

## Step Regressions

- **eporner** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **heavyr** `categories`: `PASS -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177493
- **porndoe** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **xhamster** `play`: `PASS -> FAIL` (CODE) | AttributeError: 'NoneType' object has no attribute 'get'
