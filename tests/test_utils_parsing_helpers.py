import pytest

from resources.lib import utils


def test_parse_query_coerces_values_and_lists():
    query = "?url=https://example.com/watch&id=abc&page=5&download=0&channel=12&multi=a&multi=b"

    result = utils.parse_query(query)

    assert result["mode"] == "main.INDEX"
    assert result["url"] == "https://example.com/watch"
    assert result["id"] == "abc"
    # integer coercion
    assert result["page"] == 5
    assert result["download"] == 0
    assert result["channel"] == 12
    # multi-value parameters keep list semantics
    assert result["multi"] == ["a", "b"]


def test_parse_query_gracefully_handles_invalid_ints():
    query = "mode=custom&download=NaN&page=two"

    result = utils.parse_query(query)

    # values that cannot be coerced remain strings
    assert result["download"] == "NaN"
    assert result["page"] == "two"
    assert result["mode"] == "custom"


def test_cleantext_unescapes_entities_and_strips():
    messy = "  &lt;Hello&nbsp;World&gt; &amp; other&amp;apos;s&nbsp; "

    cleaned = utils.cleantext(messy)

    assert cleaned == "<Hello World> & other's"


def test_cleanhtml_strips_tags_preserving_text():
    raw = "<p>Hello <strong>World</strong>!</p>"

    assert utils.cleanhtml(raw) == "Hello World!"


def test_fix_url_handles_protocol_and_baseurl():
    siteurl = "https://example.com/"
    baseurl = "https://example.com/base/"

    assert utils.fix_url("/path", siteurl=siteurl) == "https://example.com/path"
    assert utils.fix_url("?q=test", siteurl=siteurl, baseurl=baseurl) == "https://example.com/base/?q=test"
    assert utils.fix_url("image.jpg", siteurl=siteurl, baseurl=baseurl) == "https://example.com/base/image.jpg"
    assert utils.fix_url("//cdn.example.com/img.png", siteurl=siteurl) == "https://cdn.example.com/img.png"


def test_get_vidhost_extracts_base_domain():
    assert utils.get_vidhost("https://media.sub.hosting.example.co.uk/video.mp4") == "example.co.uk"


@pytest.mark.parametrize(
    "code, expected",
    [
        ("en", "English"),
        ("ES", "Spanish"),
        ("zz", "zz"),
    ],
)
def test_get_language_resolves_known_codes(code, expected):
    assert utils.get_language(code) == expected


@pytest.mark.parametrize(
    "code, expected",
    [
        ("us", "United States"),
        ("GB", "United Kingdom"),
        ("xx", "xx"),
    ],
)
def test_get_country_returns_human_readable_name(code, expected):
    assert utils.get_country(code) == expected
