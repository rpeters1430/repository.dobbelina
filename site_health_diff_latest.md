# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 185` | `WARN 4` | `FAIL 0` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 186` | `WARN 3` | `FAIL 1` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `0`
- Resolved failures: `1`
- Persistent failures: `0`
- Site regressions: `3`
- Step regressions: `3`

## Resolved Failures

- **pornhoarder**: `FAIL -> SKIP`

## Step Regressions

- **hanime** `play`: `SKIP -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 404 from website
- **xoxo** `play`: `PASS -> FAIL` (CODE) | ValueError: No videolink found!
- **xtapesla** `search`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://xtapes.la/?s=test: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Improvements

- **camwhorestv**: `WARN -> PASS`
- **porndoe**: `WARN -> PASS`
