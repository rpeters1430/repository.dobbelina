# Cherry-Pick Analysis: Upstream → Fork

**Upstream**: dobbelina/repository.dobbelina
**Fork**: rpeters1430/repository.dobbelina
**Analysis Date**: 2026-01-04

---

## Summary

- **Total upstream commits (excluding version bumps)**: 33
- **Already applied in fork**: 10
- **Available to cherry-pick**: 23

---

## Category 1: Already Applied ✅

These commits have similar changes already in the fork (different commit hashes):

| Upstream Hash | Message | Status |
|---------------|---------|--------|
| `673fe9b` | fix module load error on TvOS #1724 | ✅ In fork as `07aafdc` |
| `8eae561` | fullxcinema | ✅ In fork as `ef3a914` |
| `3a98f37` | Python 2 fixes #1722 fixes #1663 | ✅ In fork as `f9e4c51` |
| `c11caeb` | pornhoarder fixes #1713 | ✅ In fork as `b4a998e` |
| `31644dc` | pornhub fixes #1712 | ✅ In fork as `1888b76` |
| `53a9dfe` | whoreshub fixes #1715 | ✅ In fork as `ab66f4f` |
| `0509d5b` | premiumporn - fixes #1714 | ✅ In fork as `8ee8f7f` |
| `51c39fb` | porntn fixes #1720 | ✅ In fork as `5e1458b` |
| `afe1ff0` | celebsroulette, awmnet | ✅ In fork as `dfbc225` |
| `b4daafc` | fixes | ✅ Similar fixes likely applied |

---

## Category 2: Recommended Cherry-Picks 🔄

### High Priority (Bug Fixes & Critical Issues)

| Upstream Hash | Message | Files Changed | Impact |
|---------------|---------|---------------|--------|
| `7bbe1c7` | Fix video playback for FlareSolverr scraped sites (e.g. luxuretv) | utils.py | 🔴 **CRITICAL** - Fixes playback for multiple sites |
| `004f106` | luxuretv - fix nextpage, fixes #1734 | luxuretv.py | 🟠 High - Pagination fix |
| `b075cbd` | luxuretv - fix nextpage | luxuretv.py | 🟠 High - Related to above |
| `d92bd04` | tnaflix fixes #1718 | tnaflix.py | 🟠 High - Site fix |
| `e96ed9b` | stripchat - fix playback (SD only) fixes #1710 | stripchat.py | 🟠 High - Playback fix |
| `b4beb80` | camwhoresbay - fix playback | camwhoresbay.py | 🟠 High - Playback fix |
| `9722f3e` | camwhoresbay - fix next page | camwhoresbay.py | 🟠 High - Pagination fix |
| `60b6859` | hanime playback - fixes #1688 | hanime.py | 🟠 High - Playback fix |
| `86d995a` | hanime fixes #1686 | hanime.py | 🟠 High - Site fix |
| `d47192d` | camsoda #1685 | camsoda.py | 🟠 High - Site fix |
| `f3d48c1` | xhmster playback | xhamster.py, xhamster_decrypt.py | 🟠 High - Playback fix |

### Medium Priority (Feature Enhancements)

| Upstream Hash | Message | Files Changed | Impact |
|---------------|---------|---------------|--------|
| `af3c079` | porntn liting, fixes #1731 | porntn.py, xhamster.py, awmnet.py, fyxxr.py (renamed from watchmdh.py) | 🟡 Medium - Multiple site updates + new site fyxxr |
| `90d2f5a` | pornxp - domain change - fixes #1711 | pornxp.py | 🟡 Medium - Domain update |
| `d522ced` | awmnet - fix listing | awmnet.py | 🟡 Medium - Listing fix |
| `a34c0a7` | terebon - fix listing | terebon.py | 🟡 Medium - Listing fix |
| `1721e03` | terebon - fix playback | terebon.py | 🟡 Medium - Playback fix |
| `e40d58d` | camcaps site name change | reallifecam.py, about files | 🟡 Medium - Site rename (camcapsto → simpvids) |

### New Sites

| Upstream Hash | Message | Files Changed | Impact |
|---------------|---------|---------------|--------|
| `122e955` | freepornvideos - new site | freepornvideos.py + media | 🟢 New site addition |
| `67bd60f` | tokyomotion - new site fixes #1689 | tokyomotion.py | 🟢 New site addition |

