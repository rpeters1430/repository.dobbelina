"""Tests for RedTube Playvid video extraction."""

from resources.lib.sites import redtube


def test_extract_best_source_prefers_higher_quality():
    """Test that extraction selects highest quality video."""
    # Simplified test - just verify quality selection works
    html = """
    <html>
    <script>
    var videos = [
        {"quality":"720","videoUrl":"https://example.com/video_720p.mp4"},
        {"quality":"480","videoUrl":"https://example.com/video_480p.mp4"},
        {"quality":"240","videoUrl":"https://example.com/video_240p.mp4"}
    ];
    </script>
    </html>
    """

    def mock_kodilog(msg):
        pass

    original_kodilog = redtube.utils.kodilog
    redtube.utils.kodilog = mock_kodilog

    try:
        result = redtube._extract_best_source(html)

        # Should return 720p (highest quality)
        assert "720p" in result, f"Should select 720p quality, got: {result}"
        assert "example.com" in result, f"Should have video URL, got: {result}"

    finally:
        redtube.utils.kodilog = original_kodilog


def test_extract_best_source_filters_preview_videos():
    """Test that _fb.mp4 preview videos are filtered out."""
    html = """
    <html>
    <body>
    <script>
    var sources = [
        "https://example.com/720P_4000K_video.mp4",
        "https://example.com/360P_360K_video_fb.mp4",
        "https://example.com/480P_2000K_video.mp4"
    ];
    </script>
    </body>
    </html>
    """

    def mock_kodilog(msg):
        pass

    original_kodilog = redtube.utils.kodilog
    redtube.utils.kodilog = mock_kodilog

    try:
        result = redtube._extract_best_source(html)

        # Should NOT include _fb.mp4 preview
        assert "_fb.mp4" not in result, (
            f"Should filter out preview videos, got: {result}"
        )

        # Should get highest quality non-preview video
        assert "720P" in result or "480P" in result, (
            f"Should get proper quality video, got: {result}"
        )

    finally:
        redtube.utils.kodilog = original_kodilog


def test_extract_best_source_with_direct_urls():
    """Test extraction when direct URLs are in JSON."""
    html = """
    <html>
    <script>
    var mediaDefinitions = [
        {"quality":"720","videoUrl":"https://example.com/video_720p.mp4"},
        {"quality":"480","videoUrl":"https://example.com/video_480p.mp4"}
    ];
    </script>
    </html>
    """

    def mock_kodilog(msg):
        pass

    original_kodilog = redtube.utils.kodilog
    redtube.utils.kodilog = mock_kodilog

    try:
        result = redtube._extract_best_source(html)

        # Should return 720p (highest quality)
        assert "720p" in result, f"Should select 720p quality, got: {result}"
        assert "example.com" in result, f"Should have video URL, got: {result}"

    finally:
        redtube.utils.kodilog = original_kodilog


def test_extract_best_source_returns_empty_when_no_videos():
    """Test that empty string is returned when no videos found."""
    html = "<html><body>No videos here</body></html>"

    def mock_kodilog(msg):
        pass

    original_kodilog = redtube.utils.kodilog
    redtube.utils.kodilog = mock_kodilog

    try:
        result = redtube._extract_best_source(html)
        assert result == "", "Should return empty string when no videos found"

    finally:
        redtube.utils.kodilog = original_kodilog
