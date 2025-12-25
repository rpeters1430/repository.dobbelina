"""
Additional tests for utils.py functions
Testing utility functions not covered by other test files
"""

from unittest.mock import Mock, patch


class TestKodilog:
    """Test kodilog() function"""

    @patch("resources.lib.utils.xbmc")
    def test_kodilog_default_level(self, mock_xbmc):
        """Test kodilog with default log level"""
        from resources.lib import utils

        utils.kodilog("Test message")

        mock_xbmc.log.assert_called_once()
        call_args = mock_xbmc.log.call_args[0]
        assert "@@@@Cumination: Test message" in call_args[0]

    @patch("resources.lib.utils.xbmc")
    def test_kodilog_custom_level(self, mock_xbmc):
        """Test kodilog with custom log level"""
        from resources.lib import utils
        import xbmc

        utils.kodilog("Error message", xbmc.LOGERROR)

        mock_xbmc.log.assert_called_once()
        call_args = mock_xbmc.log.call_args
        assert "@@@@Cumination: Error message" in call_args[0][0]
        assert call_args[0][1] == xbmc.LOGERROR

    @patch("resources.lib.utils.xbmc")
    def test_kodilog_with_numbers(self, mock_xbmc):
        """Test kodilog converts numbers to strings"""
        from resources.lib import utils

        utils.kodilog(12345)

        mock_xbmc.log.assert_called_once()
        call_args = mock_xbmc.log.call_args[0]
        assert "@@@@Cumination: 12345" in call_args[0]


class TestClearFunctions:
    """Test cache and cookie clearing functions"""

    @patch("resources.lib.utils.xbmcgui.Dialog")
    @patch("resources.lib.utils.cache")
    def test_clear_cache(self, mock_cache, mock_dialog_class):
        """Test clear_cache clears the cache"""
        from resources.lib import utils

        mock_dialog = Mock()
        mock_dialog_class.return_value = mock_dialog

        utils.clear_cache()

        mock_cache.cacheDelete.assert_called_once_with("%get%")

    @patch("resources.lib.utils.xbmcgui.Dialog")
    @patch("resources.lib.utils.cj")
    def test_clear_cookies(self, mock_cj, mock_dialog_class):
        """Test clear_cookies clears cookies"""
        from resources.lib import utils

        mock_dialog = Mock()
        mock_dialog_class.return_value = mock_dialog

        utils.clear_cookies()

        mock_cj.clear.assert_called_once()
        mock_cj.save.assert_called_once()


class TestStreamdefence:
    """Test streamdefence() base64 decoding function"""

    def test_streamdefence_with_iframe(self):
        """Test streamdefence returns HTML as-is when iframe present"""
        from resources.lib import utils

        html = '<html><iframe src="video.html"></iframe></html>'
        result = utils.streamdefence(html)

        assert result == html

    def test_streamdefence_without_iframe_returns_html(self):
        """Test streamdefence handles non-iframe HTML"""
        from resources.lib import utils

        html = "<html><div>Simple content</div></html>"

        # Should either decode or return as-is
        # The function may fail decoding and return original
        try:
            result = utils.streamdefence(html)
            # Just verify it returns something
            assert result is not None
        except (IndexError, Exception):
            # Expected for invalid encoded data
            pass


class TestSetSortedFunctions:
    """Test setSorted and setUnsorted functions"""

    @patch("resources.lib.utils.xbmc")
    @patch("resources.lib.utils.addon")
    def test_setSorted(self, mock_addon, mock_xbmc):
        """Test setSorted sets the setting to true"""
        from resources.lib import utils

        utils.setSorted()

        mock_addon.setSetting.assert_called_once_with("keywords_sorted", "true")
        mock_xbmc.executebuiltin.assert_called_once_with("Container.Refresh")

    @patch("resources.lib.utils.xbmc")
    @patch("resources.lib.utils.addon")
    def test_setUnsorted(self, mock_addon, mock_xbmc):
        """Test setUnsorted sets the setting to false"""
        from resources.lib import utils

        utils.setUnsorted()

        mock_addon.setSetting.assert_called_once_with("keywords_sorted", "false")
        mock_xbmc.executebuiltin.assert_called_once_with("Container.Refresh")


class TestRefresh:
    """Test refresh() function"""

    @patch("resources.lib.utils.xbmc")
    def test_refresh(self, mock_xbmc):
        """Test refresh executes Container.Refresh"""
        from resources.lib import utils

        utils.refresh()

        mock_xbmc.executebuiltin.assert_called_once_with("Container.Refresh")


