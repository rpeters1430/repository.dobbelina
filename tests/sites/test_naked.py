"""Tests for naked.com site implementation."""

import json
from resources.lib.sites import naked


def test_list_parses_json_models(monkeypatch):
    """Test that List correctly parses JSON model data."""
    models_json = [
        {
            "model_seo_name": "test-model-1",
            "model_id": "12345",
            "age": 25,
            "location": "USA",
            "tagline": "Welcome to my room",
            "topic": "Come and chat!",
            "room_status": "In Open",
            "video_host": "host1.example.com",
        },
        {
            "model_seo_name": "test-model-2",
            "model_id": "67890",
            "age": 22,
            "location": "Colombia",
            "tagline": "Private show",
            "topic": "Tip me!",
            "room_status": "In Private",
            "video_host": "host2.example.com",
        },
    ]

    html = f"""
    <html>
    <script>
    window.__DATA__ = {{"models": {json.dumps(models_json)}}};
    </script>
    </html>
    """

    downloads = []

    def fake_get_html(url, *args, **kwargs):
        return html

    def fake_add_download_link(name, url, mode, iconimage, desc, **kwargs):
        downloads.append({"name": name, "url": url, "icon": iconimage, "desc": desc})

    monkeypatch.setattr(naked.utils, "_getHtml", fake_get_html)
    monkeypatch.setattr(naked.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(naked.utils, "eod", lambda: None)
    monkeypatch.setattr(naked.utils.addon, "getSetting", lambda x: "false")

    naked.List("https://www.naked.com/live/girls/")

    assert len(downloads) == 2
    assert "Test Model 1" in downloads[0]["name"]
    assert "25" in downloads[0]["name"]
    assert "model_id=12345" in downloads[0]["url"]
    assert "video_host=host1.example.com" in downloads[0]["url"]
    assert "Welcome to my room" in downloads[0]["desc"]

    assert "Test Model 2" in downloads[1]["name"]
    assert "In Private" in downloads[1]["name"]


def test_list_handles_empty_models(monkeypatch):
    """Test that List handles empty models array gracefully."""
    html = """
    <html>
    <script>
    window.__DATA__ = {"models": []};
    </script>
    </html>
    """

    downloads = []

    def fake_notify(*args, **kwargs):
        pass

    monkeypatch.setattr(naked.utils, "_getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        naked.site, "add_download_link", lambda *a, **k: downloads.append(1)
    )
    monkeypatch.setattr(naked.utils, "eod", lambda: None)
    monkeypatch.setattr(naked.utils.addon, "getSetting", lambda x: "false")
    monkeypatch.setattr(naked.utils, "notify", fake_notify)

    naked.List("https://www.naked.com/live/girls/")

    # No models should be added
    assert len(downloads) == 0


def test_list_skips_models_without_required_fields(monkeypatch):
    """Test that List skips models missing required fields."""
    models_json = [
        {
            "model_seo_name": "valid-model",
            "model_id": "12345",
            "age": 25,
            "room_status": "In Open",
            "video_host": "host1.example.com",
        },
        {
            "model_seo_name": "no-model-id",
            "age": 22,
            "room_status": "In Open",
            "video_host": "host2.example.com",
            # Missing model_id
        },
        {
            "model_seo_name": "no-video-host",
            "model_id": "99999",
            "age": 28,
            "room_status": "In Open",
            # Missing video_host
        },
    ]

    html = f"""
    <html>
    <script>
    window.__DATA__ = {{"models": {json.dumps(models_json)}}};
    </script>
    </html>
    """

    downloads = []

    monkeypatch.setattr(naked.utils, "_getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        naked.site, "add_download_link", lambda *a, **k: downloads.append(a[0])
    )
    monkeypatch.setattr(naked.utils, "eod", lambda: None)
    monkeypatch.setattr(naked.utils.addon, "getSetting", lambda x: "false")

    naked.List("https://www.naked.com/live/girls/")

    # Only the valid model should be added
    assert len(downloads) == 1
    assert "Valid Model" in downloads[0]
