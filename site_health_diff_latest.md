# Site Health Delta

- Current report: `live_smoke_20260424_070432.json`
- Previous report: `live_smoke_latest.json`

## Snapshot

- Current: `PASS 149` | `WARN 2` | `FAIL 19` | `ERROR 0` | `SKIP 0`
- Previous: `PASS 168` | `WARN 1` | `FAIL 1` | `ERROR 0` | `SKIP 0`

## Delta Summary

- New failures: `18`
- Resolved failures: `0`
- Persistent failures: `1`
- Site regressions: `20`
- Step regressions: `59`

## New Failures

- **erogarga**: `PASS -> FAIL` (PLAYBACK) | list: RuntimeError: FlareSolverr error for https://www.erogarga.com/page/2/?filter=latest: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **familypornhd**: `WARN -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://familypornhd.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **freepornvideos**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://www.freepornvideos.xxx/latest-updates/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **hdporn92**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://hdporn92.com/?filter=latest: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **heavyr**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://www.heavy-r.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **javgg**: `PASS -> FAIL` (PLAYBACK) | list: RuntimeError: FlareSolverr error for https://javgg.co/trending/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **javhdporn**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://www4.javhdporn.net/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **jizzbunker**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://jizzbunker.com/straight/trending: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **longvideos**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://www.wow.xxx/latest-updates/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **perverzija**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://tube.perverzija.com/page/1/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **pmvhaven**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://pmvhaven.com/api/videos?limit=32&sort=-releaseDate&page=1&skipCount=true&tagMode=OR&expandTags=false: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **porndish**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://www.porndish.com/page/1/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **rlc**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://reallifecam.to/videos?o=mr: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **spankbang**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://spankbang.com/new_videos/1/?o=new: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **supjav**: `PASS -> FAIL` (NETWORK) | Site process timed out after 140s
- **thepornarea**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://thepornarea.com/latest-updates/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **whereismyporn**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://whereismyporn.com/page/1: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **xmoviesforyou**: `PASS -> FAIL` (PLAYBACK) | main: RuntimeError: FlareSolverr error for https://xmoviesforyou.com/page/1: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1

## Persistent Failures

- **josporn**: `FAIL -> FAIL` (NETWORK) | list: List URL unavailable in harness (HTTP 503)

## Step Regressions

- **erogarga** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.erogarga.com/page/2/?filter=latest: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **erogarga** `play`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.erogarga.com/trofey-2025/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **erogarga** `search`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.erogarga.com/test: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **familypornhd** `categories`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://familypornhd.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **familypornhd** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://familypornhd.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **familypornhd** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://familypornhd.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **familypornhd** `search`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://familypornhd.com/test: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **freepornvideos** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.freepornvideos.xxx/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **freepornvideos** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.freepornvideos.xxx/latest-updates/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **freepornvideos** `search`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.freepornvideos.xxx/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **hdporn92** `categories`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://hdporn92.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **hdporn92** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://hdporn92.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **hdporn92** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://hdporn92.com/?filter=latest: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **hdporn92** `search`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://hdporn92.com/test: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **heavyr** `categories`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.heavy-r.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **heavyr** `list`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.heavy-r.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **heavyr** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.heavy-r.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **heavyr** `search`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.heavy-r.com/index.php?page=videos&section=search&query=test: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **javgg** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://javgg.co/trending/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **javgg** `search`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://javgg.co/test: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **javhdporn** `categories`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www4.javhdporn.net/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **javhdporn** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www4.javhdporn.net/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **javhdporn** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www4.javhdporn.net/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **javhdporn** `search`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www4.javhdporn.net/test/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **jizzbunker** `categories`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://jizzbunker.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **jizzbunker** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://jizzbunker.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **jizzbunker** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://jizzbunker.com/straight/trending: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **jizzbunker** `search`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://jizzbunker.com/searching/?queryString=test: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **longvideos** `categories`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.wow.xxx/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **longvideos** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.wow.xxx/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **longvideos** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.wow.xxx/latest-updates/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **longvideos** `search`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.wow.xxx/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **perverzija** `list`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://tube.perverzija.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **perverzija** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://tube.perverzija.com/page/1/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **perverzija** `search`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://tube.perverzija.com/test: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **pmvhaven** `list`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://pmvhaven.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **pmvhaven** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://pmvhaven.com/api/videos?limit=32&sort=-releaseDate&page=1&skipCount=true&tagMode=OR&expandTags=false: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **pmvhaven** `search`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://pmvhaven.com/test: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **porndish** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.porndish.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **porndish** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://www.porndish.com/page/1/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **pornhoarder** `play`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://pornhoarder.net/player_t.php?video=REV1QVptdHhWeHpVc2ViQjJKMThBa1hhbjBYcEV4WXJIVTg3Yk5RekNtdz0=: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **rlc** `categories`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://reallifecam.to/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **rlc** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://reallifecam.to/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **rlc** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://reallifecam.to/videos?o=mr: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **rlc** `search`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://reallifecam.to/test: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **spankbang** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://spankbang.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **spankbang** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://spankbang.com/new_videos/1/?o=new: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **spankbang** `search`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://spankbang.com/test/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **speedporn** `categories`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://speedporn.net/categories/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **thepornarea** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://thepornarea.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **thepornarea** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://thepornarea.com/latest-updates/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **thepornarea** `search`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://thepornarea.com/test: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **whereismyporn** `list`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://whereismyporn.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **whereismyporn** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://whereismyporn.com/page/1: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **whereismyporn** `search`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://whereismyporn.com/test: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **xmoviesforyou** `categories`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://xmoviesforyou.com/categories: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **xmoviesforyou** `list`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://xmoviesforyou.com/: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **xmoviesforyou** `main`: `PASS -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://xmoviesforyou.com/page/1: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
- **xmoviesforyou** `search`: `SKIP -> FAIL` (PLAYBACK) | RuntimeError: FlareSolverr error for https://xmoviesforyou.com/search?q=test: Expecting value: line 1 column 1 (char 0). Check if FlareSolverr is running at http://localhost:8191/v1
