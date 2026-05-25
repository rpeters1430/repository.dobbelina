
import pytest
from resources.lib.sites import analdin
from resources.lib import utils

@pytest.mark.skip(reason="Live tests are blocked by network guard in conftest.py")
def test_analdin_list_live():
    url = "https://www.analdin.com/latest-updates/"
    
    # We need to capture the items added to site.add_download_link
    added_items = []
    
    def mock_add_download_link(title, url, mode, thumb, original_title):
        added_items.append({'title': title, 'url': url})
    
    # Patch the site object's method
    analdin.site.add_download_link = mock_add_download_link
    
    analdin.List(url)
    
    assert len(added_items) > 0, "No items found in Analdin List"
    print(f"\nFound {len(added_items)} items")
    for item in added_items[:3]:
        print(f"  - {item['title']}")
