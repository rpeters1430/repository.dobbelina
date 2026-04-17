# Site Categories Design

**Date:** 2026-04-17
**Status:** Approved

## Goal

Make it easier for users to find sites by type. The addon has ~155 sites and the existing "Browse by Category" feature is wired up but only ~28 sites have categories assigned, leaving most of the list uncategorized.

## Decisions

- **7 broad categories** (not fine-grained — Kodi benefits from fewer top-level choices)
- **One category per site** (no duplication across categories)
- **Existing site logos as category icons** (zero new assets needed; each category shows a familiar logo thumbnail)

## Category Taxonomy

| Category | Representative Icon | Sites (approx) |
|---|---|---|
| Video Tubes | `pornhub.png` | ~95 |
| Cams & Live | `chaturbate.png` | ~12 |
| JAV & Asian | `javmoe.png` | ~18 |
| Hentai & Anime | `hanime.png` | ~7 |
| Amateur & Social | `erome.png` | ~11 |
| Specialty | `trannyteca.png` | ~17 |
| Aggregators | `archivebate.png` | ~4 |

**Consolidations from existing category strings:**
- `"JAV"` → `"JAV & Asian"`
- `"Cam Models"` → `"Cams & Live"`
- `"Hentai"` → `"Hentai & Anime"`
- `"Social / Amateur"` → `"Amateur & Social"`
- `"Leaks"` → absorbed into `"Amateur & Social"`
- `"VR"` → absorbed into `"Specialty"`

## Site-to-Category Mapping

### Video Tubes
`6xtube, absoluporn, analdin, anybunny, anysex, ask4porn, beeg, beemtube, blendporn, cumlouder, drtuber, eporner, foxnxx, freepornvideos, freeomovie, freshporno, fullporner, fullxcinema, fyxxr, hdporn, hdporn92, heavyr, heroero, hitprn, hornyfap, hqporner, jizzbunker, josporn, justfullporn, justporn, longvideos, motherless, mrsexe, naked, neporn, netfapx, netflixporno, nltubes, nonktube, okxxx, pimpbunny, playhdporn, porndig, porndish, pornditt, porndoe, pornez, porngo, pornhat, pornhd3x, pornhits, pornhoarder, pornhub, pornkai, pornmz, porno1hu, porno365, pornone, pornroom, porntn, porntrex, pornxp, premiumporn, redtube, allclassic, sextb, sexyporn, someporn, speedporn, sunporno, superporn, sxyprn, thepornarea, tnaflix, tube8, tubxporn, txxx, uflash, vaginanl, vipporns, viralvideosporno, watchporn, whereismyporn, whoreshub, xfreehd, xhamster, xmegadrive, xmoviesforyou, xnxx, xozilla, xtheatre, xxdbx, xxxtube, xvideos, youcrazyx, youjizz, youporn, yrprno`

### Cams & Live
`amateurtv, bongacams, cam4, camsoda, chaturbate, cloudbate, lemoncams, myfreecams, paradisehill, reallifecam, streamate, stripchat`

### JAV & Asian
`85po, avple, hpjav, japteenx, javbangers, javgg, javguru, javhdporn, javmoe, javseen, kissjav, missav, netflav, noodlemagazine, seaporn, supjav, terebon, tokyomotion`

### Hentai & Anime
`animeidhentai, hanime, hentai-moon, hentaidude, hentaihavenco, hentaistream, rule34video`

### Amateur & Social
`camwhoresbay, erome, hobbyporn, homemoviestube, hotleak, livecamrips, naughtyblog, thothub, watchmdh, xsharings, xxthots`

### Specialty
`aagmaal, aagmaalpro, celebsroulette, eroticage, erogarga, eroticmv, familypornhd, freeuseporn, peachurnet, perverzija, pmvhaven, porn4k, taboofantazy, tabootube, theyarehuge, trannyteca, watcherotic`

### Aggregators
`archivebate, awmnet, peekvids, playvids`

## Code Changes

### 1. `default.py` — update `category_list()`

Add a `CATEGORY_ICONS` dict mapping each category string to an existing image path via `basics.cum_image()`. Pass the mapped icon to `url_dispatcher.add_dir()` instead of the current hardcoded `cum-sites.png`.

```python
CATEGORY_ICONS = {
    "Video Tubes":      basics.cum_image("pornhub.png"),
    "Cams & Live":      basics.cum_image("chaturbate.png"),
    "JAV & Asian":      basics.cum_image("javmoe.png"),
    "Hentai & Anime":   basics.cum_image("hanime.png"),
    "Amateur & Social": basics.cum_image("erome.png"),
    "Specialty":        basics.cum_image("trannyteca.png"),
    "Aggregators":      basics.cum_image("archivebate.png"),
}
```

Fall back to `cum-sites.png` for any category not in the dict (e.g. custom sites a user might add).

### 2. ~155 site `.py` files — add `category=` kwarg

Each `AdultSite(...)` instantiation gets a `category="..."` keyword argument matching one of the 7 strings above. No site logic changes — purely additive. Sites with existing (old) category strings get them renamed to match the new taxonomy.

## Notes

- `erogarga.py` registers 3 sites (`erogarga`, `fulltaboo`, `koreanpornmovie`) — all three get `category=` added.
- `reallifecam.py` registers 4 sites — all four get `category="Cams & Live"`.
- `missav` and `luxuretv` are in `EXCLUDED_SITE_MODULES` — no changes needed for excluded sites, but `missav.py` already has `category="JAV"` which can be updated for consistency.
