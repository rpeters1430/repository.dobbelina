# Site Categories Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Assign one of 7 broad categories to every site in the addon and display a per-category icon in the "Browse by Category" Kodi menu.

**Architecture:** `AdultSite` already has a `category` field and `default.py` already has `category_list()` / `browse_category()` wired up. This plan is almost entirely data: (1) update `default.py` to use a category→icon mapping, (2) add/rename `category=` kwargs across ~155 site files. One new test verifies completeness.

**Tech Stack:** Python 3, Kodi addon (kodi-six), pytest

---

## File Map

| File | Change |
|---|---|
| `tests/test_site_categories.py` | **Create** — coverage test |
| `plugin.video.cumination/default.py` | **Modify** — `category_list()` uses per-category icons |
| `plugin.video.cumination/resources/lib/sites/*.py` | **Modify** — add/rename `category=` kwarg on each `AdultSite(...)` |

---

## Valid Categories (reference for all tasks)

```python
VALID_CATEGORIES = {
    "Video Tubes",
    "Cams & Live",
    "JAV & Asian",
    "Hentai & Anime",
    "Amateur & Social",
    "Specialty",
    "Aggregators",
}
```

---

## Task 1: Write failing category coverage test

**Files:**
- Create: `tests/test_site_categories.py`

- [ ] **Step 1: Create the test file**

```python
"""Verify every non-testing site has a valid category."""
import importlib

VALID_CATEGORIES = {
    "Video Tubes",
    "Cams & Live",
    "JAV & Asian",
    "Hentai & Anime",
    "Amateur & Social",
    "Specialty",
    "Aggregators",
}


def test_all_sites_have_valid_category():
    from resources.lib.sites import __all__ as site_names
    for name in site_names:
        importlib.import_module(f"resources.lib.sites.{name}")

    from resources.lib.adultsite import AdultSite
    sites = list(AdultSite.get_sites())
    assert sites, "No sites loaded — check imports"

    uncategorized = [s.name for s in sites if not s.category]
    assert not uncategorized, (
        f"Sites missing category ({len(uncategorized)}): {sorted(uncategorized)}"
    )

    invalid = [s.name for s in sites if s.category not in VALID_CATEGORIES]
    assert not invalid, (
        f"Sites with unknown category string: {sorted(invalid)}"
    )
```

- [ ] **Step 2: Run test — verify it fails**

```bash
python run_tests.py --site test_site_categories -v
```

Expected: FAIL — lists ~130 sites missing a category.

---

## Task 2: Update `default.py` category list with per-category icons

**Files:**
- Modify: `plugin.video.cumination/default.py`

- [ ] **Step 1: Add `CATEGORY_ICONS` dict and update `category_list()`**

In `default.py`, replace the existing `category_list()` function (currently around line 292) with:

```python
_CATEGORY_ICONS = {
    "Video Tubes":      basics.cum_image("pornhub.png"),
    "Cams & Live":      basics.cum_image("chaturbate.png"),
    "JAV & Asian":      basics.cum_image("javmoe.png"),
    "Hentai & Anime":   basics.cum_image("hanime.png"),
    "Amateur & Social": basics.cum_image("erome.png"),
    "Specialty":        basics.cum_image("trannyteca.png"),
    "Aggregators":      basics.cum_image("archivebate.png"),
}


@url_dispatcher.register()
def category_list():
    categories = set()
    for x in AdultSite.get_sites():
        if x.category:
            categories.add(x.category)

    for cat in sorted(categories):
        icon = _CATEGORY_ICONS.get(cat, basics.cum_image("cum-sites.png"))
        url_dispatcher.add_dir(
            "[COLOR white]{}[/COLOR]".format(cat),
            cat,
            "browse_category",
            icon,
            "",
            list_avail=False,
        )

    utils.eod(basics.addon_handle, False)
```

