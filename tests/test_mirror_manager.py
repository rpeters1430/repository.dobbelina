"""
Unit tests for Dynamic Mirror Manager module.
"""

from unittest.mock import MagicMock, patch
from resources.lib import mirror_manager
from resources.lib.adultsite import AdultSite


def test_mirror_manager_default_lookup():
    mirror_manager.clear_mirrors_cache()
    url = mirror_manager.get_site_url("thothub", "https://thothub.to/")
    assert url == "https://thothub.to/"

    unknown_url = mirror_manager.get_site_url("unknown_site", "https://default.com/")
    assert unknown_url == "https://default.com/"


def test_mirror_manager_set_and_report_failure(tmp_path):
    mirror_manager.clear_mirrors_cache()
    # Test setting active mirror
    mirror_manager.set_active_mirror("thothub", "https://thothub.lol/")
    assert mirror_manager.get_site_url("thothub", "https://thothub.to/") == "https://thothub.lol/"

    # Test report failure to rotate to alternate mirror
    next_mirror = mirror_manager.report_failure("thothub", "https://thothub.lol/")
    assert next_mirror in mirror_manager.get_mirrors("thothub")
    assert next_mirror != "https://thothub.lol/"


def test_adultsite_dynamic_url_integration():
    mirror_manager.clear_mirrors_cache()
    site = AdultSite("thothub", "ThotHub", "https://thothub.to/")
    assert site.url == "https://thothub.to/"

    # When active mirror changes
    mirror_manager.set_active_mirror("thothub", "https://thothub.lol/")
    assert site.url == "https://thothub.lol/"


def test_probe_mirror():
    mock_resp = MagicMock()
    mock_resp.status = 200

    with patch("six.moves.urllib_request.urlopen", return_value=mock_resp):
        assert mirror_manager.probe_mirror("https://thothub.to/") is True

    with patch("six.moves.urllib_request.urlopen", side_effect=Exception("Failed")):
        assert mirror_manager.probe_mirror("https://broken.domain/") is False
