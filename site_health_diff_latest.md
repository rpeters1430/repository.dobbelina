# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 178` | `WARN 3` | `FAIL 1` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 179` | `WARN 1` | `FAIL 2` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `0`
- Resolved failures: `1`
- Persistent failures: `1`
- Site regressions: `3`
- Step regressions: `3`

## Resolved Failures

- **pornez**: `FAIL -> PASS`

## Persistent Failures

- **pornhoarder**: `FAIL -> FAIL` (UNKNOWN) | main: URLError: <urlopen error [Errno -5] No address associated with hostname> ⚠️ [FLAKY: 0.0%]

## Step Regressions

- **awmnet** `search`: `SKIP -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 404 from website
- **hentaidude** `search`: `SKIP -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr solved challenge but got HTTP 404 from website
- **ikisoda** `play`: `PASS -> FAIL` (CODE) | AttributeError: module 'kodi_six.xbmc' has no attribute 'Keyboard'

## Improvements

- **yrprno**: `WARN -> PASS`
