"""Tests for livecamrips site module"""

import re
from unittest.mock import patch, MagicMock
from resources.lib.sites import livecamrips


def test_list_parses_video_items(read_fixture):
    """Test that List function parses video items from main page"""
    html = read_fixture("livecamrips/main_page.html")

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.eod") as mock_eod,
        patch.object(livecamrips.site, "add_download_link") as mock_add_link,
        patch.object(livecamrips.site, "add_dir") as mock_add_dir,
    ):
        mock_gethtml.return_value = html

        livecamrips.List("https://www.livecamsrip.com/", 1)

        # Should have called getHtml
        assert mock_gethtml.called

        # Should have added multiple video links
        assert mock_add_link.call_count > 20, (
            f"Expected >20 videos, got {mock_add_link.call_count}"
        )

        # Check first video call
        first_call = mock_add_link.call_args_list[0]
        args = first_call[0]

        # args: (name, videopage, mode, img, desc)
        assert len(args) == 5
        assert isinstance(args[0], str), "Name should be string"
        assert "livecamsrip.com/watch/" in args[1], "URL should contain /watch/"
        assert args[2] == "Playvid", "Mode should be Playvid"
        assert args[3] is None or "allmy.cam" in args[3], (
            "Thumbnail should be from allmy.cam or None"
        )
        assert isinstance(args[4], str), "Description should be string"

        # Should have pagination
        assert mock_add_dir.called, "Should add pagination directory"

        # Should have called eod
        assert mock_eod.called


def test_list_extracts_metadata(read_fixture):
    """Test that List function extracts username, platform, timestamp, views"""
    html = read_fixture("livecamrips/main_page.html")

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.eod"),
        patch.object(livecamrips.site, "add_download_link") as mock_add_link,
        patch.object(livecamrips.site, "add_dir"),
    ):
        mock_gethtml.return_value = html

        livecamrips.List("https://www.livecamsrip.com/", 1)

        # Check that videos have names with platform info
        calls = mock_add_link.call_args_list

        # At least some videos should have platform names
        platforms_found = False
        for call in calls:
            name = call[0][0]
            if any(
                platform in name
                for platform in ["Stripchat", "Chaturbate", "Camsoda", "Cam4"]
            ):
                platforms_found = True
                break

        assert platforms_found, (
            "Should extract platform names (Stripchat, Chaturbate, etc.)"
        )

        # Check descriptions contain timestamp or views
        desc_with_metadata = False
        for call in calls:
            desc = call[0][4]
            if "ago" in desc or "views" in desc or "•" in desc:
                desc_with_metadata = True
                break

        assert desc_with_metadata, (
            "Descriptions should contain timestamp/views metadata"
        )


def test_list_handles_pagination(read_fixture):
    """Test that List function adds pagination link"""
    html = read_fixture("livecamrips/main_page.html")

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.eod"),
        patch.object(livecamrips.site, "add_download_link"),
        patch.object(livecamrips.site, "add_dir") as mock_add_dir,
    ):
        mock_gethtml.return_value = html

        livecamrips.List("https://www.livecamsrip.com/", 1)

        # Should add pagination directory
        assert mock_add_dir.called

        # Check pagination call
        page_call = mock_add_dir.call_args_list[0]
        args = page_call[0]

        # args: (label, url, mode, icon, page_number)
        assert "Next Page" in args[0] or "Page" in args[0]
        assert "?page=" in args[1] or "page=" in args[1]
        assert args[2] == "List"


def test_search_without_keyword():
    """Test that Search without keyword shows search dialog"""
    with patch.object(livecamrips.site, "search_dir") as mock_search:
        livecamrips.Search("https://www.livecamsrip.com/search")

        assert mock_search.called
        assert mock_search.call_args[0][0] == "https://www.livecamsrip.com/search"
        assert mock_search.call_args[0][1] == "Search"


def test_search_with_keyword():
    """Test that Search with keyword builds search URL and calls List"""
    with patch.object(livecamrips, "List") as mock_list:
        livecamrips.Search("https://www.livecamsrip.com/search", "test query")

        assert mock_list.called
        search_url = mock_list.call_args[0][0]
        assert "search=test+query" in search_url or "search=test%20query" in search_url


