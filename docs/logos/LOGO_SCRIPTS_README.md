# Logo Standardization Scripts - User Guide

## Overview

This directory contains a comprehensive suite of Python scripts to standardize all site logos in the Cumination addon. All logo scripts are located in the `scripts/` directory and should be run from the repository root.

## Scripts Summary

| Script | Purpose | When to Use |
|--------|---------|-------------|
| **scripts/validate_logos.py** | Check all logos meet standards | Before/after any changes |
| **scripts/process_logos.py** | Download, convert, resize logos | Main processing tool |
| **scripts/update_site_modules.py** | Update site .py files | After processing logos |
| **scripts/analyze_logos.py** | Detailed analysis and reports | Initial assessment |
| **scripts/get_logo_dimensions.py** | Extract logo dimensions | Manual inspection |

## Prerequisites

### Required: ImageMagick

**All processing scripts require ImageMagick 7.x**

**Windows Installation:**
1. Download: https://imagemagick.org/script/download.php
   - Get: `ImageMagick-7.x.x-Q16-HDRI-x64-dll.exe`
2. Run installer
3. **IMPORTANT:** Check "Add application directory to system path"
4. Restart terminal
5. Verify: `magick --version`

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt install imagemagick

# macOS
brew install imagemagick
```

### Optional: pngquant

For better PNG compression (recommended but not required):

**Windows:** Download from https://pngquant.org/
**Linux:** `sudo apt install pngquant`
**macOS:** `brew install pngquant`

## Workflow

### Step 1: Initial Assessment

Run the validation script to see current state:

```bash
cd "C:/Users/James/Desktop/repository.dobbelina"
python scripts/validate_logos.py
```

**What it checks:**
- Sites using remote URLs vs local files
- Missing logo files
- Orphaned logos
- Format (PNG vs JPG/GIF)
- Dimensions (if ImageMagick installed)
- File sizes

**Output example:**
```
[CHECK 1] Sites using remote URLs...
  FAILED: 50 sites use remote URLs

[CHECK 2] Sites with missing logo files...
  PASSED

[CHECK 3] Orphaned logo files...
  WARNING: 2 orphaned logos found

[CHECK 4] Logo file specifications...
  ISSUES FOUND:
    - Non-PNG formats: 9
    - Wrong dimensions: 47
    - File size issues: 47

SUMMARY
Errors: 50
Warnings: 58
Info: 0
```

### Step 2: Process Logos

Run the main processing script:

```bash
python scripts/process_logos.py
```

**Interactive menu:**
```
Options:
  1. Download and process all missing logos (50 sites)
  2. Convert existing JPG/GIF logos to PNG
  3. Resize all existing logos to 256x256
  4. Validate all logos
  5. Run all tasks (full standardization)
  6. Exit
```

**Recommended:** Choose option 5 to run all tasks automatically.

**What it does:**
- Downloads logos from remote URLs
- Converts JPG/GIF to PNG
- Resizes all logos to 256x256 (with transparent padding)
- Optimizes file sizes
- Validates results

**Processing example:**
```
[1/50] Processing avple...
  Downloading from: https://assert.avple.tv/file/avple-images/logo.png
  Downloaded: 15234 bytes
  Processing: temp_logo.png -> avple.png
  Initial size: 14.9 KB
  Optimized size: 12.3 KB
  [SUCCESS] Processed logo: avple.png (12.3 KB)
```

### Step 3: Update Site Modules

After processing logos, update the site .py files:

```bash
python scripts/update_site_modules.py
```

**Interactive menu:**
```
OPTIONS
1. Create backup and apply changes
2. Apply changes without backup (not recommended)
3. Dry run (show what would change without modifying files)
4. Exit without making changes
```

**Recommended:** Choose option 1 (creates backup before changes).

**What it does:**
- Finds all sites using remote logo URLs
- Changes them to local .png references
- Creates backup of original files
- Shows preview before applying

**Example changes:**
```
BEFORE: 'https://assert.avple.tv/file/avple-images/logo.png'
AFTER:  'avple.png'
```

### Step 4: Final Validation

Run validation again to confirm all changes:

```bash
python scripts/validate_logos.py
```

**Expected result:**
```
[CHECK 1] Sites using remote URLs...
  PASSED

