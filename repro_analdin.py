
import sys
import os

# Add the addon resources to the path
sys.path.append(os.path.join(os.getcwd(), 'plugin.video.cumination'))
sys.path.append(os.path.join(os.getcwd(), 'plugin.video.cumination', 'resources', 'lib'))

# Mock xbmc modules
from MagicMock import mock
mock.xbmc_all()

from resources.lib.sites import analdin
from resources.lib import utils

def test_analdin_list():
    url = "https://www.analdin.com/latest-updates/"
    print(f"Testing Analdin List: {url}")
    
    # We need to capture the items added to site.add_download_link
    original_add_download_link = analdin.site.add_download_link
    added_items = []
    
    def mock_add_download_link(title, url, mode, thumb, original_title):
        added_items.append({'title': title, 'url': url})
        # print(f"Found: {title}")
    
    analdin.site.add_download_link = mock_add_download_link
    
    analdin.List(url)
    
    print(f"Total items found: {len(added_items)}")
    if len(added_items) == 0:
        print("FAILURE: No items found")
    else:
        print("SUCCESS: Items found")
        for item in added_items[:5]:
            print(f" - {item['title']} -> {item['url']}")

if __name__ == "__main__":
    test_analdin_list()