### Site Removals

| Upstream Hash | Message | Files Changed | Impact |
|---------------|---------|---------------|--------|
| `43c6322` | americass - removed fixes #1709 | Remove americass.py | ⚪ Removal - site defunct |
| `f4c5a43` | iflix - removed | Remove iflix.py | ⚪ Removal - site defunct |
| `b5ae7b6` | bubba, cambro, yespornplease removed | Remove 3 sites | ⚪ Removal - sites defunct |
| `71d1398` | vintagetube - removed | Remove vintagetube.py | ⚪ Removal - site defunct |

---

## Category 3: Recommended Cherry-Pick Strategy

### Option A: Cherry-pick all non-conflicting commits (Recommended)
```bash
# Cherry-pick critical fixes first
git cherry-pick 7bbe1c7  # FlareSolverr playback fix
git cherry-pick 004f106  # luxuretv nextpage
git cherry-pick b075cbd  # luxuretv nextpage (duplicate/related)
git cherry-pick d92bd04  # tnaflix
git cherry-pick e96ed9b  # stripchat playback
git cherry-pick b4beb80  # camwhoresbay playback
git cherry-pick 9722f3e  # camwhoresbay nextpage
git cherry-pick 60b6859  # hanime playback
git cherry-pick 86d995a  # hanime fixes
git cherry-pick d47192d  # camsoda
git cherry-pick f3d48c1  # xhamster playback

# Then feature updates
git cherry-pick af3c079  # porntn, xhamster, awmnet, fyxxr
git cherry-pick 90d2f5a  # pornxp domain
git cherry-pick d522ced  # awmnet listing
git cherry-pick a34c0a7  # terebon listing
git cherry-pick 1721e03  # terebon playback
git cherry-pick e40d58d  # camcaps rename

# New sites
git cherry-pick 122e955  # freepornvideos
git cherry-pick 67bd60f  # tokyomotion

# Removals (optional - your choice)
git cherry-pick 43c6322  # remove americass
git cherry-pick f4c5a43  # remove iflix
git cherry-pick b5ae7b6  # remove bubba, cambro, yespornplease
git cherry-pick 71d1398  # remove vintagetube
```

### Option B: Cherry-pick only critical bug fixes
```bash
git cherry-pick 7bbe1c7  # FlareSolverr - CRITICAL
git cherry-pick 004f106  # luxuretv
git cherry-pick d92bd04  # tnaflix
git cherry-pick e96ed9b  # stripchat
git cherry-pick f3d48c1  # xhamster
```

### Option C: Interactive cherry-pick with review
```bash
# Review each commit before applying
for commit in 7bbe1c7 004f106 d92bd04 e96ed9b b4beb80 9722f3e 60b6859 86d995a d47192d f3d48c1; do
    git show $commit
    read -p "Cherry-pick $commit? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git cherry-pick $commit
    fi
done
```

---

## Notes

1. **Conflict Resolution**: Some commits may conflict with your fork's changes. Review each conflict carefully.

2. **Version Numbers**: All version bumps have been excluded from this analysis as requested.

3. **Testing**: After cherry-picking, run tests to ensure nothing breaks:
   ```bash
   python run_tests.py
   python run_tests.py --coverage
   ```

4. **Changelog**: The upstream commits include changelog entries. You may want to merge/update these manually.

5. **Already Applied Commits**: The 10 commits marked as "already applied" have similar changes in your fork but different commit hashes. This is normal for a fork workflow.

6. **Site Removals**: Consider whether you want to keep defunct sites or remove them. The upstream has removed several broken sites.

---

## Quick Commands Reference

```bash
# View upstream remote
git remote -v

# Update upstream commits
git fetch upstream

# View a specific commit
git show <commit-hash>

# Cherry-pick a commit
git cherry-pick <commit-hash>

# Abort a cherry-pick if there are conflicts
git cherry-pick --abort

# Continue after resolving conflicts
git cherry-pick --continue

# View what changed in a commit
git show --stat <commit-hash>
```

---

## Next Steps

1. Review the recommended commits above
2. Choose a cherry-pick strategy (A, B, or C)
3. Execute the cherry-picks
4. Resolve any conflicts
5. Run full test suite
6. Update version and changelog as needed
