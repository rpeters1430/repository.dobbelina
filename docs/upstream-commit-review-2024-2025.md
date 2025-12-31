# Upstream Commit Review (October 2024 - December 2025)

## Executive Summary

This document analyzes **1,929 commits** from the upstream repository (dobbelina/repository.dobbelina) that are not present in this fork. The analysis focuses on identifying which commits should be cherry-picked to enhance the fork while preserving the custom testing infrastructure and modernization work already completed.

**Key Findings:**
- Fork version: **1.1.209** (ahead of upstream in numbering)
- Upstream version: **1.1.163**
- Fork contains significant custom work (testing, BeautifulSoup migration, documentation)
- **~150 high-value commits** recommended for cherry-picking
- **314 version bump commits** should be skipped (fork has its own versioning)

---

## Commit Statistics

| Category | Count | Action |
|----------|-------|--------|
| Version bumps/packaging | 314 | **SKIP** |
| Site fixes | 449 | **SELECTIVE** |
| New sites | 70 | **REVIEW** |
| Site removals | 16 | **CONSIDER** |
| Python 2 compatibility | 4 | **IMPORTANT** |
| FlareSolverr updates | 3 | **IMPORTANT** |
| Core module fixes | 1 | **CRITICAL** |
| Other changes | 1,072 | **REVIEW** |
| **Total** | **1,929** | |

---

## Critical Commits (MUST CHERRY-PICK)

### 1. Core Module Fixes

These fix fundamental issues affecting all sites:

| Commit | Title | Reason |
|--------|-------|--------|
| `673fe9b` | fix module load error on TvOS #1724 | Fixes critical module loading bug on TvOS platform |
| `7bbe1c7` | Fix video playback for FlareSolverr scraped sites (e.g. luxuretv) | Fixes playback for all FlareSolverr-enabled sites |

**Action**: Cherry-pick both commits immediately after testing for conflicts.

### 2. Python 2 Compatibility Fixes

Required for users still on Python 2.7 (Kodi 18 and older):

| Commit | Title |
|--------|-------|
| `3a98f37` | Python 2 fixes #1722 fixes #1663 |
| `fb3243d` | fix python 2 compatibility #1663 |
| `86946aa` | chaturbate python 2 compatibiity fix |
| `24d0b16` | Exceptionlogger Python 2.7 compatible |

**Action**: Cherry-pick all 4 commits as a group to maintain compatibility.

### 3. FlareSolverr Integration

Critical for Cloudflare-protected sites:

| Commit | Title |
|--------|-------|
| `13b282c` | Kodi Flaresolverr Autostarter |
| `58241c6` | Flaresolverr support |
| `7bbe1c7` | Fix video playback for FlareSolverr scraped sites |

**Action**: Review carefully - fork may already have FlareSolverr support. Check for conflicts.

---

## High-Priority Site Fixes (RECOMMENDED)

### Popular Sites (Top 10 by usage)

These fix the most commonly used sites:

#### Pornhub Fixes
- `31644dc` - pornhub fixes #1712
- `0649955` - pornhub categories - fixes #1664

#### XHamster Fixes
- `ad3cfe5` - xhamster fixes #1668
- `c92e14e` - xhamster: play h264 streams instead of av1 - fixes #1676
- `7436c71` - awmnet fix xhamster streams #1677
- `f3d48c1` - xhmster playback

#### Hanime Fixes (Popular anime site)
- `60b6859` - hanime playback - fixes #1688
- `86d995a` - hanime fixes #1686
- `273e27b` - hanime fix favorites #1666
- `e250c5d` - hanime - fix playback fixes #1646
- `5069719` - hentaihavenco - fix listing, playback #1644

#### Spankbang Fixes
- `1e2417e` - spankbang - fix listing #1643

#### Stripchat Fixes
- `e96ed9b` - stripchat - fix playback (SD only) fixes #1710

#### Other Important Fixes
- `6ee3883` - Foxnxx & HQPorner playback fix - fixes #1607
- `58d28d9` - foxnxx - fix playback fixes #1657
- `cd0cc1c` - foxnxx - fix playback fixes #1600

**Action**: Cherry-pick all popular site fixes (20 commits). Test each site after applying.

---

## New Sites to Consider (70 total)

### Recently Added (Most Recent First)

| Commit | Site Name | Notes |
|--------|-----------|-------|
| `8eae561` | fullxcinema | Latest addition |
| `122e955` | freepornvideos | Stable, working site |
| `67bd60f` | tokyomotion | Japanese content site |
| `ba754a5` | xxdbx | Video sharing platform |
| `8301e4d` | 85po | New site with HD content |
| `6449cad` | xsharings | File sharing site |
| `4e2c8e0` | premiumporn | Premium content aggregator |
| `e3246a1` | longvideos | Long-form content |
| `84fa2f4` | terebon | Japanese adult site |
| `d68a825` | fulltaboo, koreanpornmovie | Two Korean sites |