Note: the `_CATEGORY_ICONS` dict is defined at module level (not inside the function) so it is built once. The "Uncategorized" fallback entry is removed — after this work all sites will have a category.

- [ ] **Step 2: Commit**

```bash
git add plugin.video.cumination/default.py
git commit -m "feat: use per-category icons in Browse by Category menu"
```

---

## Task 3: Rename existing old category strings (15 files)

These sites already have `category=` but with old strings that must match the new taxonomy.

**Files to modify** (all in `plugin.video.cumination/resources/lib/sites/`):

| File | Old value | New value |
|---|---|---|
| `javbangers.py` | `"JAV"` | `"JAV & Asian"` |
| `javguru.py` | `"JAV"` | `"JAV & Asian"` |
| `chaturbate.py` | `"Cam Models"` | `"Cams & Live"` |
| `bongacams.py` | `"Cam Models"` | `"Cams & Live"` |
| `stripchat.py` | `"Cam Models"` | `"Cams & Live"` |
| `amateurtv.py` | `"Cam Models"` | `"Cams & Live"` |
| `cloudbate.py` | `"Cam Models"` | `"Cams & Live"` |
| `hentaistream.py` | `"Hentai"` | `"Hentai & Anime"` |
| `hentaihavenco.py` | `"Hentai"` | `"Hentai & Anime"` |
| `hentaidude.py` | `"Hentai"` | `"Hentai & Anime"` |
| `animeidhentai.py` | `"Hentai"` | `"Hentai & Anime"` |
| `hanime.py` | `"Hentai"` | `"Hentai & Anime"` |
| `erome.py` | `"Social / Amateur"` | `"Amateur & Social"` |
| `hotleak.py` | `"Leaks"` | `"Amateur & Social"` |
| `porn4k.py` | `"VR"` | `"Specialty"` |

- [ ] **Step 1: Apply all 15 renames**

For each file, find the line `category="<old value>",` and change it to `category="<new value>",`. The surrounding code does not change.

Example — `javbangers.py`:
```python
# before
    category="JAV",
# after
    category="JAV & Asian",
```

- [ ] **Step 2: Run the coverage test — verify count drops**

```bash
python run_tests.py --site test_site_categories -v
```

Expected: still FAIL, but the invalid-category list should now be empty; only the uncategorized list remains.

- [ ] **Step 3: Commit**

```bash
git add plugin.video.cumination/resources/lib/sites/javbangers.py \
        plugin.video.cumination/resources/lib/sites/javguru.py \
        plugin.video.cumination/resources/lib/sites/chaturbate.py \
        plugin.video.cumination/resources/lib/sites/bongacams.py \
        plugin.video.cumination/resources/lib/sites/stripchat.py \
        plugin.video.cumination/resources/lib/sites/amateurtv.py \
        plugin.video.cumination/resources/lib/sites/cloudbate.py \
        plugin.video.cumination/resources/lib/sites/hentaistream.py \
        plugin.video.cumination/resources/lib/sites/hentaihavenco.py \
        plugin.video.cumination/resources/lib/sites/hentaidude.py \
        plugin.video.cumination/resources/lib/sites/animeidhentai.py \
        plugin.video.cumination/resources/lib/sites/hanime.py \
        plugin.video.cumination/resources/lib/sites/erome.py \
        plugin.video.cumination/resources/lib/sites/hotleak.py \
        plugin.video.cumination/resources/lib/sites/porn4k.py
git commit -m "chore: rename legacy category strings to new taxonomy"
```

---

## Task 4: Tag Video Tubes — batch A (a–n)

**Pattern:** For each site file below, add `category="Video Tubes",` as the last kwarg inside the `AdultSite(...)` call, before the closing `)`.

Multi-line example (`analdin.py`):
```python
# before
site = AdultSite(
    "analdin",
    "[COLOR hotpink]Analdin[/COLOR]",
    "https://www.analdin.com/",
    "analdin.png",
)
# after
site = AdultSite(
    "analdin",
    "[COLOR hotpink]Analdin[/COLOR]",
    "https://www.analdin.com/",
    "analdin.png",
    category="Video Tubes",
)
```

