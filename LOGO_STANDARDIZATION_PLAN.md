# Cumination Logo Standardization Plan

## Executive Summary

**Current State:**
- 137 site modules active
- 130 logo files exist (but some are orphaned)
- 89 sites have working logos
- 48 sites missing logos entirely
- 35 orphaned logos from removed sites
- Dimensions: 16x16px to 752x93px (wildly inconsistent)
- File sizes: 0.4 KB to 191 KB
- Formats: 121 PNG, 8 JPG, 1 GIF, 1 uppercase .PNG

**Problems:**
1. Inconsistent dimensions (16x16 to 752x93) create poor UX in Kodi
2. Mixed formats (PNG/JPG/GIF) with uppercase extension causing issues
3. 48 sites referencing remote URLs instead of local logos
4. 35 orphaned files wasting 280+ KB of space
5. Some logos are microscopic (16x16), others huge (512x512)
6. File sizes vary from 400 bytes to 191 KB
7. Many logos have poor aspect ratios (non-square)

**Target State:**
- All 137 sites have local PNG logos
- Standardized dimensions: **256x256 pixels**
- Optimized file size: **5-30 KB** per logo
- Consistent format: **PNG with transparency**
- No orphaned files
- All logos professionally processed and visually consistent

---

## Logo Standards (NEW)

### Required Specifications

**Dimensions:** 256x256 pixels (square aspect ratio)

**Format:** PNG (Portable Network Graphics)
- 24-bit color with 8-bit alpha channel
- Transparency supported and encouraged
- sRGB color space

**File Size:** Target 5-30 KB
- Minimum: 2 KB (acceptable for simple text logos)
- Maximum: 50 KB (hard limit)
- Optimal: 10-20 KB (good balance)

**File Naming:**
- Must match site identifier EXACTLY (case-sensitive)
- Format: `[siteid].png` (all lowercase)
- Example: `pornhub.png`, `xvideos.png`, `hentaidude.png`

**Visual Quality:**
- Clear and recognizable at 256x256
- Professional appearance
- No watermarks or artifacts
- Transparent background (preferred) or solid color
- Centered logo with adequate padding

**Directory:** `plugin.video.cumination/resources/images/`

### Rationale for 256x256

**Why 256x256?**
1. Kodi skin compatibility - most skins scale well at this size
2. Perfect square for consistent UI alignment
3. High enough quality for HD displays (1080p/4K)
4. Low enough file size when optimized
5. Industry standard for app/addon icons
6. 2^8 (power of 2) for efficient image processing

**Why not other sizes?**
- 512x512: Too large, bloated file sizes (50-200 KB)
- 128x128: Too small, pixelated on HD displays
- 64x64: Way too small, unusable on modern TVs
- Non-square: Creates alignment issues in Kodi UIs

---

## Implementation Strategy

### Phase 1: Cleanup (Priority: HIGH)

**Task 1.1: Remove Orphaned Logos (35 files)**

Delete these logos that are no longer referenced by any site:

```
12milf.png          fulltaboo.png       okporn.png          tporn.png
cpv.png             hclips.png          okxxx.png           tubepornclassic.png
desiporn.png        hdpornbay.png       pornstarstube.png   upornia.png
elreyx.png          hdzog.png           porntubenl.png      vjav.png
helloporn.png       pornzog.png         voyeurhit.png
homoxxx.PNG         seexxx.png          xt.png
hotmovs.png         sextube.png
icon.png            shemalez.png
inporn.png          thegay.png
javbuz.png
javhihi.png
k18.png
letfap.png
lpv.png
manysex.png
maxporn.png
```

**Estimated space savings:** ~280 KB

**Task 1.2: Rename Uppercase Extension**
- `homoxxx.PNG` → `homoxxx.png` (or delete if orphaned)

---

### Phase 2: Fix Sites Using Remote URLs (Priority: HIGH)

**48 sites currently reference remote logos instead of local files:**

These need logos downloaded, processed, and saved locally:

