# Site Health Delta

- Current report: `site_health_latest.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 164` | `WARN 3` | `FAIL 36` | `ERROR 0` | `SKIP 3`
- Previous: `PASS 192` | `WARN 5` | `FAIL 7` | `ERROR 0` | `SKIP 2`

## Delta Summary

- New failures: `32`
- Resolved failures: `3`
- Persistent failures: `4`
- Site regressions: `34`
- Step regressions: `36`

## New Failures

- **camhub**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **camwhoresbay**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (CamWhoresBay: No videos found on this page)
- **cumlouder**: `PASS -> FAIL` (ENV) | search: RuntimeError: FlareSolverr error for https://www.cumlouder.com/search/?q=test: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **ecamrips**: `PASS -> FAIL` (PARSER) | search: Search for 'meybaldini' returned no videos (Oh oh: It looks like this website is down.)
- **freshporno**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **hentaidude**: `PASS -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **hpjav**: `PASS -> FAIL` (ENV) | search: Search for 'test' returned no videos (FlareSolverr Failed: FlareSolverr error for https://hpjav.in/?s=test: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1)
- **hypnotube**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **ikisoda**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **javgg**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **javhdporn**: `PASS -> FAIL` (PLAYBACK) | play: Site could not find a stream: Oh oh: No video found
- **javmoe**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **kissjav**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **mangoporn**: `PASS -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://mangoporn.net/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **mrsexe**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **netflav**: `PASS -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **peachurnet**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (PeachUrNet: No videos found on this page)
- **peekvids**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **perverzija**: `WARN -> FAIL` (CODE) | play: IndexError: list index out of range
- **porno365**: `PASS -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **porntrex**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: No videos found)
- **seaporn**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **sexyporn**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **sxyprn**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **terebon**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **tokyomotion**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos (notify: )
- **txxx**: `PASS -> FAIL` (PLAYBACK) | play: Play function executed but no playback URL captured (no notifications)
- **uflash**: `PASS -> FAIL` (PLAYBACK) | play: Site could not find a stream: Oh oh: Couldn't find video source
- **whoreshub**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xgirls**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xhamster**: `PASS -> FAIL` (PLAYBACK) | play: Site could not find a stream: Oh Oh: No playable video found.
- **xlovecam**: `PASS -> FAIL` (PARSER) | search: Search for 'test' returned no videos

## Resolved Failures

- **hitprn**: `FAIL -> PASS`
- **watchporn**: `FAIL -> PASS`
- **watchpornx**: `FAIL -> PASS`

## Persistent Failures

- **hentai2w**: `FAIL -> FAIL` (PARSER) | list: List returned no videos
- **porn4k**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://porn4k.to/page/1/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **xsharings**: `FAIL -> FAIL` (PARSER) | search: Search for 'test' returned no videos
- **xtapesla**: `FAIL -> FAIL` (ENV) | main: RuntimeError: FlareSolverr error for https://xtapes.la/?display=tube&filtre=date: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1

## Step Regressions

- **camhub** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **camwhoresbay** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (CamWhoresBay: No videos found on this page)
- **cumlouder** `search`: `SKIP -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://www.cumlouder.com/search/?q=test: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **ecamrips** `search`: `PASS -> FAIL` (PARSER) | Search for 'meybaldini' returned no videos (Oh oh: It looks like this website is down.)
- **freshporno** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **hentai2w** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos
- **hentaidude** `play`: `SKIP -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **hobbyporn** `play`: `SKIP -> FAIL` (PARSER) | Site could not find a stream: Oh Oh: No Videos found
- **hpjav** `search`: `SKIP -> FAIL` (ENV) | Search for 'test' returned no videos (FlareSolverr Failed: FlareSolverr error for https://hpjav.in/?s=test: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1)
- **hypnotube** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos
- **ikisoda** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos
- **javgg** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **javhdporn** `play`: `SKIP -> FAIL` (PLAYBACK) | Site could not find a stream: Oh oh: No video found
- **javmoe** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos
- **kissjav** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **mangoporn** `main`: `PASS -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://mangoporn.net/: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **mrsexe** `play`: `SKIP -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **mrsexe** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos
- **netflav** `play`: `SKIP -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **peachurnet** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos (PeachUrNet: No videos found on this page)
- **peekvids** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like the page does not exist.)
- **porno365** `play`: `SKIP -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **porntrex** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: No videos found)
- **seaporn** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **sextb** `categories`: `SKIP -> FAIL` (ENV) | RuntimeError: FlareSolverr error for https://sextb.net/genres: Timed out after 35s. Check if FlareSolverr is running at http://localhost:8191/v1
- **sexyporn** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos
- **sxyprn** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like this website is down.)
- **terebon** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos (Oh oh: It looks like this website is too slow.)
- **tokyomotion** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos (notify: )
- **txxx** `play`: `SKIP -> FAIL` (PLAYBACK) | Play function executed but no playback URL captured (no notifications)
- **uflash** `play`: `SKIP -> FAIL` (PLAYBACK) | Site could not find a stream: Oh oh: Couldn't find video source
- **whoreshub** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos
- **xgirls** `search`: `PASS -> FAIL` (PARSER) | Search for 'test' returned no videos
- **xhamster** `play`: `SKIP -> FAIL` (PLAYBACK) | Site could not find a stream: Oh Oh: No playable video found.
- **xlovecam** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos
- **xsharings** `search`: `SKIP -> FAIL` (PARSER) | Search for 'test' returned no videos

## Improvements

- **nonktube**: `WARN -> PASS`
- **xozilla**: `WARN -> PASS`
