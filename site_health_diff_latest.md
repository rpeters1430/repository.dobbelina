# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 185` | `WARN 2` | `FAIL 2` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 186` | `WARN 3` | `FAIL 0` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `2`
- Resolved failures: `0`
- Persistent failures: `0`
- Site regressions: `2`
- Step regressions: `2`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **xtheatre**: `WARN -> FAIL` (BLOCKED) | list: RuntimeError: FlareSolverr solved challenge but got HTTP 500 from website

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **xtheatre** `list`: `PASS -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 500 from website