| Site ID | Current Remote URL | New Local File |
|---------|-------------------|----------------|
| avple | https://assert.avple.tv/file/avple-images/logo.png | avple.png |
| celebsroulette | https://celebsroulette.com/images/logo.png | celebsroulette.png |
| eporner | https://static-eu-cdn.eporner.com/new/logo.png | eporner.png |
| erome | https://www.erome.com/img/logo-erome-horizontal.png | erome.png |
| eroticage | https://www.eroticage.net/wp-content/uploads/2021/08/eroticage-logo.jpg | eroticage.png |
| eroticmv | https://eroticmv.com/wp-content/uploads/2019/10/logo-2.png | eroticmv.png |
| familypornhd | https://familypornhd.com/wp-content/uploads/2020/06/Light-normal.png | familypornhd.png |
| fullporner | https://fullporner.org/wp-content/uploads/2023/04/logo-1.png | fullporner.png |
| hentaidude | https://hentaidude.xxx/wp-content/uploads/2021/03/Hentai-Dude.png | hentaidude.png |
| hentaistream | https://hstream.moe/images/hs_banner.png | hentaistream.png |
| heroero | https://www.heroero.com/images/logo.png | heroero.png |
| hitprn | https://www.hitprn.com/wp-content/uploads/2021/03/hitprn-logo.png | hitprn.png |
| hobbyporn | https://hobby.porn/static/images/logo.png | hobbyporn.png |
| homemoviestube | https://www.homemoviestube.com/images/logo.png | homemoviestube.png |
| hpjav | https://hpjav.in/wp-content/themes/HPJAV/images/logo.png | hpjav.png |
| japteenx | https://jtx.ilfcdn.li/images/logo/logo.png | japteenx.png |
| javgg | https://javgg.co/javggclub.png | javgg.png |
| javguru | https://cdn.javsts.com/wp-content/uploads/2018/12/logofinal6.png | javguru.png |
| javhdporn | https://pics.pornfhd.com/javhdporn/logo.png | javhdporn.png |
| justfullporn | https://justfullporn.net/wp-content/uploads/2024/12/cropped-Made_with_FlexClip_AI-2024-12-26T013132-removebg-preview.png | justfullporn.png |
| luxuretv | https://luxuretv.com/images/logo.png | luxuretv.png |
| netfapx | https://netfapx.com/wp-content/uploads/2017/11/netfapx-lg-1_319381e1f227e13ae1201bfa30857622.png | netfapx.png |
| netflav | https://netflav.com/static/assets/logo.png | netflav.png |
| peachurnet | https://peachurnet.com/favicon-32x32.png | peachurnet.png |
| peekvids | https://www.peekvids.com/img/logo.png | peekvids.png |
| porn4k | https://porn4k.to/wp-content/uploads/2022/04/banner.png | porn4k.png |
| porndish | https://www.porndish.com/wp-content/uploads/2022/03/logo.png | porndish.png |
| porngo | https://www.porngo.com/img/logo.png | porngo.png |
| pornmz | https://pornmz.com/wp-content/uploads/2021/03/PornMZ.png | pornmz.png |
| porno1hu | https://porno1.hu/static/images/logo.png | porno1hu.png |
| porno365 | http://m.porno365.pics/settings/l8.png | porno365.png |
| porntn | https://porntn.com/static/images/logo.png | porntn.png |
| pornxp | https://pornxp.com/logo2.png | pornxp.png |
| rlc | https://reallifecam.to/images/logo/logo.png | reallifecam.png |
| tabootube | https://www.tabootube.xxx/contents/other/theme/logo.png | tabootube.png |
| theyarehuge | https://www.theyarehuge.com/static/images/tah-logo-m.png | theyarehuge.png |
| tokyomotion | https://cdn.tokyo-motion.net/img/logo.gif | tokyomotion.png |
| uflash | http://www.uflash.tv/templates/frontend/default/images/logo.png | uflash.png |
| vaginanl | https://c749a9571b.mjedge.net/img/logo-default.png | vaginanl.png |
| watcherotic | https://watcherotic.com/contents/fetrcudmeesb/theme/logo.png | watcherotic.png |
| watchmdh | https://watchdirty.is/contents/playerother/theme/logo.png | watchmdh.png |
| watchporn | https://watchporn.to/contents/djifbwwmsrbs/theme/logo.png | watchporn.png |
| whereismyporn | (needs discovery) | whereismyporn.png |
| xmoviesforyou | https://xmoviesforyou.com/wp-content/uploads/2018/08/logo.png | xmoviesforyou.png |
| xnxx | https://static-cdn77.xnxx-cdn.com/v3/img/skins/xnxx/logo-xnxx.png | xnxx.png |
| xozilla | https://i.xozilla.com/images/logo.png | xozilla.png |
| xsharings | https://xsharings.com/wp-content/uploads/2025/05/Sharinglg5.png | xsharings.png |
| xtheatre | https://pornxtheatre.com/wp-content/uploads/2020/06/ggf.png | xtheatre.png |
| xxdbx | https://xxdbx.com/l.png | xxdbx.png |

