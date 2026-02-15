"""
Tests for hotleak site
"""
import pytest
import base64
import json


def test_hotleak_url_decryption():
    """Test that we can decrypt hotleak video URLs."""

    def decrypt_video_url(encrypted_url):
        """Decrypt hotleak video URL."""
        # Remove first 8 chars
        decrypted = encrypted_url[8:]
        # Remove last 16 chars
        decrypted = decrypted[:-16]
        # Reverse the string
        decrypted = decrypted[::-1]
        # Base64 decode
        decrypted = base64.b64decode(decrypted).decode('utf-8')
        return decrypted

    # Test with real encrypted URL from hotleak
    encrypted = "nsHBDRtgq21ismxd==wToxkWER0YThjYYdTcwZkY9IzZpNnJ1ADNiFjM2YWYjdTN4ATNkdTNiVGOlNTMjJ2Y0MDOxYWYldTYmJmNllTOwETN4ATZidTO5MTN0EGNmFTY4ETNh1zZpNnJ4MzM5gTMxczNx0TZtlGd/gTdz0mL2kDM5MTOxEzL4U3Mt9CcpZnLrFWZsR3bo9yL6MHc0RHaAwsYEQOVzY1M3sRW"

    decrypted = decrypt_video_url(encrypted)

    # Should be an M3U8 URL
    assert decrypted.startswith("https://hotleak.vip/m3u8/")
    assert ".m3u8" in decrypted
    assert "time=" in decrypted
    assert "sig=" in decrypted


def test_hotleak_list():
    """Test hotleak video listing parser."""
    import sys
    import os

    # Add plugin path
    plugin_path = os.path.join(os.path.dirname(__file__), '..', '..', 'plugin.video.cumination')
    sys.path.insert(0, plugin_path)

    from resources.lib import utils

    # Read fixture HTML
    fixture_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'hotleak', 'list.html')

    # For now, we'll skip if fixture doesn't exist
    if not os.path.exists(fixture_path):
        pytest.skip("Fixture file not found - save https://hotleak.vip/videos HTML to tests/fixtures/hotleak/list.html")

    with open(fixture_path, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = utils.parse_html(html)
    items = soup.select("article.movie-item")

    assert len(items) > 0, "Should find video items"

    # Check first item structure
    first_item = items[0]
    link = first_item.select_one("a[href]")
    assert link is not None, "Should have link"

    href = utils.safe_get_attr(link, "href")
    assert href, "Should have href attribute"

    # Should have thumbnail
    img = first_item.select_one("img.post-thumbnail")
    assert img is not None, "Should have thumbnail image"


def test_hotleak_video_page_parsing():
    """Test extracting encrypted URL from video page."""
    import sys
    import os

    plugin_path = os.path.join(os.path.dirname(__file__), '..', '..', 'plugin.video.cumination')
    sys.path.insert(0, plugin_path)

    from resources.lib import utils

    fixture_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'hotleak', 'video.html')

    if not os.path.exists(fixture_path):
        pytest.skip("Fixture file not found - save a hotleak video page HTML to tests/fixtures/hotleak/video.html")

    with open(fixture_path, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = utils.parse_html(html)
    video_items = soup.select('[data-video]')

    assert len(video_items) > 0, "Should find elements with data-video attribute"

    # Parse the first data-video
    data_video = utils.safe_get_attr(video_items[0], 'data-video')
    assert data_video, "Should have data-video attribute"

    video_json = json.loads(data_video)
    assert 'source' in video_json, "Should have source in video JSON"
    assert len(video_json['source']) > 0, "Should have at least one source"

    encrypted_url = video_json['source'][0].get('src', '')
    assert encrypted_url, "Should have encrypted src URL"
    assert len(encrypted_url) > 50, "Encrypted URL should be reasonably long"
