# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 171` | `WARN 3` | `FAIL 30` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 173` | `WARN 2` | `FAIL 28` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `3`
- Resolved failures: `1`
- Persistent failures: `27`
- Site regressions: `4`
- Step regressions: `7`

## New Failures

- **kissjav**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **sexyporn**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xhamster**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh Oh: No video found.)

## Resolved Failures

- **pornslash**: `FAIL -> PASS`

## Persistent Failures

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
- **javmoe**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **mrsexe**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **netflav**: `FAIL -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **peachurnet**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (PeachUrNet: No videos found on this page)
- **perverzija**: `FAIL -> FAIL` (CODE) | play: IndexError: list index out of range
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **porno365**: `FAIL -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **seaporn**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **sextb**: `FAIL -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **sxyprn**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **terebon**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **txxx**: `FAIL -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **uflash**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xgirls**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xlovecam**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xsharings**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **kissjav** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **kissjav** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **pornmz** `play`: `PASS -> FAIL` (PLAYBACK) | Site could not find a stream: Oh oh: No video found
- **sexyporn** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos
- **sexyporn** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **xhamster** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh Oh: No video found.)
- **xhamster** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play

## Improvements

- **spankbang**: `SKIP -> PASS`
