# Commits to Apply from Upstream

This document lists specific commits from upstream that should be cherry-picked to this fork, organized by priority.

## Quick Stats
- **Total upstream commits**: 1,929
- **Recommended to apply**: ~150 commits
- **Skip (version bumps)**: 314 commits
- **Review case-by-case**: ~1,465 commits

---

## Phase 1: CRITICAL FIXES (Apply First) ⚠️

### Core Module Fixes
```bash
git cherry-pick 673fe9b  # fix module load error on TvOS #1724
git cherry-pick 7bbe1c7  # Fix video playback for FlareSolverr scraped sites
```

### Python 2 Compatibility (Kodi 18 users)
```bash
git cherry-pick 3a98f37  # Python 2 fixes #1722 fixes #1663
git cherry-pick fb3243d  # fix python 2 compatibility #1663
git cherry-pick 86946aa  # chaturbate python 2 compatibiity fix
git cherry-pick 24d0b16  # Exceptionlogger Python 2.7 compatible
```

### FlareSolverr Integration (Review for conflicts first!)
```bash
# Check if these conflict with existing FlareSolverr code
git show 13b282c  # Kodi Flaresolverr Autostarter
git show 58241c6  # Flaresolverr support
# If no conflicts:
git cherry-pick 13b282c
git cherry-pick 58241c6
```

**Total Phase 1**: 8 commits  
**Testing**: Run full test suite, test 3-5 sites manually

---

## Phase 2: POPULAR SITE FIXES (High Priority) 🔥

### Pornhub
```bash
git cherry-pick 31644dc  # pornhub fixes #1712
git cherry-pick 0649955  # pornhub categories - fixes #1664
```

### XHamster
```bash
git cherry-pick f3d48c1  # xhmster playback
git cherry-pick ad3cfe5  # xhamster fixes #1668
git cherry-pick c92e14e  # xhamster: play h264 streams instead of av1
git cherry-pick 7436c71  # awmnet fix xhamster streams #1677
```

### Hanime (Popular anime site)
```bash
git cherry-pick e250c5d  # hanime - fix playback fixes #1646
git cherry-pick 273e27b  # hanime fix favorites #1666
git cherry-pick 86d995a  # hanime fixes #1686
git cherry-pick 60b6859  # hanime playback - fixes #1688
git cherry-pick 5069719  # hentaihavenco - fix listing, playback #1644
```

### Spankbang & Stripchat
```bash
git cherry-pick 1e2417e  # spankbang - fix listing #1643
git cherry-pick e96ed9b  # stripchat - fix playback (SD only) fixes #1710
```

### Other Popular Sites
```bash
git cherry-pick 6ee3883  # Foxnxx & HQPorner playback fix
git cherry-pick 58d28d9  # foxnxx - fix playback fixes #1657
git cherry-pick cd0cc1c  # foxnxx - fix playback fixes #1600
git cherry-pick efddcfe  # foxnxx playback fixes #1629
```

**Total Phase 2**: 19 commits  
**Testing**: Test each affected site (pornhub, xhamster, hanime, spankbang, stripchat, foxnxx, hqporner)

---

## Phase 3: SITE CLEANUP (Remove Dead Sites) 🗑️

```bash
git cherry-pick 43c6322  # americass - removed fixes #1709
git cherry-pick f4c5a43  # iflix - removed
git cherry-pick b5ae7b6  # bubba, cambro, yespornplease removed
git cherry-pick 71d1398  # vintagetube - removed
git cherry-pick abb53d8  # ividz - removed
git cherry-pick 8655ef5  # asstoo & bitporno - removed
git cherry-pick 91d2249  # americass - removed (duplicate check)
git cherry-pick da3a465  # asianporn - removed
git cherry-pick 24b5b73  # amateurcool - removed
```

**Total Phase 3**: 9 commits  
**Testing**: Verify sites no longer appear in menu

---

## Phase 4: NEW SITES (Selective Addition) 🆕

### High Quality / Popular (Recommended)
```bash
git cherry-pick 8eae561  # fullxcinema
git cherry-pick 122e955  # freepornvideos - new site
git cherry-pick 67bd60f  # tokyomotion - new site (Japanese)
git cherry-pick ba754a5  # xxdbx - new site
git cherry-pick 8301e4d  # 85po - new site (includes hdporn92 fix)
git cherry-pick 4e2c8e0  # premiumporn - new site
git cherry-pick 750c731  # Netflav - new site (JAV)
git cherry-pick 464392c  # PornTN - new site
```

### Consider Based on Demand
```bash
# Review these before applying:
git show 6449cad  # xsharings - new site
git show e3246a1  # longvideos - new site
git show 84fa2f4  # terebon - new site
git show d68a825  # fulltaboo, koreanpornmovie - new sites
git show 5a7bf2c  # Porno1hu - new site
git show 42aaa0a  # Fuxmovies - new site
git show 9af43e2  # WatchMDH - new site
git show f57d9db  # Porn4k.to - new site
git show 20af76e  # EroticMV - new site
git show 5030432  # DrTuber - new site
git show c3924de  # Fullporner - new site
git show 5b6a091  # WhereIsMyPorn - new site
```

**Total Phase 4**: 8-20 commits (selective)  
**Testing**: Test each new site thoroughly (listing, search, playback)

---

## Phase 5: MEDIUM-PRIORITY FIXES (As Needed) ⚙️

