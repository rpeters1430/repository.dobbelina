"""
Additional tests for thothub.py utility functions
"""

from unittest.mock import patch
from pathlib import Path


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "thothub"


def load_fixture(name):
    """Load a fixture file for testing"""
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


class TestHasCredentials:
    """Test _has_credentials() function"""

    @patch("resources.lib.sites.thothub.addon")
    def test_has_credentials_with_both_set(self, mock_addon):
        """Test returns True when both username and password are set"""
        from resources.lib.sites import thothub

        mock_addon.getSetting.side_effect = lambda key: {
            "thothub_username": "testuser",
            "thothub_password": "testpass",
        }.get(key, "")

        result = thothub._has_credentials()

        assert result is True

    @patch("resources.lib.sites.thothub.addon")
    def test_has_credentials_missing_username(self, mock_addon):
        """Test returns False when username is missing"""
        from resources.lib.sites import thothub

        mock_addon.getSetting.side_effect = lambda key: {
            "thothub_username": "",
            "thothub_password": "testpass",
        }.get(key, "")

        result = thothub._has_credentials()

        assert result is False

    @patch("resources.lib.sites.thothub.addon")
    def test_has_credentials_missing_password(self, mock_addon):
        """Test returns False when password is missing"""
        from resources.lib.sites import thothub

        mock_addon.getSetting.side_effect = lambda key: {
            "thothub_username": "testuser",
            "thothub_password": "",
        }.get(key, "")

        result = thothub._has_credentials()

        assert result is False

    @patch("resources.lib.sites.thothub.addon")
    def test_has_credentials_with_whitespace_only(self, mock_addon):
        """Test returns False when credentials are only whitespace"""
        from resources.lib.sites import thothub

        mock_addon.getSetting.side_effect = lambda key: {
            "thothub_username": "   ",
            "thothub_password": "   ",
        }.get(key, "")

        result = thothub._has_credentials()

        assert result is False


class TestCleanMediaUrl:
    """Test _clean_media_url() function"""

    def test_clean_media_url_removes_escaped_slashes(self):
        """Test cleaning removes escaped slashes"""
        from resources.lib.sites import thothub

        url = "https://example.com\\/videos\\/video.mp4"
        result = thothub._clean_media_url(url)

        assert "\\/" not in result
        assert "https://example.com/videos/video.mp4" == result

    def test_clean_media_url_removes_amp_entities(self):
        """Test cleaning removes &amp; entities"""
        from resources.lib.sites import thothub

        url = "https://example.com/video.mp4?param1=val&amp;param2=val"
        result = thothub._clean_media_url(url)

        assert "&amp;" not in result
        assert "&" in result

    def test_clean_media_url_handles_none(self):
        """Test returns None for None input"""
        from resources.lib.sites import thothub

        result = thothub._clean_media_url(None)

        assert result is None

    def test_clean_media_url_handles_empty_string(self):
        """Test returns None for empty string"""
        from resources.lib.sites import thothub

        result = thothub._clean_media_url("")

        assert result is None

    def test_clean_media_url_adds_http_prefix(self):
        """Test adds http:// prefix for relative URLs"""
        from resources.lib.sites import thothub

        url = "/videos/video.mp4"
        result = thothub._clean_media_url(url)

        assert result.startswith("http")

    def test_clean_media_url_converts_slash_ampersand(self):
        """Test converts /& to ? for query strings"""
        from resources.lib.sites import thothub

        url = "https://example.com/video.mp4/&param=value"
        result = thothub._clean_media_url(url)

        assert "/&" not in result
        assert "?param=value" in result

    def test_clean_media_url_strips_trailing_slash(self):
        """Test removes trailing slash"""
        from resources.lib.sites import thothub

        url = "https://example.com/video.mp4/"
        result = thothub._clean_media_url(url)

        assert not result.endswith("/")


