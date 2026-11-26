# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 167` | `WARN 2` | `FAIL 35` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 171` | `WARN 3` | `FAIL 30` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `6`
- Resolved failures: `1`
- Persistent failures: `29`
- Site regressions: `6`
- Step regressions: `12`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **porndoe**: `PASS -> FAIL` (ENV) | search: RuntimeError: FlareSolverr error for https://porndoe.com/search?keywords=test: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **pornkai**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **pornmd**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xnxx**: `PASS -> FAIL` (PLAYBACK) | play: Site could not find a stream: Oh oh: Couldn't find a playable link
- **xozilla**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)

## Resolved Failures

- **sexyporn**: `FAIL -> PASS`

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
- **javmoe**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **kissjav**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
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
- **xhamster**: `FAIL -> FAIL` (PLAYBACK) | play: Site could not find a stream: Oh Oh: No playable video found.
- **xlovecam**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xsharings**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **analdin** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **analdin** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **porndoe** `search`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://porndoe.com/search?keywords=test: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **pornkai** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **pornkai** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **pornmd** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos
- **pornmd** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **xhamster** `play`: `SKIP -> FAIL` (PLAYBACK) | Site could not find a stream: Oh Oh: No playable video found.
- **xnxx** `play`: `PASS -> FAIL` (PLAYBACK) | Site could not find a stream: Oh oh: Couldn't find a playable link
- **xnxx** `search_play`: `PASS -> FAIL` (PLAYBACK) | Site could not find a stream: Oh oh: Couldn't find a playable link
- **xozilla** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **xozilla** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play

## Improvements

- **pornmz**: `WARN -> PASS`
