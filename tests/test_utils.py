from resources.lib import utils
from tests.conftest import read_fixture


def test_parse_html_and_safe_get_attr_handles_fallbacks():
    soup = utils.parse_html(read_fixture("sample_listing.html"))
    anchors = soup.select("a.video-link")
    assert len(anchors) == 2

    first_img = anchors[0].select_one("img")
    # src attribute missing, should fall back to data-src
    thumbnail = utils.safe_get_attr(first_img, "src", ["data-src"])
    assert thumbnail == "//cdn.example.com/thumb-alpha.jpg"

    second_img = anchors[1].select_one("img")
    # src attribute present, primary lookup should succeed
    assert (
        utils.safe_get_attr(second_img, "src", ["data-src"])
        == "//cdn.example.com/thumb-beta.jpg"
    )


def test_safe_get_text_strips_whitespace():
    soup = utils.parse_html(read_fixture("sample_listing.html"))
    anchor = soup.select_one("a.video-link:last-of-type")
    assert utils.safe_get_text(anchor) == "Beta Video"


def test_safe_get_helpers_return_defaults_when_missing():
    assert (
        utils.safe_get_attr(None, "href", ["data-href"], default="missing") == "missing"
    )
    assert utils.safe_get_text(None, default="missing") == "missing"


def test_prefquality_selects_top_available_quality_with_aliases(monkeypatch):
    monkeypatch.setattr(
        utils.addon, "_settings", {**utils.addon._settings, "qualityask": "1"}
    )

    sources = {
        "4k": "https://cdn.example.com/video-4k.mp4",
        "1080p60": "https://cdn.example.com/video-1080p60.mp4",
        "720p": "https://cdn.example.com/video-720p.mp4",
    }

    selected = utils.prefquality(sources)

    # With qualityask set to 1 (1080p threshold), prefquality caps selections
    # at the desired quality and picks the highest source that does not exceed
    # it (after normalizing aliases like 4k -> 2160 and 1080p60 -> 1080).
    assert selected == "https://cdn.example.com/video-1080p60.mp4"


def test_prefquality_selects_2160p_when_quality_0(monkeypatch):
    monkeypatch.setattr(
        utils.addon, "_settings", {**utils.addon._settings, "qualityask": "0"}
    )

    sources = {
        "2160p": "https://cdn.example.com/video-4k.mp4",
        "1080p": "https://cdn.example.com/video-1080p.mp4",
        "720p": "https://cdn.example.com/video-720p.mp4",
    }

    assert utils.prefquality(sources) == "https://cdn.example.com/video-4k.mp4"


def test_prefquality_selects_720p_when_quality_2(monkeypatch):
    monkeypatch.setattr(
        utils.addon, "_settings", {**utils.addon._settings, "qualityask": "2"}
    )

    sources = {
        "2160p": "https://cdn.example.com/video-4k.mp4",
        "1080p": "https://cdn.example.com/video-1080p.mp4",
        "720p": "https://cdn.example.com/video-720p.mp4",
        "480p": "https://cdn.example.com/video-480p.mp4",
    }

    assert utils.prefquality(sources) == "https://cdn.example.com/video-720p.mp4"


def test_prefquality_selects_576p_when_quality_3(monkeypatch):
    monkeypatch.setattr(
        utils.addon, "_settings", {**utils.addon._settings, "qualityask": "3"}
    )

    sources = {
        "1080p": "https://cdn.example.com/video-1080p.mp4",
        "720p": "https://cdn.example.com/video-720p.mp4",
        "576p": "https://cdn.example.com/video-576p.mp4",
    }

    assert utils.prefquality(sources) == "https://cdn.example.com/video-576p.mp4"


def test_prefquality_defers_to_selector_when_configured(monkeypatch):
    monkeypatch.setattr(
        utils.addon, "_settings", {**utils.addon._settings, "qualityask": "4"}
    )

    called = {}

    def fake_selector(prompt, items, sort_by=None, reverse=False):
        called["prompt"] = prompt
        called["sort_by"] = sort_by
        called["reverse"] = reverse
        return "picked"

    monkeypatch.setattr(utils, "selector", fake_selector)

    result = utils.prefquality(
        {"360p": "low", "720p": "mid"}, sort_by=lambda k: k, reverse=True
    )

    assert result == "picked"
    assert called["prompt"] == utils.i18n("pick_qual")
    assert called["reverse"] is True
    assert callable(called["sort_by"])
    assert called["sort_by"]("key") == "key"


