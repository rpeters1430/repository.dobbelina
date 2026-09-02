# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 187` | `WARN 2` | `FAIL 3` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 189` | `WARN 2` | `FAIL 1` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `2`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `2`
- Step regressions: `2`

## New Failures

- **javseen**: `PASS -> FAIL` (UNKNOWN) | list: List URL unavailable in harness (HTTP 502)
- **xtapesla**: `PASS -> FAIL` (ENV) | list: RuntimeError: FlareSolverr error for https://xtapes.la/tag/full-movie/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Persistent Failures

- **analdin**: `FAIL -> FAIL` (PARSER) | list: List returned no videos

## Step Regressions

- **javseen** `list`: `SKIP -> FAIL` (UNKNOWN) | List URL unavailable in harness (HTTP 502)
- **xtapesla** `list`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://xtapes.la/tag/full-movie/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
