# New Sites to Implement

This file tracks sites identified from screenshots that are not yet implemented in the Cumination addon.

## 🔥 Tier 1 - Major Tube Sites (Highest Priority)

- [x] **YouPorn** - Major tube site (MindGeek/Aylo network) ✅ **COMPLETED**
- [x] **RedTube** - Major tube site (MindGeek/Aylo network) ✅ **COMPLETED**
- [x] **Tube8** - Major tube site (MindGeek/Aylo network) ✅ **COMPLETED**
- [x] **YouJizz** - Popular tube site ✅ **COMPLETED**
- [x] **Motherless** - User-generated content site ✅ **COMPLETED**

## ⭐ Tier 2 - Popular Sites

- [ ] **SexyPorn**
- [ ] **Porninja**
- [ ] **PlayHDPorn**
- [ ] **PornHD3x**
- [ ] **SuperPorn**
- [ ] **OnlinePornHub**

## 📊 Tier 3 - Medium Traffic Sites

- [ ] **neporn**
- [ ] **FreePornVideos**
- [ ] **StreamPorn** (variants: 2, 3)
- [ ] **BananaMovies**
- [ ] **ShyFap**
- [ ] **PornLay**
- [ ] **SomePorn**
- [ ] **wapbold**
- [ ] **5MoviesPorn**
- [ ] **TopVid**
- [ ] **OK.XXX**
- [ ] **Hotmovix**
- [ ] **iPornTV**
- [ ] **PornoBae**
- [ ] **Jizzbunker**
- [ ] **10HitMovies**
- [ ] **pornken**
- [ ] **Heavy-R**
- [ ] **ThePornArea**
- [ ] **Analdin**
- [ ] **SU1**
- [ ] **Porndoe**
- [ ] **Intporn**
- [ ] **Siska**
- [ ] **PornXpert**
- [ ] **Ask4Porn**
- [ ] **ClipHunter**
- [ ] **xGoMovies**
- [ ] **Vid123**

## 🌍 Tier 4 - International/Niche

- [ ] **anysex.com**
- [ ] **Kojka**
- [ ] **Sex-Empire**
- [ ] **ifugyou**
- [ ] **xxxgr** (Greek porn)

## 📝 Sites Excluded (Not Applicable)

These sites were identified but won't be implemented:
- ❌ **CUMS** - Aggregator/search engine
- ❌ **PHPremium** - Premium content (may require auth)
- ❌ **LPSG** - Forum (not video site)
- ❌ **Adult TV Channels** - Live streams (different architecture)
- ❌ **Porn Randomizer** - Aggregator
- ❌ **Porn App/NsfwBox** - Android apps (not applicable)
- ❌ **Full Length Porn CSE** - Search engine
- ❌ **DXXX/NSFWBase/PornMD** - Aggregators

## Implementation Notes

**Recommended Order:**
1. **Phase 1:** YouPorn, RedTube, Tube8 (Same network as PornHub)
2. **Phase 2:** YouJizz, Motherless, SexyPorn, PlayHDPorn
3. **Phase 3:** Rest of Tier 2 and Tier 3 as needed

**When implementing a site:**
1. Check this list and mark with `[x]` when started
2. Create site implementation in `plugin.video.cumination/resources/lib/sites/[sitename].py`
3. Use BeautifulSoup pattern (preferred over regex)
4. Create test fixtures in `tests/fixtures/[sitename]/`
5. Create tests in `tests/sites/test_[sitename].py`
6. Test functionality: listing, pagination, categories, search, playback
7. Mark as complete in this file when working and tested