class TestParseFlashvars:
    """Test _parse_flashvars() function"""

    def test_parse_flashvars_var_with_single_quotes(self):
        """Test parsing var flashvars with single quotes"""
        from resources.lib.sites import thothub

        html = """
        <script>
        var flashvars = { video_url: 'https://example.com/video.mp4', video_id: '12345' };
        </script>
        """

        result = thothub._parse_flashvars(html)

        assert "video_url" in result
        assert result["video_url"] == "https://example.com/video.mp4"
        assert result["video_id"] == "12345"

    def test_parse_flashvars_var_with_double_quotes(self):
        """Test parsing var flashvars with double quotes"""
        from resources.lib.sites import thothub

        html = """
        <script>
        var flashvars = { video_url: "https://example.com/video.mp4", video_id: "12345" };
        </script>
        """

        result = thothub._parse_flashvars(html)

        assert "video_url" in result
        assert result["video_url"] == "https://example.com/video.mp4"

    def test_parse_flashvars_without_var_keyword(self):
        """Test parsing flashvars without var keyword"""
        from resources.lib.sites import thothub

        html = """
        <script>
        flashvars = { video_url: 'https://example.com/video.mp4' };
        </script>
        """

        result = thothub._parse_flashvars(html)

        assert "video_url" in result

    def test_parse_flashvars_json_config(self):
        """Test parsing JSON player config"""
        from resources.lib.sites import thothub

        html = """
        <script>
        var playerConfig = {"video_url":"https://example.com/video.mp4","video_id":"12345"};
        </script>
        """

        result = thothub._parse_flashvars(html)

        assert "video_url" in result
        assert result["video_url"] == "https://example.com/video.mp4"

    def test_parse_flashvars_returns_empty_dict_when_not_found(self):
        """Test returns empty dict when no flashvars found"""
        from resources.lib.sites import thothub

        html = "<html><body>No flashvars here</body></html>"

        result = thothub._parse_flashvars(html)

        assert result == {}

    def test_parse_flashvars_lowercases_keys(self):
        """Test that keys are lowercased"""
        from resources.lib.sites import thothub

        html = """
        <script>
        var flashvars = { VIDEO_URL: 'https://example.com/video.mp4', Video_ID: '12345' };
        </script>
        """

        result = thothub._parse_flashvars(html)

        assert "video_url" in result
        assert "video_id" in result
        assert "VIDEO_URL" not in result


class TestIsLoggedIn:
    """Test _is_logged_in() function"""

    @patch("resources.lib.sites.thothub._thothub_cookie_names")
    def test_is_logged_in_with_auth_cookie(self, mock_cookie_names):
        """Test returns True when auth cookie present"""
        from resources.lib.sites import thothub

        mock_cookie_names.return_value = ["kt_member", "other_cookie"]

        result = thothub._is_logged_in()

        assert result is True

    @patch("resources.lib.sites.thothub._thothub_cookie_names")
    def test_is_logged_in_with_login_key_cookie(self, mock_cookie_names):
        """Test returns True when kt_login_key present"""
        from resources.lib.sites import thothub

        mock_cookie_names.return_value = ["kt_login_key"]

        result = thothub._is_logged_in()

        assert result is True

    @patch("resources.lib.sites.thothub._thothub_cookie_names")
    def test_is_logged_in_without_auth_cookies(self, mock_cookie_names):
        """Test returns False when no auth cookies"""
        from resources.lib.sites import thothub

        mock_cookie_names.return_value = ["some_other_cookie"]

        result = thothub._is_logged_in()

        assert result is False

    @patch("resources.lib.sites.thothub._thothub_cookie_names")
    def test_is_logged_in_with_empty_cookies(self, mock_cookie_names):
        """Test returns False when no cookies at all"""
        from resources.lib.sites import thothub

        mock_cookie_names.return_value = []

        result = thothub._is_logged_in()

        assert result is False


class TestBuildBrowserHeaders:
    """Test _build_browser_headers() function"""

    def test_build_browser_headers_includes_user_agent(self):
        """Test headers include user agent"""
        from resources.lib.sites import thothub

        headers = thothub._build_browser_headers()

        assert "User-Agent" in headers
        assert headers is not None
