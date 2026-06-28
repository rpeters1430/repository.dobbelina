from unittest.mock import MagicMock, patch

from scripts import track_and_test_new_sites


def test_normalize():
    assert track_and_test_new_sites.normalize("AnySex.com") == "anysexcom"
    assert track_and_test_new_sites.normalize("Porn-Doe") == "porndoe"
    assert track_and_test_new_sites.normalize("HQ Porner") == "hqporner"


def test_same_site():
    assert track_and_test_new_sites.same_site("https://example.com", "https://example.com/video")
    assert track_and_test_new_sites.same_site("https://example.com", "https://www.example.com/video")
    assert not track_and_test_new_sites.same_site("https://example.com", "https://another.com")


def test_host_changed():
    assert track_and_test_new_sites.host_changed("https://example.com", "https://another.com")
    assert not track_and_test_new_sites.host_changed("https://example.com", "https://example.com/page")
    assert not track_and_test_new_sites.host_changed("https://example.com", "https://www.example.com")


def test_count_playback_signals():
    html = "<html><body><video src='video.mp4'></video><script src='jwplayer.js'></script></body></html>"
    assert track_and_test_new_sites.count_playback_signals(html) == 4


def test_likely_video_links_filters_correctly():
    html = """
    <html>
      <body>
        <a href="/video/123-cool-scene.html">Watch Now</a>
        <a href="/category/all">Categories</a>
        <a href="https://external.com/video/123">External Link</a>
        <a href="/watch/abc">Watch abc</a>
      </body>
    </html>
    """
    links = track_and_test_new_sites.likely_video_links("https://example.com", html)
    assert "https://example.com/video/123-cool-scene.html" in links
    assert "https://example.com/watch/abc" in links
    assert "https://example.com/category/all" not in links
    assert "https://external.com/video/123" not in links


def test_generate_suggested_markdown():
    candidate = track_and_test_new_sites.Candidate(
        name="Porninja",
        url="https://porninja.com",
        category="Streaming & Video Tubes"
    )
    val = track_and_test_new_sites.Validation(
        candidate=candidate,
        status="PROMISING",
        final_url="https://porninja.com",
        http_status=200,
        bytes_read=10000,
        title="Porninja",
        video_links=5,
        playback_signals=1,
        sampled_video_url="https://porninja.com/video/123",
        sampled_video_status=200,
        sampled_playback_signals=2,
        reasons=[]
    )
    md = track_and_test_new_sites.generate_suggested_markdown([val])
    assert "| **Porninja** | Streaming & Video Tubes | Easy | [ ] |" in md
    assert "5 video links" in md
    assert "Sample playback signals: 2" in md


@patch("requests.Session")
def test_validate_candidate_promising(mock_session_class):
    mock_session = mock_session_class.return_value
    
    # Mock responses: homepage and sample video page
    mock_response_home = MagicMock()
    mock_response_home.status_code = 200
    mock_response_home.url = "https://example.com"
    mock_response_home.text = '<a href="/video/123.html">video</a>' + (' ' * 2000)
    
    mock_response_video = MagicMock()
    mock_response_video.status_code = 200
    mock_response_video.url = "https://example.com/video/123.html"
    mock_response_video.text = "<video src='test.mp4'></video>"
    
    mock_session.get.side_effect = [mock_response_home, mock_response_video]
    
    candidate = track_and_test_new_sites.Candidate(
        name="ExampleSite",
        url="https://example.com",
        category="Streaming & Video Tubes"
    )
    
    val = track_and_test_new_sites.validate_candidate(mock_session, candidate, timeout=10)
    
    assert val.status == "PROMISING"
    assert val.video_links == 1
    assert val.sampled_video_url == "https://example.com/video/123.html"
    assert val.sampled_playback_signals == 2  # matches ".mp4" and "<video" (2 patterns)
    assert not val.reasons
