import pytest

from resources.lib.sites import tabootube


def _raise_get_html(*_, **__):
    raise ValueError("boom")


def _empty_get_html(*_, **__):
    return ""


def test_tabootube_list_logs_and_raises(monkeypatch):
    messages = []

    monkeypatch.setattr(tabootube.utils, "getHtml", _raise_get_html)
    monkeypatch.setattr(
        tabootube.utils,
        "kodilog",
        lambda msg, level=None: messages.append((msg, level)),
    )

    with pytest.raises(ValueError):
        tabootube.List("https://example.com", page=5)

    assert messages == [
        ("TabooTube: Failed to fetch list page 5: boom", tabootube.xbmc.LOGERROR),
    ]


def test_tabootube_categories_logs_and_raises(monkeypatch):
    messages = []

    monkeypatch.setattr(tabootube.utils, "getHtml", _raise_get_html)
    monkeypatch.setattr(
        tabootube.utils,
        "kodilog",
        lambda msg, level=None: messages.append((msg, level)),
    )

    with pytest.raises(ValueError):
        tabootube.Categories("https://example.com/categories")

    assert messages == [
        ("TabooTube: Failed to fetch categories: boom", tabootube.xbmc.LOGERROR),
    ]


def test_tabootube_tags_logs_and_raises(monkeypatch):
    messages = []

    monkeypatch.setattr(tabootube.utils, "getHtml", _raise_get_html)
    monkeypatch.setattr(
        tabootube.utils,
        "kodilog",
        lambda msg, level=None: messages.append((msg, level)),
    )

    with pytest.raises(ValueError):
        tabootube.Tags("https://example.com/tags")

    assert messages == [
        ("TabooTube: Failed to fetch tags: boom", tabootube.xbmc.LOGERROR),
    ]


def test_tabootube_list_logs_empty_response(monkeypatch):
    messages = []
    eod_calls = []

    monkeypatch.setattr(tabootube.utils, "getHtml", _empty_get_html)
    monkeypatch.setattr(
        tabootube.utils,
        "kodilog",
        lambda msg, level=None: messages.append((msg, level)),
    )
    monkeypatch.setattr(tabootube.utils, "eod", lambda: eod_calls.append("eod"))

    assert tabootube.List("https://example.com", page=2) is None

    assert messages == [
        (
            "TabooTube: Got empty response for list page 2 at https://example.com",
            tabootube.xbmc.LOGWARNING,
        ),
    ]
    assert eod_calls == ["eod"]


def test_tabootube_categories_logs_empty_response(monkeypatch):
    messages = []
    eod_calls = []

    monkeypatch.setattr(tabootube.utils, "getHtml", _empty_get_html)
    monkeypatch.setattr(
        tabootube.utils,
        "kodilog",
        lambda msg, level=None: messages.append((msg, level)),
    )
    monkeypatch.setattr(tabootube.utils, "eod", lambda: eod_calls.append("eod"))

    assert tabootube.Categories("https://example.com/categories") is None

    assert messages == [
        (
            "TabooTube: Got empty response for categories at https://example.com/categories",
            tabootube.xbmc.LOGWARNING,
        ),
    ]
    assert eod_calls == ["eod"]


def test_tabootube_tags_logs_empty_response(monkeypatch):
    messages = []
    eod_calls = []

    monkeypatch.setattr(tabootube.utils, "getHtml", _empty_get_html)
    monkeypatch.setattr(
        tabootube.utils,
        "kodilog",
        lambda msg, level=None: messages.append((msg, level)),
    )
    monkeypatch.setattr(tabootube.utils, "eod", lambda: eod_calls.append("eod"))

    assert tabootube.Tags("https://example.com/tags") is None

    assert messages == [
        (
            "TabooTube: Got empty response for tags at https://example.com/tags",
            tabootube.xbmc.LOGWARNING,
        ),
    ]
    assert eod_calls == ["eod"]
