# PeachUrNet Fix - Testing Instructions

## What Was Fixed

The Peachurnet site uses **double base64 encoding** to hide video URLs in JavaScript variables. The previous code only found a placeholder URL (`https://peachurnet.com/data/video.mp4`) which doesn't work for playback.

### The Fix
- **Extraction Logic**: Added `_extract_peachurnet_video_url()` to find and decode JavaScript variables `sy` and `syt`
- **Double Base64 Decoding**: Implemented `_decode_base64_var()` to handle the two-layer encoding
- **Placeholder Filtering**: Modified `_gather_video_sources()` to skip placeholder URLs
- **Priority System**: JavaScript extraction now runs FIRST, before other methods

### Verification
```bash
# The extraction logic was tested and produces the correct URL:
# INPUT:  var sy="YUhSMGNITTZMeTl6TWk1b2IzTjBiV1ZrYVdGd2JIVnpMbU52..."
#         var syt="ZG1sa1pXOHZiWEEw"
# OUTPUT: https://s2.hostmediaplus.com/request/62cee206e58f4efcb6a4a238904c1e6356ffe68360b01dfdac8459079671193351f6/video/mp4

# All 14 tests pass:
python run_tests.py --site peachurnet -v
# Result: 14/14 PASSED ✅
```

## Installation and Testing

### Step 1: Install the Updated Addon in Kodi

1. **Open Kodi** and go to **Add-ons**
2. Click the **Package icon** (top left)
3. Select **Install from zip file**
4. Navigate to: `/home/rpeters1428/repository.dobbelina/`
5. Select: `plugin.video.cumination-1.1.211.zip`
6. Wait for the "Cumination installed" notification

### Step 2: Test Video Listing

1. Go to **Add-ons** → **Video add-ons**
2. Open **Cumination**
3. Select **PeachUrNet**
4. Choose **Latest Updates**

**Expected Results:**
- ✅ Videos show proper titles (not just durations like "15:30")
- ✅ Thumbnails load correctly
- ✅ Duration shows as metadata below the title

### Step 3: Test Video Playback

1. Select any video from the list (e.g., "kaliana_ggh")
2. Click to play

**Expected Results:**
- ✅ Video starts playing without errors
- ✅ The real video URL is used (not the placeholder)
- ✅ No "cannot find video url" error

### Step 4: Check Debug Logs (If Issues Occur)

If video playback fails:

1. Enable Kodi debug logging:
   - **Settings** → **System** → **Logging** → **Enable debug logging**

2. Try to play a video again

3. Check the Kodi log for peachurnet messages:
   ```bash
   tail -100 ~/kodi.log | grep peachurnet
   ```

4. Look for these key log lines:
   ```
   peachurnet: Decoded video URL from JavaScript: https://s2.hostmediaplus.com/...
   peachurnet: Found X video source(s)
   peachurnet: Selected source: <URL>
   ```

**What to Look For:**
- ✅ **GOOD**: Selected source shows `https://s2.hostmediaplus.com/...` or similar external URL
- ❌ **BAD**: Selected source shows `https://peachurnet.com/data/video.mp4` (placeholder)

### Step 5: Test Multiple Videos

Try playing 2-3 different videos to ensure consistency:
- Videos from "Latest Updates"
- Videos from search results
- Videos from different categories

## Expected Behavior After Fix

| Scenario | Before Fix | After Fix |
|----------|------------|-----------|
| Video listing | Shows only durations | Shows proper titles ✅ |
| Video playback | "No video URL found" error | Plays successfully ✅ |
| Video source | Placeholder URL | Real hostmediaplus.com URL ✅ |
| Error messages | Generic errors | Clear, actionable messages ✅ |

## Troubleshooting

### Issue: Videos still don't play

**Check 1:** Verify the addon version installed
```bash
# In Kodi, go to Add-ons → Video add-ons → Right-click Cumination → Information
# Version should be: 1.1.211 or higher
```

**Check 2:** Check if JavaScript variables are present
```bash
# The site might have changed their obfuscation method
# Check the debug HTML for "var sy" and "var syt"
grep "var sy" ~/peachurnet_debug.html
```

**Check 3:** Verify the URL extraction works
```bash
# Run the test script
python3 test_extraction.py
# Should show: ✓ This is a real video URL (not the placeholder)
```

### Issue: No debug HTML file created

The addon only creates `~/peachurnet_debug.html` when:
- Video playback fails
- No sources are found

If the file isn't created, it means sources were found (good sign).

## Cleanup After Testing

Once testing is complete and successful:

```bash
# Remove debug files
rm -f scripts/debug_peachurnet.py scripts/debug_peachurnet_simple.py test_extraction.py
rm -f ~/peachurnet_debug.html /tmp/peachurnet_*.html

# Restore kodi.log (if desired)
git restore kodi.log

# Restore settings if needed
git restore .claude/settings.local.json
```

## What to Report

If issues persist, please provide:
1. **Kodi log excerpt** showing the peachurnet lines
2. **Debug HTML file** (if created): `~/peachurnet_debug.html`
3. **Specific video URL** that doesn't work
4. **Addon version** installed (from Add-ons → Information)

This will help identify if the site changed their HTML structure or encoding method.

## Summary

✅ **Fix implemented and tested**
✅ **All unit tests pass (14/14)**
✅ **Extraction logic verified with live data**
✅ **Addon package built: plugin.video.cumination-1.1.211.zip**
⏳ **Ready for Kodi installation and testing**

The fix correctly extracts real video URLs from double base64-encoded JavaScript variables and skips placeholder URLs.
