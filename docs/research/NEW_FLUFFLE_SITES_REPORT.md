# New Fluffle Sites Discovery & Validation Report

**101** brand new sites found on Fluffle that are not currently implemented or tracked.
Tested **20** of them.

Validation Status Summary: FAIL=7, LOW=5, PROMISING=6, REVIEW=2

## Tested Sites Table

| Status | Site | Category | HTTP | Links | Playback | Sample Playback | Notes |
| :--- | :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| FAIL | **chuyenphim18**<br>https://chuyenphim18.site | Adult Movies / Grindhouse |  | 0 | 0 | 0 | request error: RequestException: Failed to fetch https://chuyenphim18.site |
| PROMISING | **Film-Adult**<br>https://hd.film-adult.com/en/ | Adult Movies / Grindhouse | 200 | 39 | 1 | 3 | PORN MOVIES ONLINE \| Watch porn movies and videos completely free! |
| FAIL | **PandaMovies**<br>https://pandamovies.pw/ | Adult Movies / Grindhouse | 522 | 0 | 0 | 0 | HTTP 522; no likely same-site video links found |
| LOW | **Pinkueiga**<br>https://pinkueiga.net/ | Adult Movies / Grindhouse | 200 | 0 | 0 | 0 | no likely same-site video links found |
| PROMISING | **Sex Film**<br>https://en.sex-film.biz/ | Adult Movies / Grindhouse | 200 | 31 | 1 | 3 | Porn Movies and Videos Online 18+ \| Sex-Film |
| PROMISING | **VintageClassix**<br>http://www.vintageclassix.com/ | Adult Movies / Grindhouse | 200 | 30 | 1 | 2 | Vintage Classix |
| PROMISING | **91rb**<br>https://www.91rb.net/ | Asian / JAV | 200 | 34 | 0 | 7 | 91热爆,91视频,热爆视频,91自拍,亚洲火爆视频在线观看 |
| LOW | **AsianGirl**<br>https://asiangirl.porn/ | Asian / JAV | 200 | 0 | 1 | 0 | no likely same-site video links found |
| FAIL | **AVHAI**<br>https://avsea.sbs | Asian / JAV |  | 0 | 0 | 0 | request error: RequestException: Failed to fetch https://avsea.sbs |
| FAIL | **JavFun**<br>https://en.javfun.me/ | Asian / JAV | 200 | 24 | 1 | 4 | redirected to different host: en.javfun.me |
| PROMISING | **KRX18**<br>https://krx18.com/ | Asian / JAV | 200 | 56 | 3 | 3 | Watch Erotic Adult Movies 18+ Online Free – Mov18plus Watch Free Erotic Movies 18+ Japanese Movies 18+ JavHD Porn HD free movie , EROTIC MOVIE ,Adutl Movies – Erotic Sex. , erotica movie. Watch cat 3 movie online. Erotica movies |
| LOW | **rou.video**<br>https://rou.video/ | Asian / JAV | 200 | 0 | 0 | 0 | no likely same-site video links found |
| FAIL | **WatchFreeJAV**<br>https://s26.watchfreejavonline.co/ | Asian / JAV | 200 | 0 | 3 | 0 | redirected to different host: s26.watchfreejavonline.co; no likely same-site video links found |
| FAIL | **Bestcam**<br>https://bestcam.tv/ | Cam Models | 403 | 0 | 1 | 0 | HTTP 403; anti-bot or access challenge text detected; no likely same-site video links found |
| LOW | **CamGirlFinder**<br>https://camgirlfinder.net/ | Cam Models | 200 | 0 | 0 | 0 | no likely same-site video links found |
| FAIL | **CamSeek.TV**<br>https://camseek.tv/ | Cam Models | 522 | 0 | 0 | 0 | HTTP 522; no likely same-site video links found |
| REVIEW | **CamSmut**<br>https://camsmut.com/ | Cam Models | 200 | 100 | 0 | 0 | sample video HTTP 404 |
| LOW | **Chaturflix**<br>https://chaturflix.cam/ | Cam Models | 200 | 0 | 1 | 0 | no likely same-site video links found |
| REVIEW | **CumCams**<br>https://cumcams.cc/ | Cam Models | 200 | 36 | 0 | 0 | CumCams — Free Chaturbate and Stripchat Archive |
| PROMISING | **eCamRips**<br>https://www.ecamrips.com/en/ | Cam Models | 200 | 32 | 1 | 1 | Webcam: Webcam Show web cam Ecamrips 1 |

## Promising New Candidates
These sites are highly recommended for implementation. They have same-site video links and direct playback signals (HTML5 video, players, iFrames, or stream formats).

- **Film-Adult** (Adult Movies / Grindhouse) - Links found: 39, Playback signals: 3 (Sample URL: https://hd.film-adult.com/en/168-pirates-2-stagnettis-revenge.html)
- **Sex Film** (Adult Movies / Grindhouse) - Links found: 31, Playback signals: 3 (Sample URL: https://en.sex-film.biz/11194-my-first-time.html)
- **VintageClassix** (Adult Movies / Grindhouse) - Links found: 30, Playback signals: 2 (Sample URL: http://www.vintageclassix.com/2021/03/reups-only-here_73.html)
- **91rb** (Asian / JAV) - Links found: 34, Playback signals: 7 (Sample URL: https://www.91rb.net/videos/134899/p-29/)
- **KRX18** (Asian / JAV) - Links found: 56, Playback signals: 3 (Sample URL: https://krx18.com/movies/594692/)
- **eCamRips** (Cam Models) - Links found: 32, Playback signals: 1 (Sample URL: https://www.ecamrips.com/show-cam-sex-movies/2157594-anabel054-chaturbate-webcam-rip-20260926-005545.html)

### Suggested Additions for docs/development/NEW_SITES.md
Copy and paste the promising entries below into your tracking file.

| Site | Category | Difficulty | Status | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Film-Adult** | Adult Movies / Grindhouse | Medium | [ ] | New Fluffle discovery. 39 video links. Sample playback signals: 3. |
| **Sex Film** | Adult Movies / Grindhouse | Medium | [ ] | New Fluffle discovery. 31 video links. Sample playback signals: 3. |
| **VintageClassix** | Adult Movies / Grindhouse | Medium | [ ] | New Fluffle discovery. 30 video links. Sample playback signals: 2. |
| **91rb** | Asian / JAV | Medium | [ ] | New Fluffle discovery. 34 video links. Sample playback signals: 7. |
| **KRX18** | Asian / JAV | Medium | [ ] | New Fluffle discovery. 56 video links. Sample playback signals: 3. |
| **eCamRips** | Cam Models | Medium | [ ] | New Fluffle discovery. 32 video links. Sample playback signals: 1. |