Single-line example (`85po.py` — but note 85po is JAV & Asian, this is just a format demo):
```python
# before
site = AdultSite("name", "Title", "https://url/", "img.png", "about")
# after
site = AdultSite("name", "Title", "https://url/", "img.png", "about", category="Video Tubes")
```

**Files to tag (Video Tubes, batch A):**

`6xtube.py`, `absoluporn.py`, `allclassic.py`, `analdin.py`, `anybunny.py`, `ask4porn.py`, `beemtube.py`, `blendporn.py`, `cumlouder.py`, `drtuber.py`, `foxnxx.py`, `freeomovie.py`, `freepornvideos.py`, `freshporno.py`, `fullporner.py`, `fullxcinema.py`, `fyxxr.py`, `hdporn.py`, `hdporn92.py`, `heavyr.py`, `heroero.py`, `hitprn.py`, `hornyfap.py`, `jizzbunker.py`, `josporn.py`, `justfullporn.py`, `justporn.py`, `longvideos.py`, `mrsexe.py`, `naked.py`, `neporn.py`, `netfapx.py`, `netflixporno.py`, `nltubes.py`, `nonktube.py`

- [ ] **Step 1: Add `category="Video Tubes"` to all 35 files above**

- [ ] **Step 2: Run the coverage test**

```bash
python run_tests.py --site test_site_categories -v
```

Expected: still FAIL but uncategorized count should drop by ~35.

- [ ] **Step 3: Commit**

```bash
git add plugin.video.cumination/resources/lib/sites/6xtube.py \
        plugin.video.cumination/resources/lib/sites/absoluporn.py \
        plugin.video.cumination/resources/lib/sites/allclassic.py \
        plugin.video.cumination/resources/lib/sites/analdin.py \
        plugin.video.cumination/resources/lib/sites/anybunny.py \
        plugin.video.cumination/resources/lib/sites/ask4porn.py \
        plugin.video.cumination/resources/lib/sites/beemtube.py \
        plugin.video.cumination/resources/lib/sites/blendporn.py \
        plugin.video.cumination/resources/lib/sites/cumlouder.py \
        plugin.video.cumination/resources/lib/sites/drtuber.py \
        plugin.video.cumination/resources/lib/sites/foxnxx.py \
        plugin.video.cumination/resources/lib/sites/freeomovie.py \
        plugin.video.cumination/resources/lib/sites/freepornvideos.py \
        plugin.video.cumination/resources/lib/sites/freshporno.py \
        plugin.video.cumination/resources/lib/sites/fullporner.py \
        plugin.video.cumination/resources/lib/sites/fullxcinema.py \
        plugin.video.cumination/resources/lib/sites/fyxxr.py \
        plugin.video.cumination/resources/lib/sites/hdporn.py \
        plugin.video.cumination/resources/lib/sites/hdporn92.py \
        plugin.video.cumination/resources/lib/sites/heavyr.py \
        plugin.video.cumination/resources/lib/sites/heroero.py \
        plugin.video.cumination/resources/lib/sites/hitprn.py \
        plugin.video.cumination/resources/lib/sites/hornyfap.py \
        plugin.video.cumination/resources/lib/sites/jizzbunker.py \
        plugin.video.cumination/resources/lib/sites/josporn.py \
        plugin.video.cumination/resources/lib/sites/justfullporn.py \
        plugin.video.cumination/resources/lib/sites/justporn.py \
        plugin.video.cumination/resources/lib/sites/longvideos.py \
        plugin.video.cumination/resources/lib/sites/mrsexe.py \
        plugin.video.cumination/resources/lib/sites/naked.py \
        plugin.video.cumination/resources/lib/sites/neporn.py \
        plugin.video.cumination/resources/lib/sites/netfapx.py \
        plugin.video.cumination/resources/lib/sites/netflixporno.py \
        plugin.video.cumination/resources/lib/sites/nltubes.py \
        plugin.video.cumination/resources/lib/sites/nonktube.py
git commit -m "chore: tag Video Tubes sites batch A (a-n)"
```

