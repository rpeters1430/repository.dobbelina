import pytest

from resources.lib.sites import tabootube


def _raise_get_html(*_, **__):
    raise ValueError("boom")


def test_tabootube_list_logs_and_raises(monkeypatch):
    messages = []

    monkeypatch.setattr(tabootube.utils, "getHtml", _raise_get_html)
    monkeypatch.setattr(tabootube.utils, "kodilog", lambda msg, level=None: messages.append((msg, level)))

    with pytest.raises(ValueError):
        tabootube.List("https://example.com", page=5)

    assert messages == [
        ("TabooTube: Failed to fetch list page 5: boom", tabootube.xbmc.LOGERROR),
    ]


def test_tabootube_categories_logs_and_raises(monkeypatch):
    messages = []

    monkeypatch.setattr(tabootube.utils, "getHtml", _raise_get_html)
    monkeypatch.setattr(tabootube.utils, "kodilog", lambda msg, level=None: messages.append((msg, level)))

    with pytest.raises(ValueError):
        tabootube.Categories("https://example.com/categories")

    assert messages == [
        ("TabooTube: Failed to fetch categories: boom", tabootube.xbmc.LOGERROR),
    ]
