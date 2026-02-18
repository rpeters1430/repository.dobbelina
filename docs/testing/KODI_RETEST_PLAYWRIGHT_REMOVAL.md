# Kodi Retest Checklist (Playwright Removed From Site Modules)

Date: 2026-02-16

This checklist covers the site modules that were changed to remove Playwright runtime usage in Kodi.

## Quick Test Flow (Per Site)

1. Open site in Kodi.
2. Open main listing and confirm items load.
3. Open categories/tags/models (if the site has them).
4. Run a search and open at least one result.
5. Play at least one video/stream.
6. Test next page navigation.
7. Confirm no `playwright_helper`, `npx`, or `@playwright/test` errors in `kodi.log`.

## Sites To Retest

- [X] `anybunny` - videos + images load (very low quality) - need "Next Page" on main screen. Top Videos folder lists videos with no images and lists only 10 videos with no Next Page. Videos play same quality issues. We can remove "Categories - images" folder completely. Categories work but loads only 9 videos and images are iffy. Videos do play though at about 10p it looks like. Search Works and videos play with same issue. On main screen we can list the "Newest" or latest videos on the page.
- [X] `blendporn` - main screen videos load with no images. Videos play no problem. Category folder works but image shows "Preview Image Coming Soon! (we can just add the logo as the image or find them). Category videos load no images but videos do play. Search works with no images and videos do play for search.
- [ ] `drtuber` - Videos on main page load with images ok and videos play ok. Categories do load but there are about 12-14 empty folders at the top of the screen that list before the categories actually list. Videos in categories do load with images and videos do play. HD & 4k folders work with videos + images + video playback. Search all works just fine.
- [ ] `foxnxx` - videos load but the title of the video there are numbers overlayed over the name of it. Videos do not play on main screen. There are no Category folder or anything just Search but the listing names are messed up.
- [ ] `hotleak` - List latest videos on main screen. The videos do load with the images but do not play. The name of the video listed is weird says i.e. "@estarletto 11939060" so search is broken
- [ ] `josporn` - Latest updates videos can be listed on main screen. Logo is missing. Latest videos do load with images. Videos do not play saying cannot find video url. Search does not work either but essentially search + logo + video playback. Also the name of the site just JosPorn will work remove the URL
- [ ] `luxuretv` - luxeretv we can remove the site completely
- [ ] `missav` - missav we can remove also completely 
- [ ] `naked` - Error is Unable to load naked.com page
- [ ] `noodlemagazine` - Noodlemagazine won't load at all
- [ ] `pornhub` - Everything works except for search
- [ ] `porntn`
- [ ] `pornxpert`
- [ ] `spankbang`
- [ ] `stripchat`
- [ ] `trendyporn`
- [ ] `viralvideosporno`

## Shared Runtime Change To Retest

- [ ] `utils._solve_hornyhill` path still resolves playable stream links without Playwright.

## Pass Criteria

- [ ] Site loads without immediate script abort.
- [ ] Listing/search/category pages render items.
- [ ] Playback starts for at least one item.
- [ ] Pagination works.
- [ ] No Playwright-related runtime errors in `kodi.log`.

## Optional Notes Template

Use this per site while testing:

`<site>`: PASS/FAIL  
`List`: PASS/FAIL  
`Search`: PASS/FAIL  
`Categories/Tags/Models`: PASS/FAIL  
`Play`: PASS/FAIL  
`Next Page`: PASS/FAIL  
`kodi.log errors`: none / details

