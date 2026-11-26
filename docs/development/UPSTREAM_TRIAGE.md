# Upstream Triage Report

Generated: 2026-11-26
Pending commits: 94 (grouped into 94 items)

Run `python scripts/sync_manager.py` (interactive) to review/cherry-pick, or `python scripts/sync_manager.py --report` to regenerate this file.

## New Sites Available (0)

Sites touched by these commits don't exist in our fork yet. Candidates for new site modules.

_None._

## Needs Review (9)

Touches a site we have that isn't BeautifulSoup-migrated, or mentions playback/decrypt - worth reviewing for porting.

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| c8bf334a | `c8bf334a` | 3movs | - |  | 3Movs fixed pagination |
| cc8e0aab | `cc8e0aab` | 3movs | - |  | Add files via upload |
| #2056 | `b804dd77` | 3movs | - |  | 3movs #2056 |
| #2029 | `165b78cf` | perverzija | - | yes | perverzija playback & pervtube #2029 fixes #2053 |
| a6175792 | `a6175792` | camcaps, watcherotic | - |  | camcaps logo |
| ab89390f | `ab89390f` | camsoda | - |  | thumbnail_clean.py kodi 18 compatible final |
| 3896369f | `3896369f` | bongacams, cam4, camsoda, sinparty, stripchat | - |  | Refresh images fix |
| 7beaee0e | `7beaee0e` | amateurtv, bongacams, cam4, camsoda, chaturbate, naked, sinparty, streamate, stripchat | - |  | replaced the path to textures13.db with utils.TEXTURESDB |
| bcd41438 | `bcd41438` | allclassic, archivebate, blendporn, hdporn92, heroero, incesto69, javguru, onlyjerk, porndish, pornkai, terebon, trendyporn, tubxporn, xfreehd, youcrazyx, yrprno | - |  | Merge branch 'main' of https://github.com/dobbelina/repository.cumination |

## Likely Already Covered (20)

Only touches BeautifulSoup-migrated sites we already have - spot-check, likely skip.

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| #2043 | `cab8318a` | archivebate, terebon | - |  | terebon, archivebate fixes #2043 |
| ede00196 | `ede00196` | yespornvip | - |  | - YesPorn.vip fixed listing |
| #2058 | `261cd0f4` | yespornvip | - |  | YesPorn.vip  #2058 |
| 11ce5d81 | `11ce5d81` | aagmaal, aagmaalpro, xsharings | - |  | Various fixes |
| 32fa6d47 | `32fa6d47` | aagmaal, aagmaalpro, viralvideosporno, xsharings | - |  | "Don't ask for videohost" |
| 3b4714c1 | `3b4714c1` | watcherotic | - |  | watcherotic - fix thumbnails (Kodi 22) |
| f4efca1a | `f4efca1a` | watcherotic | - |  | watcherotic logo |
| 5005dc51 | `5005dc51` | homemoviestube | - |  | hitprn - pagination, gotopage, thumbnails |
| c0c9eb8c | `c0c9eb8c` | homemoviestube | - |  | Merge branch 'main' of https://github.com/dobbelina/repository.cumination |
| 492d3be6 | `492d3be6` | sextb | - |  | sextb listing |
| 1aaaf136 | `1aaaf136` | homemoviestube | - |  | pagination search results fix |
| #2046 | `a73847dc` | sextb | - |  | sextb fixes #2046 |
| e88c7f99 | `e88c7f99` | homemoviestube | - |  | Homemoviestube |
| 00ae5e09 | `00ae5e09` | beemtube, netflixporno | - |  | Netflixporno fixed |
| c0d96b76 | `c0d96b76` | rule34video | - |  | rule43video - caching for thumbnails |
| e4a56707 | `e4a56707` | watchporn | - |  | Add Studios entry to the WatchPorn main menu |
| 93941719 | `93941719` | xmoviesforyou | - |  | Xmoviesforyou fix |
| #2028 | `3c8ae660` | xmoviesforyou | - |  | Xmoviesforyou  #2028 |
| 218f6992 | `218f6992` | hdporn92 | - |  | Hdporn92 categories to channels |
| #2024 | `f14f9b23` | watchporn | - |  | watchporn - fixes #2024 |

## Auto-Skip (65)

No site module changes detected (changelog/icon/docs/version-bump-style commits).

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| 2319dfa9 | `2319dfa9` | - | - |  | utils - code cleanup |
| beece3f8 | `beece3f8` | - | - |  | Player menu ratings button |
| eb7ef229 | `eb7ef229` | - | - |  | Remove rating during internetstream |
| 5bb6558a | `5bb6558a` | - | - |  | Tiny change MusicVisualisation.xml |
| #2055 | `654fd676` | erogarga | - | yes | erogarga playback #2055 |
| e04a2859 | `e04a2859` | - | - |  | Add files via upload |
| 58bb72ec | `58bb72ec` | - | - |  | Artist - Album divider fix |
| 322a9248 | `322a9248` | - | - |  | Music player title fix |
| ca8100b4 | `ca8100b4` | - | - |  | Added kbps & channels to music player |
| af228b7b | `af228b7b` | - | - |  | switched places HDR image |
| 4edad015 | `4edad015` | - | - |  | Added fps.png |
| 55e9b1fe | `55e9b1fe` | - | - |  | Add files via upload |
| 649c6805 | `649c6805` | - | - |  | Added gradient 480, 540, 576 .png |
| 764a4372 | `764a4372` | - | - |  | changed letter-spacing png, 480, 540, 576 |
| aa4bc5a6 | `aa4bc5a6` | - | - |  | Updated 480, 540 .png |
| e995f53c | `e995f53c` | - | - |  | Changed , SD to 480, 540, 576 |
| 2b7f2e6e | `2b7f2e6e` | - | - |  | Added missing 8K.png |
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
