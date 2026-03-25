# Site Health Delta

- Current report: `live_smoke_20260325_064920.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 154` | `WARN 5` | `FAIL 7` | `ERROR 0` | `SKIP 1`
- Previous: `PASS 145` | `WARN 2` | `FAIL 19` | `ERROR 0` | `SKIP 1`

## Delta Summary

- New failures: `5`
- Resolved failures: `17`
- Persistent failures: `2`
- Site regressions: `6`
- Step regressions: `9`

## New Failures

- **analdin**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **eporner**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **porndoe**: `PASS -> FAIL` (PARSER) | list: List returned no videos
- **speedporn**: `WARN -> FAIL` (NETWORK) | Site process timed out after 140s
- **xhamster**: `PASS -> FAIL` (CODE) | main: KeyError: 'videoListProps'

## Resolved Failures

- **aagmaalpro**: `FAIL -> PASS`
- **erogarga**: `FAIL -> PASS`
- **familypornhd**: `FAIL -> PASS`
- **freepornvideos**: `FAIL -> PASS`
- **heavyr**: `FAIL -> WARN`
- **hentaidude**: `FAIL -> PASS`
- **javgg**: `FAIL -> PASS`
- **javhdporn**: `FAIL -> WARN`
- **jizzbunker**: `FAIL -> PASS`
- **perverzija**: `FAIL -> PASS`
- **pmvhaven**: `FAIL -> PASS`
- **porndish**: `FAIL -> PASS`
- **rlc**: `FAIL -> PASS`
- **spankbang**: `FAIL -> PASS`
- **thepornarea**: `FAIL -> PASS`
- **wimp**: `FAIL -> PASS`
- **xmoviesforyou**: `FAIL -> WARN`

## Persistent Failures

- **hdporn92**: `FAIL -> FAIL` (NETWORK) | Site process timed out after 140s
- **tubxporn**: `FAIL -> FAIL` (BLOCKED) | main: RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177442

## Step Regressions

- **analdin** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **eporner** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **eroticage** `play`: `PASS -> FAIL` (CODE) | JSONDecodeError: Expecting value: line 1 column 1 (char 0)
- **heavyr** `play`: `SKIP -> FAIL` (BLOCKED) | RuntimeError: FlareSolverr error (try 3/3): FlareSolverr server error (HTTP 500): {"status": "error", "message": "Error: Error solving the challenge. Cloudflare has blocked this request. Probably your IP is banned for this site, check in your web browser.", "startTimestamp": 177442
- **javhdporn** `play`: `SKIP -> FAIL` (BLOCKED) | HTTPError: HTTP Error 403: Forbidden
- **porndoe** `list`: `PASS -> FAIL` (PARSER) | List returned no videos
- **xhamster** `list`: `PASS -> FAIL` (CODE) | KeyError: 'videoListProps'
- **xhamster** `main`: `PASS -> FAIL` (CODE) | KeyError: 'videoListProps'
- **xhamster** `search`: `SKIP -> FAIL` (CODE) | KeyError: 'videoListProps'