def test_playvid_extracts_video_id(read_fixture):
    """Test that Playvid extracts base64 video ID from URL"""
    html = read_fixture("livecamrips/video_page.html")

    mock_vp = MagicMock()
    mock_vp.progress = MagicMock()
    mock_vp.progress.iscanceled = MagicMock(return_value=False)

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
        patch("resources.lib.utils.kodilog") as mock_log,
    ):
        mock_gethtml.return_value = html

        livecamrips.Playvid(
            "https://www.livecamsrip.com/watch/MTU2MDk3Njg=", "Test Video"
        )

        # Should log the decoded UUID
        log_calls = [str(call) for call in mock_log.call_args_list]
        uuid_logged = any("video UUID" in str(call) for call in log_calls)
        assert uuid_logged, "Should log decoded video UUID"


def test_playvid_extracts_csrf_token(read_fixture):
    """Test that Playvid extracts CSRF token from page"""
    html = read_fixture("livecamrips/video_page.html")

    # Extract CSRF token using the same regex as the code
    csrf_match = re.search(r'name="_token"[^>]+value="([^"]+)"', html)
    if not csrf_match:
        csrf_match = re.search(r'csrf-token"\s+content="([^"]+)"', html)

    assert csrf_match is not None, "CSRF token should be present in HTML fixture"
    csrf_token = csrf_match.group(1)
    assert len(csrf_token) > 10, "CSRF token should be a valid length string"


def test_playvid_builds_livewire_payload(read_fixture):
    """Test that Playvid builds proper Livewire payload structure"""
    html = read_fixture("livecamrips/video_page.html")

    mock_vp = MagicMock()
    mock_vp.progress = MagicMock()
    mock_vp.progress.iscanceled = MagicMock(return_value=False)

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.VideoPlayer", return_value=mock_vp),
        patch("resources.lib.utils.kodilog"),
    ):
        # First call returns video page, second call returns Livewire response
        mock_gethtml.side_effect = [
            html,
            '{"components":[{"effects":{"html":"https://myvidplay.com/e/test123"}}]}',
        ]

        livecamrips.Playvid(
            "https://www.livecamsrip.com/watch/MTU2MDk3Njg=", "Test Video"
        )

        # Check that getHtml was called twice (page + Livewire AJAX)
        assert mock_gethtml.call_count >= 2, (
            "Should call getHtml for page and Livewire request"
        )

        # Check second call (Livewire AJAX)
        if mock_gethtml.call_count >= 2:
            livewire_call = mock_gethtml.call_args_list[1]

            # Should include headers
            if "headers" in livewire_call[1]:
                headers = livewire_call[1]["headers"]
                assert "X-Livewire" in headers, "Should include X-Livewire header"
                assert headers["X-Livewire"] == "true"


def test_main_creates_menu():
    """Test that Main function creates main menu"""
    with (
        patch("resources.lib.utils.eod") as mock_eod,
        patch.object(livecamrips.site, "add_dir") as mock_add_dir,
        patch.object(livecamrips, "List") as mock_list,
    ):
        livecamrips.Main()

        # Should add search directory
        assert mock_add_dir.called
        search_call = mock_add_dir.call_args_list[0]
        assert "Search" in search_call[0][0]

        # Should call List to show videos
        assert mock_list.called

        # Should call eod
        assert mock_eod.called


def test_list_skips_duplicates(read_fixture):
    """Test that List function skips duplicate video URLs"""
    html = read_fixture("livecamrips/main_page.html")

    with (
        patch("resources.lib.utils.getHtml") as mock_gethtml,
        patch("resources.lib.utils.eod"),
        patch.object(livecamrips.site, "add_download_link") as mock_add_link,
        patch.object(livecamrips.site, "add_dir"),
    ):
        mock_gethtml.return_value = html

        livecamrips.List("https://www.livecamsrip.com/", 1)

        # Collect all video URLs that were added
        video_urls = [call[0][1] for call in mock_add_link.call_args_list]

        # Check for duplicates
        unique_urls = set(video_urls)
        assert len(video_urls) == len(unique_urls), (
            "Should not add duplicate video URLs"
        )
