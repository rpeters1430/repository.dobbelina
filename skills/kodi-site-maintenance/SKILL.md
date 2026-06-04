---
name: kodi-site-maintenance
description: Comprehensive workflow for investigating issues, debugging site scrapers, adding new sites, and updating tests. Use when a site is reported broken or when expanding the addon's content.
---

# Kodi Site Maintenance

This skill covers the end-to-end process of maintaining and expanding the video site scrapers in Cumination.

## Investigating Broken Sites

1.  **Reproduce**: Run the existing test for the site (`pytest tests/sites/test_<site>.py`). If it passes with fixtures but the site is broken in Kodi, the site's HTML has likely changed.
2.  **Debug Logs**: Check `kodi.log` for `@@@@Cumination` entries. Enable debug logging in the addon settings for more detail.
3.  **Inspect Live HTML**: Use `python scripts/codegen.py <url> --dump-page debug.html` to see what the scraper is actually seeing. Many sites use Cloudflare or JavaScript which can block standard `urllib` requests.

## Debugging Workflow

### Using `codegen.py`
The `scripts/codegen.py` tool is essential for modern sites:
- **Sniff URLs**: `python scripts/codegen.py <url> --sniff` to find the actual video stream or API endpoint.
- **Bypass Ads**: It automatically blocks known ad domains and closes popups to make inspection easier.

### Testing Scrapers with Live Data
Temporarily bypass the network block in a test to see live site results:
```python
# In tests/conftest.py or your test file
# Comment out: urllib.request.urlopen = _block_network_access
```

## Adding a New Site

1.  **Identify Entry Point**: Create `plugin.video.cumination/resources/lib/sites/site_<name>.py`.
2.  **Inherit from AdultSite**:
    ```python
    from resources.lib.sites.adult_site import AdultSite
    class MySite(AdultSite):
        def __init__(self):
            super().__init__('MySite', 'http://mysite.com')
    ```
3.  **Implement INDEX**: Use `soup_videos_list` for the main listing.
4.  **Implement Playvid**: Define how to resolve a video page to a playable URL.
5.  **Register**: Add the site to the main menu in `plugin.video.cumination/resources/lib/sites/__init__.py`.

## Maintenance Best Practices

- **Avoid Regex**: Always use BeautifulSoup for new or updated scrapers (see `bs4-migration-toolkit`).
- **Update Fixtures**: When a site changes, overwrite the old fixture in `tests/fixtures/sites/` with the new HTML.
- **Add Tests**: Never add a site without a corresponding test in `tests/sites/`.
- **Handle Cloudflare**: If a site is protected, ensure `utils.get_html_with_cloudflare_retry` is used and inform users to enable FlareSolverr.