[CHECK 2] Sites with missing logo files...
  PASSED

[CHECK 3] Orphaned logo files...
  PASSED

[CHECK 4] Logo file specifications...
  PASSED

VALIDATION PASSED - ALL LOGOS MEET STANDARDS!
```

## Script Details

### scripts/validate_logos.py

**Purpose:** Comprehensive validation of all logos

**Usage:**
```bash
python scripts/validate_logos.py
```

**Checks performed:**
1. Sites using remote URLs (should be local)
2. Missing logo files
3. Orphaned logos (not referenced)
4. Format (must be PNG)
5. Dimensions (must be 256x256)
6. File sizes (5-50 KB)
7. Filename conventions

**Output:** Color-coded report with errors, warnings, and info

**Exit codes:**
- 0: Validation passed (may have warnings)
- 1: Validation failed (has errors)

---

### scripts/process_logos.py

**Purpose:** Main logo processing and automation tool

**Usage:**
```bash
python scripts/process_logos.py
# Follow interactive menu
```

**Features:**

**Option 1: Download missing logos**
- Extracts URLs from site modules
- Downloads each logo
- Processes to 256x256 PNG
- **NEW:** Automatically creates a placeholder logo if download/processing fails

**Option 2: Convert formats**
- Finds all JPG/GIF logos
- Converts to PNG with transparency
- Deletes original non-PNG files

**Option 3: Resize logos**
- Checks current dimensions
- Resizes to 256x256
- Adds transparent padding for non-square logos
- Preserves aspect ratio

**Option 4: Validate**
- Same as scripts/validate_logos.py
- Convenient integration

**Option 5: Run all**
- Executes options 1, 2, 3, 4 in sequence
- Fully automated standardization

**Option 6: Test a logo source**
- **NEW:** Test any URL or local file to see how it will be processed
- Saves to `[site_id].png` and opens it for preview (Windows only)

**Option 7: Create placeholder logo manually**
- **NEW:** Generate a standardized placeholder logo by entering a site name
- Useful for new sites where a high-quality logo isn't available

**Processing logic:**
```
For each logo:
1. Download (if remote URL)
2. Convert to PNG (if JPG/GIF)
3. Resize to fit 256x256 (maintain aspect ratio)
4. Add transparent padding to reach exactly 256x256
5. Strip metadata
6. Optimize with pngquant (if available)
7. Fallback: Create placeholder if any step fails
8. Validate final size
```

**Temporary files:**
- Created in: `temp_logos/` directory
- Automatically cleaned up after processing
- Can be manually deleted if script crashes

---

### scripts/update_site_modules.py

**Purpose:** Batch update site .py files to use local logos

**Usage:**
```bash
python scripts/update_site_modules.py
# Choose option 1 (with backup)
```

**Safety features:**
- **Automatic backup** of all site modules before changes
- **Dry run mode** to preview changes
- **Validation** that local logos exist before updating
- **Preview** shows all changes before applying

**Backup location:**
```
C:/Users/James/Desktop/repository.dobbelina/site_modules_backup/
```

**To restore from backup:**
```bash
# Copy all files back
cp site_modules_backup/* plugin.video.cumination/resources/lib/sites/
```

**Pattern detection:**
Updates this pattern:
```python
site = AdultSite('siteid', '[COLOR hotpink]Name[/COLOR]',
                 'https://example.com/',
                 'https://example.com/logo.png',  # Remote URL
                 'siteid')
```

To this:
```python
site = AdultSite('siteid', '[COLOR hotpink]Name[/COLOR]',
                 'https://example.com/',
                 'siteid.png',  # Local file
                 'siteid')
```

**Skips sites:**
- Where local logo doesn't exist yet
- That already use local logos
- With parsing errors

---

### scripts/analyze_logos.py

**Purpose:** Detailed analysis and reporting

**Usage:**
```bash
python scripts/analyze_logos.py
```

**Output:**
- Total site modules and logo files
- Sites with missing logos (detailed list)
- Logo format distribution (PNG/JPG/GIF)
- File size statistics (min/max/avg/median)
- Orphaned logos list
- Sites with existing logos count

**Use case:** Initial assessment and detailed reports

---

### scripts/get_logo_dimensions.py

**Purpose:** Extract exact dimensions without PIL dependency

**Usage:**
```bash
python scripts/get_logo_dimensions.py
```

**Output:**
- Full dimension table (width x height x size)
- Sorted by total area
- Statistics (min/max/avg dimensions and sizes)
- Works without any external dependencies

**How it works:**
- Parses PNG/JPG/GIF headers directly
- Uses Python struct module
- No PIL/Pillow required

---

## Logo Standards Reference

### Required Specifications

| Property | Value |
|----------|-------|
| **Format** | PNG (24-bit + alpha) |
| **Dimensions** | 256x256 pixels (square) |
| **File Size** | 5-30 KB (optimal), 50 KB max |
| **Naming** | `[siteid].png` (lowercase) |
| **Location** | `plugin.video.cumination/resources/images/` |
| **Background** | Transparent (preferred) |
| **Color Space** | sRGB |

### Quality Guidelines

**Visual:**
- Clear and recognizable at 256x256
- Centered with adequate padding
- No watermarks or artifacts
- Professional appearance

**Technical:**
- Metadata stripped
- Optimized compression
- Progressive encoding (optional)
- Power-of-2 dimensions for efficiency

---

## Troubleshooting

### "ImageMagick not found"

**Problem:** Scripts can't find ImageMagick

**Solutions:**
1. Verify installation: `magick --version`
2. Restart terminal after installation
3. Check PATH environment variable
4. Reinstall with "Add to PATH" checked
5. Windows: Add manually to PATH: `C:\Program Files\ImageMagick-7.x.x-Q16-HDRI\`

### "Failed to download logo"

**Problem:** Logo URL returns 404 or timeout

**Solutions:**
1. Check if site still exists
2. Visit site and find new logo URL
3. Check if URL requires authentication
4. Try manual download with browser
5. Use Wayback Machine for archived logos
6. Create text-based logo as fallback

### "Orphaned logos found"

**Problem:** Logo files exist but no site references them

**Solutions:**
1. Check if site was recently removed
2. Search site modules for misspelled references
3. Check if site uses different ID
4. Safe to delete if site truly removed
5. Run: `git log --all --full-history -- "plugin.video.cumination/resources/images/[filename]"` to see history

### "File size too large"

**Problem:** Processed logo exceeds 50 KB

**Solutions:**
1. Install pngquant for better compression
2. Reduce color palette (256 colors often sufficient)
3. Remove transparency if not needed
4. Source higher quality SVG if available
5. Manually optimize with TinyPNG.com

### "Wrong dimensions after processing"

**Problem:** Logo not exactly 256x256

**Solutions:**
1. Ensure ImageMagick 7.x installed (not 6.x)
2. Check for errors in processing output
3. Try processing single logo manually
4. Verify input file is valid image
5. Re-run with verbose output

### "Site module not updated"

**Problem:** scripts/update_site_modules.py skipped a site

**Causes:**
1. Local logo doesn't exist - run scripts/process_logos.py first
2. Site already uses local logo - no update needed
3. Regex pattern didn't match - unusual formatting
4. File encoding issue - check for BOM or non-UTF8

**Manual fix:**
```python
# Edit the site .py file directly
# Change line like:
site = AdultSite('siteid', '...', 'https://.../', 'https://.../logo.png', '...')
# To:
site = AdultSite('siteid', '...', 'https://.../', 'siteid.png', '...')
```

---

## Advanced Usage

### Process Single Logo

```bash
# Manual processing with ImageMagick
cd "C:/Users/James/Desktop/repository.dobbelina"

# Download
curl -o temp.png "https://example.com/logo.png"

# Process to 256x256
magick temp.png -background none -gravity center -resize 256x256 -extent 256x256 -strip sitename.png

# Optimize
pngquant --quality=80-95 --ext .png --force sitename.png

# Move to images directory
move sitename.png "plugin.video.cumination/resources/images/"
```

### Batch Process Specific Sites

Edit `scripts/process_logos.py` and modify the `get_sites_needing_logos()` function to filter specific sites:

```python
sites = get_sites_needing_logos()
# Filter to only process specific sites
sites = [s for s in sites if s['site_id'] in ['avple', 'eporner', 'xnxx']]
```

### Custom Validation Rules

Edit `scripts/validate_logos.py` constants:

```python
TARGET_SIZE = "512x512"  # Use larger size
MAX_FILE_SIZE_KB = 100  # Allow larger files
OPTIMAL_FILE_SIZE_RANGE = (10, 50)  # Adjust optimal range
```

### Generate Site Report

```bash
# Get counts by format
python -c "from pathlib import Path; import collections; logos = list(Path('plugin.video.cumination/resources/images').glob('*.png')) + list(Path('plugin.video.cumination/resources/images').glob('*.jpg')); print(collections.Counter(l.suffix for l in logos))"

# Get total size
python -c "from pathlib import Path; logos = Path('plugin.video.cumination/resources/images').glob('*'); print(f'Total: {sum(l.stat().st_size for l in logos if l.is_file())/1024:.0f} KB')"
```

---

## Quick Reference

### Complete Workflow (First Time)

```bash
# 1. Validate current state
python scripts/validate_logos.py

# 2. Process all logos (downloads, converts, resizes)
python scripts/process_logos.py
# Select option 5

# 3. Update site modules
python scripts/update_site_modules.py
# Select option 1

# 4. Final validation
python scripts/validate_logos.py
# Should show all PASSED

# 5. Commit changes
git add plugin.video.cumination/resources/images/*.png
git add plugin.video.cumination/resources/lib/sites/*.py
git commit -m "Standardize all site logos to 256x256 PNG"
```

### Maintenance (Adding New Site)

```bash
# 1. Add logo file
# Save as: plugin.video.cumination/resources/images/newsiteid.png
# Ensure: 256x256 PNG format

# 2. Validate single logo
python -c "from pathlib import Path; import subprocess; f = Path('plugin.video.cumination/resources/images/newsiteid.png'); print(subprocess.run(['magick', 'identify', '-format', '%wx%h %b', str(f)], capture_output=True, text=True).stdout)"

# 3. Run full validation
python scripts/validate_logos.py
```

---

## Support

**For issues or questions:**
1. Check troubleshooting section above
2. Review LOGO_STANDARDIZATION_PLAN.md for detailed documentation
3. Review LOGO_STANDARDIZATION_SUMMARY.md for implementation guide
4. Ask Claude Code for help with specific issues

**Useful commands:**
```bash
# Check logo dimensions
magick identify plugin.video.cumination/resources/images/sitename.png

# Check all logos at once
magick identify -format "%f: %wx%h %b\n" plugin.video.cumination/resources/images/*.png

# Find orphaned logos
python scripts/validate_logos.py | grep -A 20 "CHECK 3"

# Count logos by format
ls plugin.video.cumination/resources/images/*.{png,jpg,gif} 2>/dev/null | wc -l
```

---

**Last Updated:** 2025-12-20
**Script Version:** 1.0
**Compatible with:** Python 3.7+, ImageMagick 7.x
