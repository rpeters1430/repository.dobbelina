# Site Health Delta

- Current report: `live_smoke_20260510_072231.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 150` | `WARN 1` | `FAIL 4` | `ERROR 0` | `SKIP 16`
- Previous: `PASS 150` | `WARN 1` | `FAIL 4` | `ERROR 0` | `SKIP 16`

## Delta Summary

- New failures: `3`
- Resolved failures: `3`
- Persistent failures: `1`
- Site regressions: `5`
- Step regressions: `6`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **hentaidude**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **motherless**: `PASS -> FAIL` (PARSER) | list: List returned no videos

## Resolved Failures

- **jizzbunker**: `FAIL -> PASS`
- **porngo**: `FAIL -> PASS`
- **pornhoarder**: `FAIL -> PASS`

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **hentaidude** `list`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://hentaidude.xxx/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **hentaidude** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://hentaidude.xxx/page/1/?m_orderby=latest: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **hentaidude** `search`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://hentaidude.xxx/test&post_type=wp-manga: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **motherless** `list`: `SKIP -> FAIL` (PARSER) | List returned no videos
- **xfreehd** `play`: `SKIP -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)

## Improvements

- **pornhd3x**: `WARN -> PASS`
- **stripchat**: `SKIP -> PASS`