### More Sites (Next 10)
- `5a7bf2c` - Porno1hu
- `42aaa0a` - Fuxmovies
- `9af43e2` - WatchMDH
- `f57d9db` - Porn4k.to
- `20af76e` - EroticMV
- `750c731` - Netflav (JAV site)
- `464392c` - PornTN
- `5030432` - DrTuber
- `c3924de` - Fullporner
- `5b6a091` - WhereIsMyPorn

**Action**: 
1. Review each new site for quality and legal concerns
2. Cherry-pick stable sites that add value
3. Test thoroughly before merging
4. Consider user demand for specific sites

---

## Site Removals to Apply

These sites are dead, broken, or legally problematic:

| Commit | Sites Removed | Reason |
|--------|---------------|--------|
| `43c6322` | americass | Website down |
| `f4c5a43` | iflix | No longer operational |
| `b5ae7b6` | bubba, cambro, yespornplease | Multiple dead sites |
| `71d1398` | vintagetube | Site offline |
| `abb53d8` | ividz | Broken |
| `8655ef5` | asstoo, bitporno | Dead sites |
| `91d2249` | americass | Duplicate removal |
| `da3a465` | asianporn | Offline |
| `24b5b73` | amateurcool | Broken |

**Action**: Apply all removal commits to clean up broken sites (saves user confusion).

---

## Medium-Priority Site Fixes (CONSIDER)

### AWM Network Sites
- `d522ced` - awmnet - fix listing
- `b806f1f` - awmnet - update site list fixes #1680
- `c267672` - awmnet - fix categories, tgs, pornstars - fixes #1679
- `61e7be5` - awm network - fix listing #1655
- `759d910` - AWM Network - fix listing fixes #1673
- `afe1ff0` - celebsroulette, awmnet

### Cam Sites
- `b4beb80` - camwhoresbay - fix playback
- `9722f3e` - camwhoresbay - fix next page
- `d47192d` - camsoda #1685
- `e40d58d` - camcaps site name change

### Other Notable Sites
- `c11caeb` - pornhoarder fixes #1713
- `53a9dfe` - whoreshub fixes #1715
- `d92bd04` - tnaflix fixes #1718
- `0509d5b` - premiumporn - fixes #1714
- `51c39fb` - porntn fixes #1720
- `90d2f5a` - pornxp - domain change - fixes #1711
- `a34c0a7` - terebon - fix listing
- `1721e03` - terebon - fix playback
- `6df953b` - familypornhd - fix sound - fixes #1682
- `97de93c` - aagmaalpro domain change
- `f2de1aa` - familypornhd - fix playback fixes #1678

**Action**: Cherry-pick based on user reports and site popularity. Not critical but improves experience.

---

## Commits to SKIP

### Version Bumps (314 commits)

All commits with "Bumped to v.X.X.XXX" should be **SKIPPED**:
- Fork maintains its own version numbering (currently 1.1.209)
- Upstream is at 1.1.163
- Version conflicts would cause confusion
- Fork has additional features not in upstream

### Examples to Skip:
- `c9f1144` - 2025-12-28 Bumped to v.1.1.163
- `d7581d5` - 2025-12-07 Bumped to v.1.1.162
- `b8e1df5` - 2025-11-30 Bumped to v.1.1.161
- `4787d5f` - 2025-11-23 Bumped to v.1.1.160
- ... (310 more)

### Packaging Commits

Commits that only update ZIP files or metadata:
- `b4daafc` - fixes (empty commit)
- Various commits with just ".zip" changes

---

## Cherry-Pick Strategy

### Phase 1: Critical Fixes (Week 1)
1. ✅ Create upstream remote and fetch
2. Test current fork state
3. Cherry-pick core module fixes (2 commits)
4. Cherry-pick Python 2 compatibility (4 commits)
5. Review FlareSolverr commits for conflicts
6. Run full test suite
7. Commit and push

### Phase 2: Popular Site Fixes (Week 2)
1. Cherry-pick pornhub fixes (2 commits)
2. Cherry-pick xhamster fixes (4 commits)
3. Cherry-pick hanime fixes (5 commits)
4. Cherry-pick spankbang, stripchat fixes (2 commits)
5. Test each site manually
6. Commit and push

### Phase 3: Site Cleanup (Week 2)
1. Apply all site removal commits (9 commits)
2. Update site listings
3. Test addon menu
4. Commit and push

