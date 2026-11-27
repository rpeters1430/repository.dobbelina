# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 165` | `WARN 2` | `FAIL 37` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 167` | `WARN 2` | `FAIL 35` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `3`
- Resolved failures: `1`
- Persistent failures: `34`
- Site regressions: `3`
- Step regressions: `8`

## New Failures

- **javgg**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **peekvids**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **sexyporn**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos

## Resolved Failures

- **xnxx**: `FAIL -> PASS`

## Persistent Failures

- **analdin**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **cumlouder**: `FAIL -> FAIL` (ENV) | search: RuntimeError: FlareSolverr error for https://www.cumlouder.com/search/?q=test: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **eporner**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **freshporno**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **hentai2w**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **hentaicity**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **hentaidude**: `FAIL -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **hpjav**: `FAIL -> FAIL` (ENV) | search: Search for 'test' returned no videos (FlareSolverr Failed: FlareSolverr error for https://hpjav.in/?s=test: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1)
- **hypnotube**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **ikisoda**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **javhdporn**: `FAIL -> FAIL` (PLAYBACK) | play: Site could not find a stream: Oh oh: No video found
- **javmoe**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **kissjav**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **mrsexe**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **netflav**: `FAIL -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **peachurnet**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (PeachUrNet: No videos found on this page)
- **perverzija**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **porndoe**: `FAIL -> FAIL` (ENV) | search: RuntimeError: FlareSolverr error for https://porndoe.com/search?keywords=test: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **pornkai**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **pornmd**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **porno365**: `FAIL -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **seaporn**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **sextb**: `FAIL -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **sxyprn**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **terebon**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **txxx**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **uflash**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xgirls**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xhamster**: `FAIL -> FAIL` (PLAYBACK) | play: Site could not find a stream: Oh Oh: No playable video found.
- **xlovecam**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xozilla**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **xsharings**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **javgg** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos
- **javgg** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **peekvids** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **peekvids** `search_play`: `SKIP -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **perverzija** `list`: `SKIP -> FAIL` (PARSER) | List returned no videos
- **sexyporn** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos
- **sexyporn** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **txxx** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
