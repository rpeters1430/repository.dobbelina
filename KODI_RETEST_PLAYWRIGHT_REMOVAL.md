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

- [ ] `anybunny`
- [ ] `blendporn`
- [ ] `drtuber`
- [ ] `foxnxx`
- [ ] `hotleak`
- [ ] `josporn`
- [ ] `luxuretv`
- [ ] `missav`
- [ ] `naked`
- [ ] `noodlemagazine`
- [ ] `pornhub`
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