---

## Task 5: Tag Video Tubes — batch B (o–z)

**Files to tag (Video Tubes, batch B):**

`okxxx.py`, `pimpbunny.py`, `playhdporn.py`, `porndig.py`, `porndish.py`, `pornditt.py`, `porndoe.py`, `pornez.py`, `porngo.py`, `pornhat.py`, `pornhd3x.py`, `pornhits.py`, `pornhoarder.py`, `pornkai.py`, `pornmz.py`, `porno1hu.py`, `porno365.py`, `pornone.py`, `pornroom.py`, `porntn.py`, `porntrex.py`, `pornxp.py`, `premiumporn.py`, `sextb.py`, `sexyporn.py`, `someporn.py`, `speedporn.py`, `sunporno.py`, `superporn.py`, `sxyprn.py`, `thepornarea.py`, `tnaflix.py`, `tube8.py`, `tubxporn.py`, `txxx.py`, `uflash.py`, `vaginanl.py`, `vipporns.py`, `viralvideosporno.py`, `watchporn.py`, `whereismyporn.py`, `whoreshub.py`, `xfreehd.py`, `xmegadrive.py`, `xmoviesforyou.py`, `xozilla.py`, `xtheatre.py`, `xxdbx.py`, `xxxtube.py`, `youcrazyx.py`, `youjizz.py`, `youporn.py`, `yrprno.py`

- [ ] **Step 1: Add `category="Video Tubes"` to all 53 files above**

Use the same pattern as Task 4: add `category="Video Tubes",` as the last kwarg before the closing `)` of each `AdultSite(...)` call.

- [ ] **Step 2: Run the coverage test**

```bash
python run_tests.py --site test_site_categories -v
```

Expected: still FAIL but only non-tube sites remain uncategorized.

- [ ] **Step 3: Commit**

