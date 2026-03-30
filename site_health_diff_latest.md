# Site Health Delta

- Current report: `live_smoke_20260330_070519.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 160` | `WARN 4` | `FAIL 3` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 154` | `WARN 5` | `FAIL 8` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `5`
- Persistent failures: `3`
- Site regressions: `0`
- Step regressions: `0`

## Resolved Failures

- **analdin**: `FAIL -> PASS`
- **ask4porn**: `FAIL -> PASS`
- **eporner**: `FAIL -> PASS`
- **hdporn92**: `FAIL -> PASS`
- **porndoe**: `FAIL -> PASS`

## Persistent Failures

- **anysex**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **peachurnet**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177485

## Improvements

- **xmoviesforyou**: `WARN -> PASS`
