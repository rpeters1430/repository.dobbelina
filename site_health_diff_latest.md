# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 170` | `WARN 3` | `FAIL 31` | `ERROR 0` | `SKIP 2`
- Previous: `PASS 164` | `WARN 3` | `FAIL 36` | `ERROR 0` | `SKIP 3`

## Delta Summary

- New failures: `5`
- Resolved failures: `10`
- Persistent failures: `26`
- Site regressions: `6`
- Step regressions: `12`

## New Failures

- **anybunny**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **porndoe**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **pornmd**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **sextb**: `WARN -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **tabootube**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is down.)

## Resolved Failures

- **camhub**: `FAIL -> PASS`
- **camwhoresbay**: `FAIL -> PASS`
- **ecamrips**: `FAIL -> PASS`
- **javgg**: `FAIL -> PASS`
- **mangoporn**: `FAIL -> PASS`
- **peekvids**: `FAIL -> PASS`
- **porntrex**: `FAIL -> PASS`
- **sexyporn**: `FAIL -> PASS`
- **tokyomotion**: `FAIL -> PASS`
- **whoreshub**: `FAIL -> PASS`

## Persistent Failures

- **cumlouder**: `FAIL -> FAIL` (ENV) | search: RuntimeError: FlareSolverr error for https://www.cumlouder.com/search/?q=test: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **freshporno**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **hentai2w**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
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
- **sxyprn**: `FAIL -> FAIL` (NETWORK) | Site process timed out after 140s
- **terebon**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **txxx**: `FAIL -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **uflash**: `FAIL -> FAIL` (PLAYBACK) | play: Site could not find a stream: Oh oh: Couldn't find video source
- **xgirls**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xhamster**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh Oh: No video found.)
- **xlovecam**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xsharings**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **anybunny** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **anybunny** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **avple** `play`: `SKIP -> FAIL` (PLAYBACK) | Site could not find a stream: Error: Unable to find video source
- **porndoe** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos
- **porndoe** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **pornmd** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos
- **pornmd** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **sextb** `play`: `SKIP -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **sextb** `search_play`: `SKIP -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **tabootube** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **tabootube** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **xhamster** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh Oh: No video found.)

## Improvements

- **spankbang**: `SKIP -> PASS`