### Phase 4: New Sites (Week 3-4)
1. Review and test each new site individually
2. Cherry-pick stable, valuable sites (~10-20 sites)
3. Add appropriate categorization
4. Test thoroughly
5. Commit in batches

### Phase 5: Medium-Priority Fixes (Week 5+)
1. Cherry-pick AWM network fixes
2. Cherry-pick cam site fixes
3. Cherry-pick miscellaneous site fixes
4. Test affected sites
5. Commit in logical groups

---

## Conflict Resolution Guidelines

### Expected Conflicts

1. **BeautifulSoup vs Regex**: Fork has migrated many sites to BeautifulSoup, upstream uses regex
   - **Resolution**: Keep fork's BeautifulSoup implementation (better maintainability)
   - Only apply upstream fix if it addresses a bug not present in BS4 version

2. **Testing Infrastructure**: Fork has extensive test suite, upstream doesn't
   - **Resolution**: Keep fork's tests, don't let upstream changes break them

3. **Documentation**: Fork has extensive .md docs, upstream has minimal
   - **Resolution**: Keep fork's documentation, update as needed

4. **Version Numbers**: Conflicts in addon.xml
   - **Resolution**: Always use fork's version number

### Testing Requirements

After each cherry-pick phase:
1. Run `python run_tests.py` - all tests must pass
2. Run `ruff check plugin.video.cumination/resources/lib/` - no new errors
3. Manually test 2-3 affected sites per commit batch
4. Check addon menu loads without errors

---

## Estimated Impact

### If ALL Recommended Commits Applied (~150 commits):

**Benefits:**
- ✅ 8 critical core/compatibility fixes
- ✅ 20+ high-priority site fixes (most popular sites)
- ✅ 10-20 new sites added
- ✅ 9 broken sites removed (cleaner menu)
- ✅ 30+ medium-priority site fixes
- ✅ Improved FlareSolverr support
- ✅ Better Python 2 compatibility

**Risks:**
- ⚠️ Possible conflicts with BeautifulSoup migrations (manageable)
- ⚠️ Testing time required (~40 hours estimated)
- ⚠️ Potential regressions if not tested thoroughly

**Recommendation**: Apply in phases with thorough testing between each phase.

---

## Quick Reference: Git Commands

### Add Upstream Remote (if not done)
```bash
git remote add upstream https://github.com/dobbelina/repository.dobbelina.git
git fetch upstream
```

### Cherry-Pick Single Commit
```bash
git cherry-pick <commit-sha>
# If conflicts:
# 1. Resolve conflicts in editor
# 2. git add <resolved-files>
# 3. git cherry-pick --continue
```

### Cherry-Pick Range of Commits
```bash
git cherry-pick <oldest-sha>^..<newest-sha>
```

### Abort if Problems
```bash
git cherry-pick --abort
```

### View Commit Details
```bash
git show upstream/master:<commit-sha>
```

### Check Which Commits Are Missing
```bash
git log --oneline 627aae7..upstream/master | wc -l
```

---

## Decision Matrix

Use this matrix to decide whether to cherry-pick a commit:

| Commit Type | Cherry-Pick? | Reason |
|-------------|--------------|--------|
| Core module fix | ✅ YES | Affects all sites |
| Python 2 compatibility | ✅ YES | Maintains backwards compatibility |
| FlareSolverr update | ⚠️ REVIEW | Check for conflicts with fork |
| Version bump | ❌ NO | Fork has own versioning |
| Popular site fix | ✅ YES | High user impact |
| Niche site fix | ⚠️ MAYBE | Based on user demand |
| New popular site | ✅ YES | Adds value |
| New niche site | ⚠️ MAYBE | Evaluate quality |
| Site removal | ✅ YES | Cleanup needed |
| Packaging/ZIP | ❌ NO | Fork builds its own |
| Documentation | ⚠️ REVIEW | Fork has better docs |

---

## Conclusion

Out of **1,929 commits** in upstream:
- **~150 commits** recommended for cherry-picking (8%)
- **314 commits** should be skipped (version bumps) (16%)
- **~1,465 commits** need individual evaluation (76%)

**Priority order:**
1. Critical core fixes (8 commits) - **MUST DO**
2. Popular site fixes (20 commits) - **HIGH PRIORITY**
3. Site removals (9 commits) - **RECOMMENDED**
4. New sites (10-20 of 70) - **SELECTIVE**
5. Medium-priority fixes (30-50 commits) - **AS NEEDED**

**Estimated effort:** 40-60 hours over 5 weeks with proper testing.

**Next step:** Begin Phase 1 (Critical Fixes) after approval.