### AWM Network Sites
```bash
git cherry-pick afe1ff0  # celebsroulette, awmnet
git cherry-pick 759d910  # AWM Network - fix listing fixes #1673
git cherry-pick 61e7be5  # awm network - fix listing #1655
git cherry-pick 5df2e5f  # awmnet, familypornhd - playback
git cherry-pick c267672  # awmnet - fix categories, tgs, pornstars
git cherry-pick b806f1f  # awmnet - update site list fixes #1680
git cherry-pick d522ced  # awmnet - fix listing
```

### Cam Sites
```bash
git cherry-pick d47192d  # camsoda #1685
git cherry-pick 9722f3e  # camwhoresbay - fix next page
git cherry-pick b4beb80  # camwhoresbay - fix playback
git cherry-pick e40d58d  # camcaps site name change
```

### Other Site Fixes
```bash
git cherry-pick c11caeb  # pornhoarder fixes #1713
git cherry-pick 53a9dfe  # whoreshub fixes #1715
git cherry-pick d92bd04  # tnaflix fixes #1718
git cherry-pick 0509d5b  # premiumporn - fixes #1714
git cherry-pick 51c39fb  # porntn fixes #1720
git cherry-pick 90d2f5a  # pornxp - domain change - fixes #1711
git cherry-pick 1721e03  # terebon - fix playback
git cherry-pick a34c0a7  # terebon - fix listing
git cherry-pick 6df953b  # familypornhd - fix sound - fixes #1682
git cherry-pick f2de1aa  # familypornhd - fix playback fixes #1678
git cherry-pick 97de93c  # aagmaalpro domain change
```

**Total Phase 5**: ~22 commits  
**Testing**: Test affected sites based on user reports

---

## Commits to SKIP ❌

### All Version Bumps (314 commits)
```bash
# DO NOT cherry-pick any commit with "Bumped to v.X.X.XXX"
# Examples:
# c9f1144 - 2025-12-28 Bumped to v.1.1.163
# d7581d5 - 2025-12-07 Bumped to v.1.1.162
# b8e1df5 - 2025-11-30 Bumped to v.1.1.161
# ... (311 more)
```

### Packaging-Only Commits
```bash
# DO NOT cherry-pick commits that only change .zip files or metadata
# Example: b4daafc - "fixes" (empty commit)
```

---

## Conflict Resolution

### If BeautifulSoup conflict occurs:
```bash
# Fork has migrated sites to BeautifulSoup
# Upstream still uses regex
# Resolution: Keep fork's BeautifulSoup version
git checkout --ours <file>  # Keep fork's version
git add <file>
git cherry-pick --continue
```

### If version conflict in addon.xml:
```bash
# Always keep fork's version number (1.1.209+)
git checkout --ours plugin.video.cumination/addon.xml
git add plugin.video.cumination/addon.xml
git cherry-pick --continue
```

### If test conflict occurs:
```bash
# Fork has extensive tests, upstream doesn't
# Keep fork's test infrastructure
git checkout --ours tests/
git add tests/
git cherry-pick --continue
```

---

## Testing Checklist

After each phase:

- [ ] `python run_tests.py` - All tests pass
- [ ] `ruff check plugin.video.cumination/resources/lib/` - No new errors
- [ ] Manual site testing (2-3 sites per phase minimum)
- [ ] Addon menu loads without errors
- [ ] Search functionality works
- [ ] Video playback works
- [ ] No Python exceptions in kodi.log

---

## Progress Tracking

Use this checklist to track progress:

- [ ] Phase 1: Critical Fixes (8 commits) - PRIORITY 1
- [ ] Phase 2: Popular Site Fixes (19 commits) - PRIORITY 2
- [ ] Phase 3: Site Cleanup (9 commits) - PRIORITY 3
- [ ] Phase 4: New Sites (8-20 commits) - PRIORITY 4
- [ ] Phase 5: Medium-Priority Fixes (22 commits) - PRIORITY 5

**Total recommended**: 66-78 commits minimum, up to ~150 if all are applied.

---

## Quick Command Summary

```bash
# Set up upstream remote (if not done)
git remote add upstream https://github.com/dobbelina/repository.dobbelina.git
git fetch upstream

# Start from clean state
git checkout copilot/update-fork-with-commits
git pull origin copilot/update-fork-with-commits

# Apply Phase 1 (example)
git cherry-pick 673fe9b 7bbe1c7 3a98f37 fb3243d 86946aa 24d0b16

# If conflicts
git status  # See conflicted files
# Edit files to resolve conflicts
git add <resolved-files>
git cherry-pick --continue

# Test
python run_tests.py
# Manual testing...

# Commit and push
git push origin copilot/update-fork-with-commits
```

---

## Estimated Timeline

| Phase | Commits | Testing Time | Total Time |
|-------|---------|--------------|------------|
| Phase 1 | 8 | 2 hours | ~4 hours |
| Phase 2 | 19 | 4 hours | ~8 hours |
| Phase 3 | 9 | 1 hour | ~2 hours |
| Phase 4 | 8-20 | 6 hours | ~12 hours |
| Phase 5 | 22 | 4 hours | ~8 hours |
| **Total** | **66-78** | **17 hours** | **~34 hours** |

Add buffer for conflict resolution: **+10 hours**  
**Grand total**: **~44 hours** (approximately 1 week of full-time work)

---

## Next Steps

1. Review this document with team/stakeholders
2. Get approval to proceed
3. Start with Phase 1 (Critical Fixes)
4. Test thoroughly after each phase
5. Document any issues encountered
6. Update this document with lessons learned
