# Cherry-Pick Analysis: Upstream → Fork

**Upstream**: dobbelina/repository.dobbelina  
**Fork**: rpeters1430/repository.dobbelina  
**Analysis Date**: 2026-02-05

---

## Summary

- **Upstream non-version-bump commits reviewed through**: 2026-02-05
- **Pending cherry-picks**: **0**
- **Tracking source of truth**: `UPSTREAM_SYNC.md`

---

## Category 1: Already Applied ✅

### 2026-02-05 Cherry-Pick Session (Completed)

| Upstream Hash | Message | Fork Hash |
|---------------|---------|-----------|
| `8b2cd89` | sxyprn - fix search fixes #1277 | `25c2afb` |
| `63348e8` | chaturbate favorites - fixes #1745 | `6137f6f` |
| `9ac3255` | allclassic - fixes #1742 | `8e5b74a` |
| `a4e50af` | kissjav - fix thumbnails, playback fixes #1743 | `732cab5` |
| `99dd004` | fix pagination | `c4c3c72` |
| `beb5b9d` | luxuretv - fix nextpage, thumbnails | `95f32d6` |

### Previously Integrated (Manual or Earlier Cherry-Picks)

See `UPSTREAM_SYNC.md` for the full list of:
- Manually integrated upstream commits
- Cherry-picked commits with `-x`
- Intentionally skipped commits (e.g., superseded by BeautifulSoup migrations)

---

## Category 2: Pending Cherry-Picks 🔄

**None at this time.**  
Run the sync checker to verify:
```powershell
.\scripts\check_upstream_sync.ps1
```

---

## Category 3: Recommended Workflow

```bash
# Run the automated sync manager
python scripts/sync_manager.py
```

The script automates:
- Fetching upstream
- Identifying new commits not in fork
- Auto-skipping BS4-migrated sites
- Cherry-picking with tracking
- Updating `UPSTREAM_SYNC.md`

---

## Notes

1. **Changelog conflicts**: Upstream often updates `plugin.video.cumination/changelog.txt`. Prefer keeping fork history and add a single line for new fixes.
2. **LuxureTV**: Updated to `https://en.luxuretv.com/` with thumbnail encoding fix.
3. **Easynews**: Added by upstream in `beb5b9d`.
4. **Skipped commits**: Any intentionally skipped items are documented in `UPSTREAM_SYNC.md`.
