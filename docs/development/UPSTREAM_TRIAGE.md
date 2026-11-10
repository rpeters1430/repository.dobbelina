# Upstream Triage Report

Generated: 2026-11-09
Pending commits: 80 (grouped into 80 items)

Run `python scripts/sync_manager.py` (interactive) to review/cherry-pick, or `python scripts/sync_manager.py --report` to regenerate this file.

## New Sites Available (1)

Sites touched by these commits don't exist in our fork yet. Candidates for new site modules.

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| #2020 | `77adfdd7` | watchpornx | watchpornx |  | Watchpornx to replace Netflixporno #2020 |

## Needs Review (6)

Touches a site we have that isn't BeautifulSoup-migrated, or mentions playback/decrypt - worth reviewing for porting.

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| a6175792 | `a6175792` | camcaps, watcherotic | - |  | camcaps logo |
| ab89390f | `ab89390f` | camsoda | - |  | thumbnail_clean.py kodi 18 compatible final |
| 3896369f | `3896369f` | bongacams, cam4, camsoda, sinparty, stripchat | - |  | Refresh images fix |
| 7beaee0e | `7beaee0e` | amateurtv, bongacams, cam4, camsoda, chaturbate, naked, sinparty, streamate, stripchat | - |  | replaced the path to textures13.db with utils.TEXTURESDB |
| #2027 | `0763b536` | beeg, xmoviesforyou | - |  | beeg - fixes #2027 |
| bcd41438 | `bcd41438` | allclassic, archivebate, blendporn, hdporn92, heroero, incesto69, javguru, onlyjerk, porndish, pornkai, terebon, trendyporn, tubxporn, xfreehd, youcrazyx, yrprno | - |  | Merge branch 'main' of https://github.com/dobbelina/repository.cumination |

## Likely Already Covered (23)

Only touches BeautifulSoup-migrated sites we already have - spot-check, likely skip.

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| 3b4714c1 | `3b4714c1` | watcherotic | - |  | watcherotic - fix thumbnails (Kodi 22) |
| f4efca1a | `f4efca1a` | watcherotic | - |  | watcherotic logo |
| 5a30e43f | `5a30e43f` | tubxporn | - |  | tubxporn domain |
| 5005dc51 | `5005dc51` | homemoviestube | - |  | hitprn - pagination, gotopage, thumbnails |
| c0c9eb8c | `c0c9eb8c` | homemoviestube | - |  | Merge branch 'main' of https://github.com/dobbelina/repository.cumination |
| 492d3be6 | `492d3be6` | sextb | - |  | sextb listing |
| 1aaaf136 | `1aaaf136` | homemoviestube | - |  | pagination search results fix |
| #2046 | `a73847dc` | sextb | - |  | sextb fixes #2046 |
| 543334e2 | `543334e2` | hitprn | - |  | Hitprn added Tags |
| e88c7f99 | `e88c7f99` | homemoviestube | - |  | Homemoviestube |
| #2045 | `698672e6` | 85po | - |  | 85po fixes #2045 |
| #2038 | `c4e4f129` | rule34video | - |  | rule34 thumnails fix for Kodi21 #2038 |
| 17f99901 | `17f99901` | netflixporno, watchpornx | - |  |  Watchpornx replaces Netflixporno |
| 00ae5e09 | `00ae5e09` | beemtube, netflixporno | - |  | Netflixporno fixed |
| c0d96b76 | `c0d96b76` | rule34video | - |  | rule43video - caching for thumbnails |
| #2035 | `7161b205` | speedporn | - |  | "Don't ask for video host" setting - #2035 |
| #2026 | `2a9f5737` | watchporn | - |  | watchporn studios  - fix thumbnails #2026 |
| ae861f3d | `ae861f3d` | watchporn | - |  | Add Studios entry to the WatchPorn main menu |
| e4a56707 | `e4a56707` | watchporn | - |  | Add Studios entry to the WatchPorn main menu |
| 93941719 | `93941719` | xmoviesforyou | - |  | Xmoviesforyou fix |
| #2028 | `3c8ae660` | xmoviesforyou | - |  | Xmoviesforyou  #2028 |
| 218f6992 | `218f6992` | hdporn92 | - |  | Hdporn92 categories to channels |
| #2024 | `f14f9b23` | watchporn | - |  | watchporn - fixes #2024 |

## Auto-Skip (50)