def test_prefquality_falls_back_to_lowest_when_all_sources_exceed_limit(monkeypatch):
    monkeypatch.setattr(
        utils.addon, "_settings", {**utils.addon._settings, "qualityask": "3"}
    )

    sources = {
        "1080p": "https://cdn.example.com/video-1080p.mp4",
        "720p": "https://cdn.example.com/video-720p.mp4",
    }

    assert utils.prefquality(sources) == "https://cdn.example.com/video-720p.mp4"


def test_soup_videos_list_handles_missing_soup():
    class _Site:
        url = "https://example.com"

        @staticmethod
        def add_download_link(*args, **kwargs):
            return None

        @staticmethod
        def add_dir(*args, **kwargs):
            return None

    result = utils.soup_videos_list(_Site, None, {"items": ".card"})

    assert result["items"] == 0
    assert result["skipped"] == 0
    assert result["pagination"] == {}


def test_soup_videos_list_skips_invalid_entries_and_finds_pagination():
    html = """
    <div class='card'>
      <a class='video-link' href='/videos/valid'>
        <img data-src='//cdn.example.com/valid.jpg' alt=' Valid Title ' />
        <span class='length'>05:15</span>
      </a>
    </div>
    <div class='card'>
      <a class='video-link' href=''>
        <img src='//cdn.example.com/missing.jpg' alt='' />
      </a>
    </div>
    <nav class='pager'>
      <a class='next' data-href='page/2'>Next »</a>
    </nav>
    """
    soup = utils.parse_html(html)
    captured = {"videos": [], "dirs": []}

    class _Site:
        url = "https://example.com"

        @staticmethod
        def add_download_link(
            name,
            url,
            mode,
            iconimage,
            desc="",
            contextm=None,
            fanart=None,
            duration="",
            quality="",
        ):
            captured["videos"].append(
                {"name": name, "url": url, "thumb": iconimage, "duration": duration}
            )

        @staticmethod
        def add_dir(name, url, mode, *args, **kwargs):
            captured["dirs"].append({"name": name, "url": url, "mode": mode})

    selectors = {
        "items": ".card",
        "url": {"selector": "a.video-link", "attr": "href"},
        "title": {
            "selector": "img",
            "attr": "alt",
            "clean": True,
            "fallback_selectors": ["a.video-link"],
        },
        "thumbnail": {"selector": "img", "attr": "data-src", "fallback_attrs": ["src"]},
        "duration": {"selector": ".length", "text": True, "clean": True, "default": ""},
        "pagination": {
            "selector": "a.next",
            "attr": "data-href",
            "text_matches": ["next"],
            "base_url": "https://example.com/list/",
        },
    }

    result = utils.soup_videos_list(_Site, soup, selectors)

    assert result["items"] == 1
    assert result["skipped"] == 1
    assert captured["videos"][0]["url"] == "https://example.com/videos/valid"
    assert captured["videos"][0]["duration"] == "05:15"
    assert captured["dirs"][0]["url"] == "https://example.com/list/page/2"


# ============================================================================
# Text Cleaning and HTML Utilities
# ============================================================================


def test_cleantext_decodes_html_entities():
    text = "&amp;Hello&nbsp;World&excl;&quot;Test&quot;"
    result = utils.cleantext(text)
    assert result == '&Hello World!"Test"'


def test_cleantext_handles_unicode_nbsp():
    text = "Hello\xa0World"
    result = utils.cleantext(text)
    assert result == "Hello World"


def test_cleantext_strips_whitespace():
    text = "  &nbsp; Test &nbsp;  "
    result = utils.cleantext(text)
    assert result == "Test"


def test_cleantext_handles_special_entities():
    text = "&lt;tag&gt;&lpar;test&rpar;&lsqb;1&rsqb;"
    result = utils.cleantext(text)
    assert result == "<tag>(test)[1]"


