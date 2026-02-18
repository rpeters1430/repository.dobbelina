# Logo Fix Script Guide

## Overview

The `scripts/fix_all_logos.py` script automatically:
1. ✅ **Verifies** all site logos are present and correctly configured
2. 🔧 **Updates** site code to use local PNG files instead of remote URLs
3. 🔨 **Fixes** file extension mismatches (e.g., .jpg → .png)
4. ⬇️ **Downloads** missing logos from actual sites
5. 🎨 **Processes** logos to standard 256x256 PNG format

## Current Status

As of the last scan, the addon has:
- ✅ **134 sites** with working local logos
- 🔧 **2 sites** using remote URLs (but local files exist)
- 🔨 **1 site** with wrong file extension
- ❌ **33 sites** missing logo files

**Total fixes needed: 36**

## Usage

### 1. Dry Run (Recommended First)

See what would be fixed without making any changes:

```bash
python3 scripts/fix_all_logos.py --dry-run
```

### 2. Interactive Mode

Run with confirmation prompt:

```bash
python3 scripts/fix_all_logos.py
```

You'll be asked to confirm before making changes.

### 3. Automatic Mode

Run without confirmation (useful for CI/CD):

```bash
python3 scripts/fix_all_logos.py --yes
```

## Requirements

- **Python 3.7+**
- **ImageMagick** - For image processing
  - Install: https://imagemagick.org/script/download.php
  - On Ubuntu/Debian: `sudo apt install imagemagick`
  - On macOS: `brew install imagemagick`
- **BeautifulSoup4** - For HTML parsing (already in requirements)
- **pngquant** (optional) - For better PNG optimization

## What The Script Does

### Step 1: Extension Fixes (1 site)
- **viralvideosporno**: Changes `vvp.jpg` → `vvp.png` in code

### Step 2: Code Updates (2 sites)
Updates these sites to use local files instead of remote URLs:
- **perverzija**: Already has `perverzija.png` locally
- **vaginanl**: Already has `vaginanl.png` locally

### Step 3: Logo Downloads (33 sites)
Downloads and processes logos for these sites:

#### From Multi-Site Modules:
- **pornhat.py** (6 sites): helloporn, okporn, okxxx, pornstarstube, maxporn, homoxxx, perfectgirls
- **txxx.py** (13 sites): tubepornclassic, voyeurhit, hclips, hdzog, vjav, shemalez, upornia, pornzog, manysex, hotmovs, tporn, seexxx, thegay, inporn, desiporn
- **reallifecam.py** (4 sites): vh, vhlife, vhlife1, camcaps
- **nltubes.py** (3 sites): sextube, 12milf, porntubenl
- **erogarga.py** (2 sites): fulltaboo, koreanpm

#### Standalone Sites:
- livecamrips, sexyporn

## How It Downloads Logos

The script tries multiple methods to find logos:

1. **Remote URL** (if site already has one configured)
2. **Favicon from HTML** - Parses the site's homepage for:
   - `<link rel="icon">`
   - `<link rel="shortcut icon">`
   - `<link rel="apple-touch-icon">`
   - Standard `/favicon.ico`
3. **Fallback** - Tries standard favicon.ico location

Once downloaded, logos are:
- Converted to PNG format
- Resized to 256x256 pixels (with padding if needed)
- Optimized to < 50KB
- Stripped of metadata

## Troubleshooting

### "Failed to download" errors

Some sites may fail to download due to:
- Cloudflare protection
- Rate limiting
- Site temporarily down
- No favicon available

**Solution**: Manually download the logo from the site and place it in:
```
plugin.video.cumination/resources/images/{site_id}.png
```

Then run the script again to update the code.

### ImageMagick not found

Install ImageMagick:
- **Linux**: `sudo apt install imagemagick`
- **macOS**: `brew install imagemagick`
- **Windows**: Download from https://imagemagick.org/script/download.php

### Logo quality issues

For better optimization, install pngquant:
- **Linux**: `sudo apt install pngquant`
- **macOS**: `brew install pngquant`
- **Windows**: https://pngquant.org/

## After Running

After the script completes:

1. **Check the summary** for any failed downloads
2. **Test in Kodi** - Install the addon and verify logos display
3. **Commit changes** if everything looks good:
   ```bash
   git add plugin.video.cumination/resources/lib/sites/*.py
   git add plugin.video.cumination/resources/images/*.png
   git commit -m "fix: update and download missing site logos"
   ```

## Manual Logo Updates

If you need to manually add/update a logo:

1. **Download** the logo file (any format: PNG, JPG, GIF, ICO, SVG)
2. **Process** it using ImageMagick:
   ```bash
   magick input.png -background none -gravity center \
     -resize 256x256 -extent 256x256 -strip output.png
   ```
3. **Place** in `plugin.video.cumination/resources/images/{site_id}.png`
4. **Update** site code to reference `{site_id}.png`

## Statistics

Based on current analysis:
- **Total sites**: 170
- **Working logos**: 134 (78.8%)
- **Needs fixes**: 36 (21.2%)
  - Extension fixes: 1
  - Code updates: 2
  - Missing logos: 33

After running this script, you should have **100% logo coverage**! 🎉