```bash
git add plugin.video.cumination/resources/lib/sites/okxxx.py \
        plugin.video.cumination/resources/lib/sites/pimpbunny.py \
        plugin.video.cumination/resources/lib/sites/playhdporn.py \
        plugin.video.cumination/resources/lib/sites/porndig.py \
        plugin.video.cumination/resources/lib/sites/porndish.py \
        plugin.video.cumination/resources/lib/sites/pornditt.py \
        plugin.video.cumination/resources/lib/sites/porndoe.py \
        plugin.video.cumination/resources/lib/sites/pornez.py \
        plugin.video.cumination/resources/lib/sites/porngo.py \
        plugin.video.cumination/resources/lib/sites/pornhat.py \
        plugin.video.cumination/resources/lib/sites/pornhd3x.py \
        plugin.video.cumination/resources/lib/sites/pornhits.py \
        plugin.video.cumination/resources/lib/sites/pornhoarder.py \
        plugin.video.cumination/resources/lib/sites/pornkai.py \
        plugin.video.cumination/resources/lib/sites/pornmz.py \
        plugin.video.cumination/resources/lib/sites/porno1hu.py \
        plugin.video.cumination/resources/lib/sites/porno365.py \
        plugin.video.cumination/resources/lib/sites/pornone.py \
        plugin.video.cumination/resources/lib/sites/pornroom.py \
        plugin.video.cumination/resources/lib/sites/porntn.py \
        plugin.video.cumination/resources/lib/sites/porntrex.py \
        plugin.video.cumination/resources/lib/sites/pornxp.py \
        plugin.video.cumination/resources/lib/sites/premiumporn.py \
        plugin.video.cumination/resources/lib/sites/sextb.py \
        plugin.video.cumination/resources/lib/sites/sexyporn.py \
        plugin.video.cumination/resources/lib/sites/someporn.py \
        plugin.video.cumination/resources/lib/sites/speedporn.py \
        plugin.video.cumination/resources/lib/sites/sunporno.py \
        plugin.video.cumination/resources/lib/sites/superporn.py \
        plugin.video.cumination/resources/lib/sites/sxyprn.py \
        plugin.video.cumination/resources/lib/sites/thepornarea.py \
        plugin.video.cumination/resources/lib/sites/tnaflix.py \
        plugin.video.cumination/resources/lib/sites/tube8.py \
        plugin.video.cumination/resources/lib/sites/tubxporn.py \
        plugin.video.cumination/resources/lib/sites/txxx.py \
        plugin.video.cumination/resources/lib/sites/uflash.py \
        plugin.video.cumination/resources/lib/sites/vaginanl.py \
        plugin.video.cumination/resources/lib/sites/vipporns.py \
        plugin.video.cumination/resources/lib/sites/viralvideosporno.py \
        plugin.video.cumination/resources/lib/sites/watchporn.py \
        plugin.video.cumination/resources/lib/sites/whereismyporn.py \
        plugin.video.cumination/resources/lib/sites/whoreshub.py \
        plugin.video.cumination/resources/lib/sites/xfreehd.py \
        plugin.video.cumination/resources/lib/sites/xmegadrive.py \
        plugin.video.cumination/resources/lib/sites/xmoviesforyou.py \
        plugin.video.cumination/resources/lib/sites/xozilla.py \
        plugin.video.cumination/resources/lib/sites/xtheatre.py \
        plugin.video.cumination/resources/lib/sites/xxdbx.py \
        plugin.video.cumination/resources/lib/sites/xxxtube.py \
        plugin.video.cumination/resources/lib/sites/youcrazyx.py \
        plugin.video.cumination/resources/lib/sites/youjizz.py \
        plugin.video.cumination/resources/lib/sites/youporn.py \
        plugin.video.cumination/resources/lib/sites/yrprno.py
git commit -m "chore: tag Video Tubes sites batch B (o-z)"
```

---

## Task 6: Tag Cams & Live sites

**Files to tag** (7 new — the other 5 were renamed in Task 3):

`cam4.py`, `camsoda.py`, `lemoncams.py`, `myfreecams.py`, `paradisehill.py`, `reallifecam.py`, `streamate.py`

**Note on `reallifecam.py`:** This file registers **4** sites (`rlc`, `voyeurhouse`, `reallifecams`, `camcaps`). Add `category="Cams & Live"` to all four `AdultSite(...)` calls in this file.

- [ ] **Step 1: Add `category="Cams & Live"` to all sites in the 7 files**

Example (`cam4.py` — single AdultSite call):
```python
site = AdultSite(
    "cam4",
    "[COLOR hotpink]Cam4[/COLOR]",
    "https://www.cam4.com/",
    "cam4.png",
    "cam4",
    category="Cams & Live",
)
```

For `reallifecam.py`, apply `category="Cams & Live"` to all four `AdultSite(...)` constructors in the file.

- [ ] **Step 2: Commit**

```bash
git add plugin.video.cumination/resources/lib/sites/cam4.py \
        plugin.video.cumination/resources/lib/sites/camsoda.py \
        plugin.video.cumination/resources/lib/sites/lemoncams.py \
        plugin.video.cumination/resources/lib/sites/myfreecams.py \
        plugin.video.cumination/resources/lib/sites/paradisehill.py \
        plugin.video.cumination/resources/lib/sites/reallifecam.py \
        plugin.video.cumination/resources/lib/sites/streamate.py
git commit -m "chore: tag Cams & Live sites"
```

---

## Task 7: Tag JAV & Asian sites

**Files to tag** (15 new — `javbangers.py` and `javguru.py` were renamed in Task 3):