def test_cleanhtml_removes_html_tags():
    html = "<p>This is <strong>bold</strong> text</p>"
    result = utils.cleanhtml(html)
    assert result == "This is bold text"


def test_cleanhtml_handles_empty_tags():
    html = "<div><span></span>Content<br/></div>"
    result = utils.cleanhtml(html)
    assert result == "Content"


def test_cleanhtml_handles_nested_tags():
    html = "<div><p><span><em>Nested</em></span></p></div>"
    result = utils.cleanhtml(html)
    assert result == "Nested"


# ============================================================================
# URL and Host Utilities
# ============================================================================


def test_get_vidhost_extracts_domain():
    url = "https://www.example.com/video/123"
    result = utils.get_vidhost(url)
    assert result == "example.com"


def test_get_vidhost_handles_subdomain():
    url = "https://cdn.example.com/video/123"
    result = utils.get_vidhost(url)
    assert result == "example.com"


def test_get_vidhost_handles_country_tld():
    url = "https://example.co.uk/video"
    result = utils.get_vidhost(url)
    assert result == "example.co.uk"


def test_get_vidhost_handles_protocol_relative_url():
    url = "//cdn.example.com/video"
    result = utils.get_vidhost(url)
    assert result == "example.com"


def test_get_vidhost_handles_no_protocol():
    url = "cdn.example.com/video"
    result = utils.get_vidhost(url)
    assert result == "example.com"


def test_get_vidhost_handles_ipv4_address():
    url = "http://192.168.1.1:8080/video"
    result = utils.get_vidhost(url)
    assert result == "192.168.1.1"


def test_get_vidhost_handles_invalid_url():
    url = "not-a-valid-url"
    result = utils.get_vidhost(url)
    # Should return empty string for invalid URLs
    assert isinstance(result, str)


# ============================================================================
# Language and Country Code Lookups
# ============================================================================


def test_get_language_returns_english():
    result = utils.get_language("en")
    assert result == "English"


def test_get_language_returns_spanish():
    result = utils.get_language("es")
    assert result == "Spanish"


def test_get_language_returns_french():
    result = utils.get_language("fr")
    assert result == "French"


def test_get_language_returns_german():
    result = utils.get_language("de")
    assert result == "German"


def test_get_language_returns_japanese():
    result = utils.get_language("ja")
    assert result == "Japanese"


def test_get_language_handles_invalid_code():
    result = utils.get_language("zz")
    # Should return the code itself or empty string for unknown codes
    assert result in ("zz", "", None)


def test_get_country_returns_usa():
    result = utils.get_country("US")
    assert result == "United States"


def test_get_country_returns_uk():
    result = utils.get_country("GB")
    assert result == "United Kingdom"


def test_get_country_returns_france():
    result = utils.get_country("FR")
    assert result == "France"


def test_get_country_returns_germany():
    result = utils.get_country("DE")
    assert result == "Germany"


def test_get_country_returns_japan():
    result = utils.get_country("JP")
    assert result == "Japan"


def test_get_country_handles_invalid_code():
    result = utils.get_country("ZZ")
    # Should return the code itself or empty string for unknown codes
    assert result in ("ZZ", "", None)


# ============================================================================
# Internationalization
# ============================================================================


def test_i18n_returns_string_for_valid_key(monkeypatch):
    # Mock the addon.getLocalizedString to return a test string
    def mock_get_localized(string_id):
        return "Test String"

    monkeypatch.setattr(utils.addon, "getLocalizedString", mock_get_localized)

    # Mock strings.STRINGS to contain the key
    monkeypatch.setattr(utils.strings, "STRINGS", {"test_key": 12345})

    result = utils.i18n("test_key")
    assert result == "Test String"


def test_i18n_returns_key_for_invalid_key(monkeypatch):
    # Mock strings.STRINGS to not contain the key
    monkeypatch.setattr(utils.strings, "STRINGS", {})

    result = utils.i18n("nonexistent_key")
    # Should return the key itself when lookup fails
    assert result == "nonexistent_key"


# ============================================================================
# Logging
# ============================================================================