No site module changes detected (changelog/icon/docs/version-bump-style commits).

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| 7f3ee13f | `7f3ee13f` | - | - |  | Update av1.png |
| cb353344 | `cb353344` | - | - |  | Update av1.png |
| 4c60679b | `4c60679b` | - | - |  | Confluence Special |
| ffb60e7c | `ffb60e7c` | - | - |  | Confluence Special |
| 61e1578a | `61e1578a` | - | - |  | Final code cleanup |
| 27a6cf8a | `27a6cf8a` | - | - |  | ListItem.VideoCodec fix |
| 43274ee4 | `43274ee4` | avjoy | - |  | avjoy logo |
| da527674 | `da527674` | - | - |  | Fixed inconsistent library xvid listing |
| 2cc91d23 | `2cc91d23` | - | - |  | Added back VideoPlayerVideoCodecTexture |
| 516f08b1 | `516f08b1` | - | - |  | Added rv40 codec image |
| 50259be8 | `50259be8` | - | - |  | Library listing fix |
| 2c615ec0 | `2c615ec0` | - | - |  | Audio Codec fix for library |
| 6301fee4 | `6301fee4` | - | - |  | VideoPlayer.AudioLanguage string empty now showing |
| 0cb0b249 | `0cb0b249` | - | - |  | Codec images fixed |
| d3dc0c66 | `d3dc0c66` | - | - |  | kodi 22 compatible confluence skin v5.0.9 |
| 48a8e956 | `48a8e956` | - | - |  | kodi 22 compatible confluence skin v5.0.9 |
| a8f95ee2 | `a8f95ee2` | - | - |  | OptiKlean added repo info to addon.xml |
| d125966b | `d125966b` | - | - |  | OptiKlean Translated log writing to English |
| #2041 | `16e8bba8` | wowxxx | - | yes | wowxxx - fix playback #2041 |
| 1ede8186 | `1ede8186` | - | - |  | OptiKlean small language correction |
| 0ed6a5c2 | `0ed6a5c2` | - | - |  | Update bug_report.yml |
| e82cb8ff | `e82cb8ff` | - | - |  | program.optiklean-2.3.1 |
| 08ed5d5e | `08ed5d5e` | - | - |  | Optiklean v2.3.1 |
| edf4ef03 | `edf4ef03` | - | - |  | favorites: next page restore |
| bf97714f | `bf97714f` | - | - |  | Confluence fanart fix |
| 59c0f05f | `59c0f05f` | - | - |  | thumbnail_clean.py kodi 18 compatible |
| dbd54f25 | `dbd54f25` | - | - |  | default.py kodi 18 compatible |
| ab83e567 | `ab83e567` | - | - |  | thumbnail_clean.py kodi 18 compatible |
| 6299c65d | `6299c65d` | allpornstream | - |  | AllPornStream fixed Search |
| a7feb886 | `a7feb886` | allpornstream | - |  | fixed malplaced forward slash |
| 1310f2f0 | `1310f2f0` | allpornstream | - |  | Allpornstream fixed Search |
| #2025 | `1842d9ba` | allclassic | - | yes | allclassic playback  #2025 |
| d43529a3 | `d43529a3` | - | - |  | addon images compressed |
| 5b662663 | `5b662663` | - | - |  | Update addon images |
| dd18b303 | `dd18b303` | - | - |  | update addon images |
| 6bdfb266 | `6bdfb266` | - | - |  | Update cum-favorites.png |
| 28dd994c | `28dd994c` | - | - |  | Update cum-favorites.png |
| 09ac45c8 | `09ac45c8` | - | - |  | Update cum-favorites.png |
| 4ca83d8b | `4ca83d8b` | - | - |  | Added thumbnails for addon start screen |
| 4ccf686f | `4ccf686f` | - | - |  | Update changelog.txt |
| 97d85cde | `97d85cde` | - | - |  | Thumbnail size reduction + clear cache addition |
| bd9ea3be | `bd9ea3be` | - | - |  | remove thumbnail addon |
| 9a8baa69 | `9a8baa69` | - | - |  | update thumbnail reset script |
| 2c806231 | `2c806231` | - | - |  | Update addon.xml |
| d804e400 | `d804e400` | - | - |  | Update thumbnail reset script |
| 8d81874d | `8d81874d` | - | - |  | Update addons.xml.md5 |
| d1297655 | `d1297655` | - | - |  | Update addons.xml |
| d2ef146e | `d2ef146e` | - | - |  | removed duplicate favorites thumbnail |
| e69a00aa | `e69a00aa` | - | - |  | refresh thumbnails addon |
| 9d13f006 | `9d13f006` | - | - |  | addon images added text shadow |