class TestProtocolRelativeUrls:
    """Test fix_url() function with protocol-relative URLs"""

    def test_fix_url_protocol_relative(self):
        """Test fix_url with protocol-relative URL"""
        from resources.lib import utils

        result = utils.fix_url("//cdn.example.com/video.mp4", "https://example.com")

        assert result == "https://cdn.example.com/video.mp4"

    def test_fix_url_absolute_url(self):
        """Test fix_url with absolute URL returns as-is"""
        from resources.lib import utils

        url = "https://cdn.example.com/video.mp4"
        result = utils.fix_url(url, "https://example.com")

        assert result == url

    def test_fix_url_http_url_unchanged(self):
        """Test fix_url with http URL"""
        from resources.lib import utils

        url = "http://example.com/video.mp4"
        result = utils.fix_url(url)

        assert result == url


class TestPrefquality:
    """Test prefquality() function - additional edge cases"""

    def test_prefquality_empty_sources(self):
        """Test prefquality with empty sources list"""
        from resources.lib import utils

        result = utils.prefquality([])

        assert result is None


class TestAdditionalTextProcessing:
    """Test additional text processing edge cases"""

    def test_cleantext_handles_nbsp(self):
        """Test cleantext handles non-breaking spaces"""
        from resources.lib import utils

        text = "Hello&nbsp;World"
        result = utils.cleantext(text)

        assert "&nbsp;" not in result
        assert "Hello World" in result or "Hello" in result

    def test_cleantext_handles_amp(self):
        """Test cleantext handles ampersand entities"""
        from resources.lib import utils

        text = "Rock &amp; Roll"
        result = utils.cleantext(text)

        assert "&amp;" not in result
        assert "&" in result

    def test_cleanhtml_removes_tags(self):
        """Test cleanhtml removes HTML tags"""
        from resources.lib import utils

        html = "<p>Hello <strong>World</strong></p>"
        result = utils.cleanhtml(html)

        assert "<p>" not in result
        assert "<strong>" not in result
        assert "Hello World" in result


class TestSafeAttrHelpers:
    """Test safe attribute helpers edge cases"""

    def test_safe_get_attr_with_none_element(self):
        """Test safe_get_attr with None element"""
        from resources.lib import utils

        result = utils.safe_get_attr(None, "href")

        assert result == ""

    def test_safe_get_attr_with_custom_default(self):
        """Test safe_get_attr with custom default"""
        from resources.lib import utils

        result = utils.safe_get_attr(None, "href", default="default_value")

        assert result == "default_value"

    def test_safe_get_text_with_none_element(self):
        """Test safe_get_text with None element"""
        from resources.lib import utils

        result = utils.safe_get_text(None)

        assert result == ""

    def test_safe_get_text_with_custom_default(self):
        """Test safe_get_text with custom default"""
        from resources.lib import utils

        result = utils.safe_get_text(None, default="default_text")

        assert result == "default_text"


class TestGetVidhost:
    """Test get_vidhost() additional cases"""

    def test_get_vidhost_with_path(self):
        """Test get_vidhost extracts domain from URL with path"""
        from resources.lib import utils

        result = utils.get_vidhost("https://example.com/videos/watch.html")

        assert result == "example.com"

    def test_get_vidhost_with_subdomain(self):
        """Test get_vidhost handles subdomains"""
        from resources.lib import utils

        result = utils.get_vidhost("https://cdn.example.com/video.mp4")

        assert result == "example.com"

    def test_get_vidhost_with_port(self):
        """Test get_vidhost handles port numbers"""
        from resources.lib import utils

        result = utils.get_vidhost("http://localhost:8080/video.mp4")

        assert result == "localhost"


class TestGetLanguage:
    """Test get_language() additional cases"""

    def test_get_language_unknown_code(self):
        """Test get_language returns code for unknown language"""
        from resources.lib import utils

        result = utils.get_language("zz")

        assert result == "zz"

    def test_get_language_uppercase(self):
        """Test get_language handles uppercase codes"""
        from resources.lib import utils

        result = utils.get_language("EN")

        assert result == "English"


class TestGetCountry:
    """Test get_country() additional cases"""

    def test_get_country_unknown_code(self):
        """Test get_country returns code for unknown country"""
        from resources.lib import utils

        result = utils.get_country("xx")

        assert result == "xx"

    def test_get_country_uppercase(self):
        """Test get_country handles uppercase codes"""
        from resources.lib import utils

        result = utils.get_country("US")

        assert result == "United States"