def test_kodilog_calls_xbmc_log(monkeypatch):
    logged = []

    def mock_log(msg, level):
        logged.append({"msg": msg, "level": level})

    monkeypatch.setattr(utils.xbmc, "log", mock_log)

    utils.kodilog("Test message", utils.xbmc.LOGINFO)

    assert len(logged) == 1
    assert "Test message" in logged[0]["msg"]
    assert logged[0]["level"] == utils.xbmc.LOGINFO


def test_kodilog_converts_to_string(monkeypatch):
    logged = []

    def mock_log(msg, level):
        logged.append({"msg": msg, "level": level})

    monkeypatch.setattr(utils.xbmc, "log", mock_log)

    utils.kodilog(12345)

    assert len(logged) == 1
    assert "12345" in logged[0]["msg"]


# ============================================================================
# Parse Query
# ============================================================================


def test_parse_query_extracts_single_param():
    query = "key1=value1"
    result = utils.parse_query(query)
    # parse_query always adds a default mode
    assert result["key1"] == "value1"
    assert result["mode"] == "main.INDEX"


def test_parse_query_extracts_multiple_params():
    query = "key1=value1&key2=value2&key3=value3"
    result = utils.parse_query(query)
    assert result["key1"] == "value1"
    assert result["key2"] == "value2"
    assert result["key3"] == "value3"
    assert result["mode"] == "main.INDEX"


def test_parse_query_decodes_url_encoding():
    query = "name=Hello+World&url=https%3A%2F%2Fexample.com"
    result = utils.parse_query(query)
    assert result["name"] == "Hello World"
    assert result["url"] == "https://example.com"


def test_parse_query_converts_special_keys_to_int():
    # Only specific keys are converted to int: page, download, favmode, channel, section
    query = "page=1&download=2&favmode=3"
    result = utils.parse_query(query)
    assert result["page"] == 1
    assert result["download"] == 2
    assert result["favmode"] == 3
    assert isinstance(result["page"], int)


def test_parse_query_keeps_other_numeric_as_string():
    # Keys not in the special list remain strings
    query = "count=50&id=123"
    result = utils.parse_query(query)
    assert result["count"] == "50"
    assert result["id"] == "123"


def test_parse_query_handles_empty_values():
    # parse_qs skips empty values, so key1 won't be in the result
    query = "key1=&key2=value"
    result = utils.parse_query(query)
    assert "key1" not in result
    assert result["key2"] == "value"


def test_parse_query_strips_leading_question_mark():
    query = "?page=5&mode=test.mode"
    result = utils.parse_query(query)
    assert result["page"] == 5
    assert result["mode"] == "test.mode"


def test_parse_query_handles_multiple_values():
    query = "tag=action&tag=comedy"
    result = utils.parse_query(query)
    # When a key has multiple values, it returns a list
    assert result["tag"] == ["action", "comedy"]


# ============================================================================
# URL Processing and Normalization
# ============================================================================


def test_notify_with_default_params(monkeypatch):
    """Test notify function with default parameters"""
    notifications = []

    def mock_notification(title, msg, icon, duration, sound):
        notifications.append({
            "title": title,
            "msg": msg,
            "icon": icon,
            "duration": duration,
            "sound": sound
        })

    mock_dialog = type('Dialog', (), {})()
    mock_dialog.notification = mock_notification
    monkeypatch.setattr(utils, "dialog", mock_dialog)

    utils.notify(msg="Test message")

    assert len(notifications) == 1
    assert notifications[0]["msg"] == "Test message"
    assert notifications[0]["duration"] == 5000


def test_notify_with_custom_params(monkeypatch):
    """Test notify function with custom parameters"""
    notifications = []

    def mock_notification(title, msg, icon, duration, sound):
        notifications.append({
            "title": title,
            "msg": msg,
            "duration": duration
        })

    mock_dialog = type('Dialog', (), {})()
    mock_dialog.notification = mock_notification
    monkeypatch.setattr(utils, "dialog", mock_dialog)

    utils.notify(header="Custom Header", msg="Custom message", duration=3000)

    assert len(notifications) == 1
    assert notifications[0]["msg"] == "Custom message"
    assert notifications[0]["duration"] == 3000