**Note:** Several sites reference logos with URLs that may be dead or require scraping from homepage. Priority should be given to actively maintained sites.

---

### Phase 3: Standardize Existing Logos (Priority: MEDIUM)

**Task 3.1: Convert Non-PNG Formats**

Convert these to PNG:
- `absoluporn.gif` → `absoluporn.png`
- `awmnet.jpg` → `awmnet.png`
- `cumlouder.jpg` → `cumlouder.png`
- `freshporno.jpg` → `freshporno.png`
- `myfreecams.jpg` → `myfreecams.png`
- `pornhoarder.jpg` → `pornhoarder.png`
- `pornroom.jpg` → `pornroom.png`
- `stripchat.jpg` → `stripchat.png`
- `vvp.jpg` → `vvp.png`

**Task 3.2: Resize All Logos to 256x256**

**Extremely undersized logos (require upscaling):**
- motherless.png (16x16) → 256x256
- redtube.png (16x16) → 256x256
- youjizz.png (32x32) → 256x256
- youporn.png (48x48) → 256x256
- beeg.png (64x53) → 256x256

**Oversized logos (require downscaling):**
- icon.png (512x512) → 256x256 (or DELETE if orphaned)
- hanime.png (512x512) → 256x256
- pornroom.jpg (512x512) → 256x256
- tubepornclassic.png (752x93) → 256x256
- amateurtv.png (677x310) → 256x256

**Non-square logos (require padding/centering):**
- Most logos are non-square and will need transparent padding to reach 256x256

---

### Phase 4: Optimize File Sizes (Priority: MEDIUM)

**Current outliers:**
- icon.png: 191 KB → target ~15 KB
- cumlouder.jpg: 52 KB → target ~20 KB
- hanime.png: 53 KB → target ~20 KB
- pornroom.jpg: 53 KB → target ~20 KB
- elreyx.png: 66 KB (orphan, DELETE)

**Optimization techniques:**
1. PNG compression with tools like `pngquant` or `optipng`
2. Remove metadata/EXIF data
3. Reduce color palette where appropriate
4. Use 8-bit PNG instead of 24-bit for simple logos

**Target distribution:**
- Simple text logos: 5-15 KB
- Moderate complexity: 15-25 KB
- Complex/colorful: 25-40 KB
- Maximum allowed: 50 KB

---

### Phase 5: Update Site Modules (Priority: HIGH)

**Task 5.1: Update site modules to reference local files**

For all 48 sites currently using remote URLs, update their `AdultSite()` constructor:

**Before:**
```python
site = AdultSite('avple', '[COLOR hotpink]Avple[/COLOR]',
                 'https://avple.tv/',
                 'https://assert.avple.tv/file/avple-images/logo.png',
                 'avple')
```

**After:**
```python
site = AdultSite('avple', '[COLOR hotpink]Avple[/COLOR]',
                 'https://avple.tv/',
                 'avple.png',
                 'avple')
```

**Task 5.2: Fix mismatched references**

Some sites may reference logos with wrong names. Verify ALL site modules reference the correct filename.

---

### Phase 6: Automation & Validation (Priority: LOW)

**Task 6.1: Create automated logo validation script**

