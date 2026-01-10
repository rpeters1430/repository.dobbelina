# PeachUrNet Bug Fixes

**Date**: 2026-01-10
**Issue**: Videos showing only duration (no titles) and playback failing

## Problems Identified

### 1. **Missing Video Titles**
**Symptom**: Video list shows only duration (e.g., "15:30") instead of video names

**Root Cause**: The `_extract_title()` function was falling back to extracting ALL text from the video link element, which included the duration. When no specific title element was found, it would return the duration as the title.

**Fix**: Enhanced title extraction with multiple strategies:
- Added more title selector patterns (`.name`, `.video-name`)
- Try `img alt` attribute as fallback (common pattern on video sites)
- Try `title` and `aria-label` attributes on the link
- Filter out duration-only text (patterns like `12:34` or `1:23:45`)
- Skip number-only parts when parsing all text

### 2. **Video Playback Failure**
**Symptom**: Clicking on videos throws "cannot find video url" error

**Root Cause**: The `_gather_video_sources()` function wasn't comprehensive enough to handle different video player structures the site might be using.

**Fix**: Expanded video source detection with:
- More data attribute patterns (`data-quality-src`, `data-video-src`)
- Direct video tag `src` attributes
- Better iframe filtering (skip ads/tracking)
- Additional regex patterns for JavaScript-embedded video URLs:
  - `src: "video.mp4"` patterns
  - `file: "video.mp4"` patterns
  - `source: "video.mp4"` patterns
- Improved logging to help debug future issues

### 3. **Added Debugging Support**
**New Feature**: When video playback fails, the addon now:
- Logs detailed information about what sources were found
- Saves the HTML to `~/peachurnet_debug.html` for inspection
- Provides better error messages distinguishing between:
  - Authentication required
  - No sources found
  - Page load failures

## Changes Made

**File**: `plugin.video.cumination/resources/lib/sites/peachurnet.py`

### `_extract_title()` Function (lines 159-205)
- Added img alt attribute fallback
- Added link title/aria-label attribute checks
- Added regex filtering to skip duration patterns
- Added logic to parse multi-line text and find the first meaningful part

### `_gather_video_sources()` Function (lines 320-381)
- Expanded video tag detection
- Added multiple JavaScript regex patterns
- Improved iframe handling with ad filtering
- Added comprehensive logging

### `Playvid()` Function (lines 444-495)
- Added detailed logging at each step
- Added HTML dump to home directory when no sources found
- Better progress updates
- Enhanced error messages

## Testing

All existing tests still pass:
```bash
python run_tests.py tests/sites/test_peachurnet.py -v
# Result: 10/10 tests PASSED ✓
```

Code quality check:
```bash
ruff check plugin.video.cumination/resources/lib/sites/peachurnet.py
# Result: All checks passed! ✓
```

## How to Test the Fix

### 1. **Install the Updated Addon**
```bash
# Build the addon
python build_repo_addons.py --addons plugin.video.cumination

# Install in Kodi:
# - Go to Add-ons → Install from zip file
# - Select plugin.video.cumination-X.X.XXX.zip
```

### 2. **Test Video Listing**
1. Open Cumination addon in Kodi
2. Navigate to PeachUrNet
3. Select any category (e.g., "Latest Updates")
4. **Expected**: Videos now show proper titles instead of just durations
5. **Expected**: Thumbnails load correctly

### 3. **Test Video Playback**
1. Select any video from the list
2. **Expected**: Video plays successfully
3. If multiple sources available, you'll be prompted to select one

### 4. **Check Logs (if issues persist)**

If videos still don't play:

1. Enable Kodi debug logging:
   - Settings → System → Logging → Enable debug logging

2. Try to play a video

3. Check the Kodi log for:
   ```
   peachurnet: Found X video source(s): [...]
   ```

4. If no sources found, check for the debug HTML file:
   - Location: `~/peachurnet_debug.html` (Linux/Mac)
   - Location: `C:\Users\YourName\peachurnet_debug.html` (Windows)

5. Send the relevant log lines or debug HTML to help diagnose

## Expected Behavior After Fix

✅ **Video listings show proper titles** - Not just durations
✅ **Thumbnails load correctly** - Using lazy-loading fallbacks
✅ **Videos play successfully** - Multiple source detection strategies
✅ **Better error messages** - Clear indication of what went wrong
✅ **Debug logging** - Easier troubleshooting if issues occur

## Potential Issues

**If titles still don't appear:**
- The site may have changed its HTML structure significantly
- Check `~/peachurnet_debug.html` to see the actual HTML
- The new selectors might need adjustment

**If videos still don't play:**
- Check if videos require login (error message will indicate this)
- Some videos might use proprietary players not yet supported
- Check logs for "Found X video source(s)" to see what was detected
- The debug HTML file will show the actual page structure

## Next Steps

If issues persist after this fix, please provide:
1. The Kodi debug log showing the "peachurnet:" log lines
2. The `peachurnet_debug.html` file (if created)
3. Specific URL of a video that doesn't work

This will help identify if the site is using a new HTML structure or video player that needs additional support.
