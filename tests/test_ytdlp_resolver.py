"""
Unit tests for yt-dlp Resolver Bridge module.
"""

from unittest.mock import MagicMock, patch
from resources.lib import ytdlp_resolver


def test_ytdlp_resolver_extract_direct_url():
    fake_info = {
        "url": "https://stream.cdn.com/video.mp4",
        "http_headers": {
            "User-Agent": "Custom-UA/1.0",
            "Referer": "https://source.com/",
        },
    }

    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.return_value = fake_info

    mock_ydl_class = MagicMock()
    mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

    with patch.object(ytdlp_resolver, "_get_ydl_class", return_value=mock_ydl_class):
        resolved = ytdlp_resolver.resolve_url("https://source.com/watch?v=123")
        assert resolved is not None
        assert "https://stream.cdn.com/video.mp4" in resolved
        assert "User-Agent=Custom-UA%2F1.0" in resolved
        assert "Referer=https%3A%2F%2Fsource.com%2F" in resolved


def test_ytdlp_resolver_extract_from_formats():
    fake_info = {
        "formats": [
            {"format_id": "720p", "url": "https://stream.cdn.com/720p.mp4"},
            {"format_id": "1080p", "url": "https://stream.cdn.com/1080p.mp4"},
        ]
    }

    mock_ydl_instance = MagicMock()
    mock_ydl_instance.extract_info.return_value = fake_info

    mock_ydl_class = MagicMock()
    mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

    with patch.object(ytdlp_resolver, "_get_ydl_class", return_value=mock_ydl_class):
        resolved = ytdlp_resolver.resolve_url("https://source.com/video456")
        assert resolved == "https://stream.cdn.com/1080p.mp4"


def test_ytdlp_resolver_unavailable():
    with patch.object(ytdlp_resolver, "_get_ydl_class", return_value=None):
        resolved = ytdlp_resolver.resolve_url("https://source.com/video")
        assert resolved is None