def test_refresh_calls_container_refresh(monkeypatch):
    """Test refresh function calls Kodi's Container.Refresh"""
    executed = []

    def mock_executebuiltin(command):
        executed.append(command)

    monkeypatch.setattr(utils.xbmc, "executebuiltin", mock_executebuiltin)

    utils.refresh()

    assert len(executed) == 1
    assert "Container.Refresh" in executed[0]


def test_setSorted_sets_setting(monkeypatch):
    """Test setSorted sets the sorted setting"""
    settings = {}

    def mock_setSetting(key, value):
        settings[key] = value

    monkeypatch.setattr(utils.addon, "setSetting", mock_setSetting)

    executed = []

    def mock_executebuiltin(command):
        executed.append(command)

    monkeypatch.setattr(utils.xbmc, "executebuiltin", mock_executebuiltin)

    utils.setSorted()

    assert settings.get("keywords_sorted") == "true"
    assert len(executed) == 1


def test_setUnsorted_sets_setting(monkeypatch):
    """Test setUnsorted sets the unsorted setting"""
    settings = {}

    def mock_setSetting(key, value):
        settings[key] = value

    monkeypatch.setattr(utils.addon, "setSetting", mock_setSetting)

    executed = []

    def mock_executebuiltin(command):
        executed.append(command)

    monkeypatch.setattr(utils.xbmc, "executebuiltin", mock_executebuiltin)

    utils.setUnsorted()

    assert settings.get("keywords_sorted") == "false"
    assert len(executed) == 1


# ============================================================================
# Safe Get Attributes Edge Cases
# ============================================================================


def test_safe_get_attr_with_none_element_returns_default():
    """Test safe_get_attr returns default when element is None"""
    result = utils.safe_get_attr(None, "href", default="default_value")
    assert result == "default_value"


def test_safe_get_attr_with_empty_attribute_tries_fallback():
    """Test safe_get_attr tries fallback when primary attr is empty"""
    from bs4 import BeautifulSoup

    html = '<img data-src="fallback.jpg" />'
    soup = BeautifulSoup(html, "html.parser")
    img = soup.select_one("img")

    # Primary attr 'src' doesn't exist, should fall back to 'data-src'
    result = utils.safe_get_attr(img, "src", ["data-src"])
    assert result == "fallback.jpg"


def test_safe_get_text_without_strip():
    """Test safe_get_text without stripping whitespace"""
    from bs4 import BeautifulSoup

    html = '<span>  Text with spaces  </span>'
    soup = BeautifulSoup(html, "html.parser")
    span = soup.select_one("span")

    result = utils.safe_get_text(span, strip=False)
    assert result == "  Text with spaces  "


def test_safe_get_text_with_strip():
    """Test safe_get_text with stripping whitespace"""
    from bs4 import BeautifulSoup

    html = '<span>  Text with spaces  </span>'
    soup = BeautifulSoup(html, "html.parser")
    span = soup.select_one("span")

    result = utils.safe_get_text(span, strip=True)
    assert result == "Text with spaces"


# ============================================================================
# Additional Parse HTML Tests
# ============================================================================


def test_parse_html_handles_malformed_html():
    """Test parse_html can handle malformed HTML"""
    malformed_html = '<div><p>Unclosed paragraph<div>Another div</div>'
    soup = utils.parse_html(malformed_html)

    # BeautifulSoup should still parse it
    assert soup is not None
    divs = soup.find_all('div')
    assert len(divs) >= 1


def test_parse_html_handles_unicode():
    """Test parse_html handles unicode characters"""
    html = '<div>Unicode: \u00e9\u00e8\u00ea \u4e2d\u6587</div>'
    soup = utils.parse_html(html)

    div = soup.select_one('div')
    text = utils.safe_get_text(div)
    assert '\u00e9' in text or 'é' in text


def test_parse_html_preserves_attributes():
    """Test parse_html preserves element attributes"""
    html = '<a href="/video/123" data-id="456" class="link">Video</a>'
    soup = utils.parse_html(html)

    link = soup.select_one('a')
    assert link.get('href') == '/video/123'
    assert link.get('data-id') == '456'
    assert 'link' in link.get('class', [])
