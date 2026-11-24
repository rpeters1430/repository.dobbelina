# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 173` | `WARN 2` | `FAIL 28` | `ERROR 0` | `SKIP 3`
- Previous: `PASS 170` | `WARN 3` | `FAIL 31` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `3`
- Resolved failures: `6`
- Persistent failures: `25`
- Site regressions: `4`
- Step regressions: `7`

## New Failures

- **eporner**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **hentaicity**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **pornslash**: `PASS -> FAIL` (CODE) | play: ValueError: No video stream found!

## Resolved Failures

- **anybunny**: `FAIL -> PASS`
- **kissjav**: `FAIL -> PASS`
- **porndoe**: `FAIL -> PASS`
- **pornmd**: `FAIL -> PASS`
- **tabootube**: `FAIL -> PASS`
- **xhamster**: `FAIL -> PASS`

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

- **eporner** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos
- **eporner** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **hentaicity** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos
- **hentaicity** `search_play`: `PASS -> FAIL` (UNKNOWN) | Search failed, so no search result to play
- **pornslash** `play`: `PASS -> FAIL` (CODE) | ValueError: No video stream found!
- **pornslash** `search_play`: `PASS -> FAIL` (CODE) | ValueError: No video stream found!
- **uflash** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos

## Improvements

- **avple**: `WARN -> PASS`