Script should check:
- [ ] All site modules reference local logos (no http:// or https://)
- [ ] All referenced logos exist in resources/images/
- [ ] All logos are exactly 256x256 pixels
- [ ] All logos are PNG format
- [ ] All logos are under 50 KB
- [ ] No orphaned logos exist
- [ ] All filenames match site IDs

**Task 6.2: Create logo download/processing script**

Script to automate:
1. Download logo from URL
2. Convert to PNG if needed
3. Resize to 256x256 with padding
4. Optimize file size
5. Save with correct filename

---

## Tools & Resources

### Recommended Tools

**Command-line (batch processing):**
- **ImageMagick:** Resize, convert, pad images
  ```bash
  # Resize and pad to 256x256 with transparent background
  magick input.png -resize 256x256 -background none -gravity center -extent 256x256 output.png

  # Convert JPG to PNG with transparency
  magick input.jpg -background none -alpha set output.png

  # Optimize PNG
  magick output.png -strip -quality 90 output.png
  ```

- **pngquant:** Lossy PNG compression
  ```bash
  pngquant --quality=80-95 --ext .png --force input.png
  ```

- **optipng:** Lossless PNG optimization
  ```bash
  optipng -o7 input.png
  ```

**Online tools (individual processing):**
- **TinyPNG:** Excellent PNG compression (https://tinypng.com/)
- **Photopea:** Web-based Photoshop alternative (https://www.photopea.com/)
- **Remove.bg:** Background removal (https://www.remove.bg/)
- **Squoosh:** Image optimization (https://squoosh.app/)

**Desktop applications:**
- **GIMP:** Free image editor
- **Adobe Photoshop:** Professional (paid)
- **Inkscape:** Vector graphics (good for SVG logos)

### Processing Workflow

**For each logo:**

1. **Obtain source:**
   - Download from site's homepage
   - Use browser DevTools to find highest resolution
   - Check for SVG version (best quality)
   - Look for press kit or brand assets

2. **Process:**
   ```bash
   # Download
   curl -o temp_logo.png "https://example.com/logo.png"

   # Convert to PNG if needed
   magick temp_logo.jpg temp_logo.png

   # Remove background (if needed)
   # Use remove.bg or Photopea for manual editing

   # Resize to 256x256 with transparent padding
   magick temp_logo.png -resize 256x256 -background none -gravity center -extent 256x256 sitename.png

   # Optimize
   optipng -o7 sitename.png
   pngquant --quality=80-95 --ext .png --force sitename.png

   # Verify dimensions and size
   identify sitename.png
   ls -lh sitename.png
   ```

3. **Validate:**
   - Check dimensions: exactly 256x256
   - Check file size: under 50 KB (ideally 10-30 KB)
   - Visual inspection: clear, centered, professional
   - Test in Kodi if possible

4. **Deploy:**
   - Copy to `plugin.video.cumination/resources/images/`
   - Update site module if needed
   - Delete temporary files

---

## Priority Matrix

### Immediate (Week 1)
1. Delete 35 orphaned logos
2. Download and process top 20 missing logos (most popular sites)
3. Fix the smallest logos (16x16, 32x32) that are unusable

### Short-term (Week 2-3)
4. Complete remaining 28 missing logos
5. Convert all JPG/GIF to PNG
6. Resize all existing logos to 256x256

### Medium-term (Week 4)
7. Optimize all logos for file size
8. Update all site modules
9. Create validation script

### Long-term (Ongoing)
10. Monitor for new sites needing logos
11. Re-process logos when sites rebrand
12. Maintain documentation

---

## Success Metrics

**Completion criteria:**
- [ ] 0 orphaned logos
- [ ] 137 sites with local PNG logos
- [ ] 100% of logos are 256x256 pixels
- [ ] 100% of logos are PNG format
- [ ] 100% of logos are under 50 KB
- [ ] Average file size: 10-20 KB
- [ ] All site modules reference local files
- [ ] Validation script passes all checks
- [ ] Documentation updated

**Quality metrics:**
- Visual consistency across all logos
- Professional appearance in Kodi UI
- Fast load times (small file sizes)
- Clear recognition at 256x256
- Proper transparency handling

---

## Appendix A: Site Priority Tiers

### Tier 1: High Traffic Sites (Process First)
pornhub, xvideos, xhamster, xnxx, spankbang, eporner, hqporner, porntrex

### Tier 2: Popular JAV Sites
javgg, javguru, javhdporn, tokyomotion, missav, netflav

### Tier 3: Popular Hentai Sites
hentaidude, hentaistream, heroero, hanime (already has logo)

### Tier 4: Live Cam Sites
(Most already have logos)

### Tier 5: Niche/International Sites
Process last based on maintenance activity

---

## Appendix B: Common Logo Issues & Solutions

**Issue:** Logo has white background instead of transparency
**Solution:** Use Photopea or GIMP to remove background, or use remove.bg

**Issue:** Logo is too small/pixelated
**Solution:** Source higher resolution from site's press kit or SVG

**Issue:** Logo has unusual aspect ratio (very wide or tall)
**Solution:** Add transparent padding to reach square 256x256

**Issue:** Logo file size too large (>50 KB)
**Solution:** Use pngquant with quality 80-90, or reduce to 8-bit PNG

**Issue:** Site has no clear logo, just text
**Solution:** Create text-based logo using site's font/colors

**Issue:** Site logo URL is dead/404
**Solution:** Extract from site's favicon, homepage screenshot, or Wayback Machine

---

## Next Steps

1. Review and approve this plan
2. Set up development environment with ImageMagick
3. Begin Phase 1 (cleanup)
4. Process logos in batches of 10-15
5. Test periodically in Kodi
6. Update CLAUDE.md with logo standards
7. Create validation script
8. Final QA pass
9. Commit and deploy

---

**Document Version:** 1.0
**Created:** 2025-12-20
**Last Updated:** 2025-12-20
**Author:** Claude (Site Branding Specialist)
