
from resources.lib.sites import analdin
from resources.lib import utils
from pathlib import Path

def test_analdin_parser_with_fixture():
    fixture_path = Path("tests/fixtures/sites/analdin_list.html")
    html = fixture_path.read_text(encoding="utf-8")
    
    # We need to capture the items added to site.add_download_link
    added_items = []
    
    def mock_add_download_link(title, url, mode, thumb, original_title):
        added_items.append({'title': title, 'url': url})
    
    # Patch the site object's method
    original_add_download_link = analdin.site.add_download_link
    analdin.site.add_download_link = mock_add_download_link
    
    # We need to mock utils.getHtml and utils.get_html_with_cloudflare_retry to return our fixture
    original_getHtml = utils.getHtml
    original_retry = utils.get_html_with_cloudflare_retry
    
    utils.getHtml = lambda url, referer=None: html
    utils.get_html_with_cloudflare_retry = lambda url, referer=None, *args, **kwargs: (html, False)
    
    try:
        analdin.List("https://www.analdin.com/latest-updates/")
    finally:
        utils.getHtml = original_getHtml
        utils.get_html_with_cloudflare_retry = original_retry
        analdin.site.add_download_link = original_add_download_link
    
    assert len(added_items) > 0, "No items found in Analdin List with fixture"
    print(f"\nFound {len(added_items)} items with fixture")
    assert len(added_items) == 2, f"Expected 2 items, found {len(added_items)}"

