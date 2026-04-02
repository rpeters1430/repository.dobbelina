# Site Health Delta

- Current report: `live_smoke_20260402_065357.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 159` | `WARN 4` | `FAIL 4` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 156` | `WARN 4` | `FAIL 7` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `2`
- Resolved failures: `5`
- Persistent failures: `2`
- Site regressions: `2`
- Step regressions: `1`

## New Failures

- **josporn**: `PASS -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)
- **speedporn**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s

## Resolved Failures

- **analdin**: `FAIL -> PASS`
- **eporner**: `FAIL -> PASS`
- **hdporn92**: `FAIL -> PASS`
- **peachurnet**: `FAIL -> PASS`
- **porndoe**: `FAIL -> PASS`

## Persistent Failures

- **supjav**: `FAIL -> FAIL` (NETWORK) | Site process timed out after 140s
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177511

## Step Regressions

- **josporn** `list`: `PASS -> FAIL` (NETWORK) | List URL unavailable in harness (HTTP 503)
