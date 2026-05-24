
import pytest
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
    analdin.site.add_download_link = mock_add_download_link
    
    # We need to mock utils.getHtml to return our fixture
    original_getHtml = utils.getHtml
    utils.getHtml = lambda url, referer=None: html
    
    try:
        analdin.List("https://www.analdin.com/latest-updates/")
    finally:
        utils.getHtml = original_getHtml
    
    assert len(added_items) > 0, "No items found in Analdin List with fixture"
    print(f"\nFound {len(added_items)} items with fixture")
    assert len(added_items) == 100, f"Expected 100 items, found {len(added_items)}"