`85po.py`, `avple.py`, `hpjav.py`, `japteenx.py`, `javgg.py`, `javhdporn.py`, `javmoe.py`, `javseen.py`, `kissjav.py`, `netflav.py`, `noodlemagazine.py`, `seaporn.py`, `supjav.py`, `terebon.py`, `tokyomotion.py`

**Note on `85po.py`:** Uses single-line constructor format. Add `, category="JAV & Asian"` before the closing `)`:
```python
# before
site = AdultSite("85po", "[COLOR hotpink]85po[/COLOR]", "https://85po.com/", "85po.png", "85po")
# after
site = AdultSite("85po", "[COLOR hotpink]85po[/COLOR]", "https://85po.com/", "85po.png", "85po", category="JAV & Asian")
```

- [ ] **Step 1: Add `category="JAV & Asian"` to all 15 files**

- [ ] **Step 2: Commit**

```bash
git add plugin.video.cumination/resources/lib/sites/85po.py \
        plugin.video.cumination/resources/lib/sites/avple.py \
        plugin.video.cumination/resources/lib/sites/hpjav.py \
        plugin.video.cumination/resources/lib/sites/japteenx.py \
        plugin.video.cumination/resources/lib/sites/javgg.py \
        plugin.video.cumination/resources/lib/sites/javhdporn.py \
        plugin.video.cumination/resources/lib/sites/javmoe.py \
        plugin.video.cumination/resources/lib/sites/javseen.py \
        plugin.video.cumination/resources/lib/sites/kissjav.py \
        plugin.video.cumination/resources/lib/sites/netflav.py \
        plugin.video.cumination/resources/lib/sites/noodlemagazine.py \
        plugin.video.cumination/resources/lib/sites/seaporn.py \
        plugin.video.cumination/resources/lib/sites/supjav.py \
        plugin.video.cumination/resources/lib/sites/terebon.py \
        plugin.video.cumination/resources/lib/sites/tokyomotion.py
git commit -m "chore: tag JAV & Asian sites"
```

---

## Task 8: Tag Hentai & Anime sites

**Files to tag** (2 new — the other 5 were renamed in Task 3):

`hentai-moon.py`, `rule34video.py`

- [ ] **Step 1: Add `category="Hentai & Anime"` to both files**

- [ ] **Step 2: Commit**

```bash
git add plugin.video.cumination/resources/lib/sites/hentai-moon.py \
        plugin.video.cumination/resources/lib/sites/rule34video.py
git commit -m "chore: tag Hentai & Anime sites"
```

---

## Task 9: Tag Amateur & Social sites

**Files to tag** (9 new — `erome.py` and `hotleak.py` were renamed in Task 3):

`camwhoresbay.py`, `hobbyporn.py`, `homemoviestube.py`, `livecamrips.py`, `naughtyblog.py`, `thothub.py`, `watchmdh.py`, `xsharings.py`, `xxthots.py`

**Note on `xxthots.py`:** Uses single-line constructor format:
```python
# before
site = AdultSite('xxthots', '[COLOR hotpink]xxThots[/COLOR]', 'https://xxthots.com/', 'xxthots.png', 'xxthots')
# after
site = AdultSite('xxthots', '[COLOR hotpink]xxThots[/COLOR]', 'https://xxthots.com/', 'xxthots.png', 'xxthots', category="Amateur & Social")
```

- [ ] **Step 1: Add `category="Amateur & Social"` to all 9 files**

- [ ] **Step 2: Commit**

```bash
git add plugin.video.cumination/resources/lib/sites/camwhoresbay.py \
        plugin.video.cumination/resources/lib/sites/hobbyporn.py \
        plugin.video.cumination/resources/lib/sites/homemoviestube.py \
        plugin.video.cumination/resources/lib/sites/livecamrips.py \
        plugin.video.cumination/resources/lib/sites/naughtyblog.py \
        plugin.video.cumination/resources/lib/sites/thothub.py \
        plugin.video.cumination/resources/lib/sites/watchmdh.py \
        plugin.video.cumination/resources/lib/sites/xsharings.py \
        plugin.video.cumination/resources/lib/sites/xxthots.py
git commit -m "chore: tag Amateur & Social sites"
```

---

## Task 10: Tag Specialty sites

**Files to tag** (16 new — `porn4k.py` was renamed in Task 3):

`aagmaal.py`, `aagmaalpro.py`, `celebsroulette.py`, `eroticage.py`, `erogarga.py`, `eroticmv.py`, `familypornhd.py`, `freeuseporn.py`, `peachurnet.py`, `perverzija.py`, `pmvhaven.py`, `taboofantazy.py`, `tabootube.py`, `theyarehuge.py`, `trannyteca.py`, `watcherotic.py`

**Note on `erogarga.py`:** This file registers **3** sites. Add `category="Specialty"` to all three:
- `site` (erogarga.com) → `"Specialty"`
- `site1` (fulltaboo.tv) → `"Specialty"`
- `site2` (koreanpornmovie.com) → `"Specialty"`

- [ ] **Step 1: Add `category="Specialty"` to all sites in the 16 files**

- [ ] **Step 2: Commit**

```bash
git add plugin.video.cumination/resources/lib/sites/aagmaal.py \
        plugin.video.cumination/resources/lib/sites/aagmaalpro.py \
        plugin.video.cumination/resources/lib/sites/celebsroulette.py \
        plugin.video.cumination/resources/lib/sites/eroticage.py \
        plugin.video.cumination/resources/lib/sites/erogarga.py \
        plugin.video.cumination/resources/lib/sites/eroticmv.py \
        plugin.video.cumination/resources/lib/sites/familypornhd.py \
        plugin.video.cumination/resources/lib/sites/freeuseporn.py \
        plugin.video.cumination/resources/lib/sites/peachurnet.py \
        plugin.video.cumination/resources/lib/sites/perverzija.py \
        plugin.video.cumination/resources/lib/sites/pmvhaven.py \
        plugin.video.cumination/resources/lib/sites/taboofantazy.py \
        plugin.video.cumination/resources/lib/sites/tabootube.py \
        plugin.video.cumination/resources/lib/sites/theyarehuge.py \
        plugin.video.cumination/resources/lib/sites/trannyteca.py \
        plugin.video.cumination/resources/lib/sites/watcherotic.py
git commit -m "chore: tag Specialty sites"
```

---

## Task 11: Tag Aggregators

**Files to tag** (4 files — all new):

`archivebate.py`, `awmnet.py`, `peekvids.py`, `playvids.py`

- [ ] **Step 1: Add `category="Aggregators"` to all 4 files**

- [ ] **Step 2: Commit**

```bash
git add plugin.video.cumination/resources/lib/sites/archivebate.py \
        plugin.video.cumination/resources/lib/sites/awmnet.py \
        plugin.video.cumination/resources/lib/sites/peekvids.py \
        plugin.video.cumination/resources/lib/sites/playvids.py
git commit -m "chore: tag Aggregators sites"
```

---

## Task 12: Verify all tests pass

- [ ] **Step 1: Run the full test suite**

```bash
python run_tests.py -v
```

Expected: all tests PASS including `test_site_categories.py::test_all_sites_have_valid_category`.

If `test_all_sites_have_valid_category` still fails, the output will list the offending site names — add the missing `category=` kwarg to those files and re-run.

- [ ] **Step 2: Run lint**

```bash
ruff check plugin.video.cumination/resources/lib/
```

Expected: no new errors.

- [ ] **Step 3: Commit the test file (if not already committed)**

The test file `tests/test_site_categories.py` was created in Task 1 but intentionally left uncommitted until the implementation was complete. Commit it now:

```bash
git add tests/test_site_categories.py
git commit -m "test: add category coverage test for all sites"
```
