import http.server
import threading
import urllib.parse
import urllib.request
import pytest
from scripts.media_validator import validate_media


class MockMediaHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/video.mp4":
            self.send_response(206 if "Range" in self.headers else 200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", "1024")
            self.end_headers()
            self.wfile.write(b"\x00" * 1024)

        elif path == "/master.m3u8":
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.apple.mpegurl")
            self.end_headers()
            self.wfile.write(b"#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=1280000\nindex.m3u8\n")

        elif path == "/index.m3u8":
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.apple.mpegurl")
            self.end_headers()
            self.wfile.write(b"#EXTM3U\n#EXTINF:10.0,\nsegment.ts\n")

        elif path == "/segment.ts":
            self.send_response(200)
            self.send_header("Content-Type", "video/mp2t")
            self.end_headers()
            self.wfile.write(b"\x47" * 512)

        elif path == "/dash.mpd":
            self.send_response(200)
            self.send_header("Content-Type", "application/dash+xml")
            self.end_headers()
            xml = (
                b'<?xml version="1.0"?>'
                b'<MPD xmlns="urn:mpeg:dash:schema:mpd:2011">'
                b'<Period>'
                b'<AdaptationSet mimeType="video/mp4">'
                b'<Representation id="1" bandwidth="100000">'
                b'<BaseURL>dash_segment.m4s</BaseURL>'
                b'</Representation>'
                b'</AdaptationSet>'
                b'</Period>'
                b'</MPD>'
            )
            self.wfile.write(xml)

        elif path == "/dash_segment.m4s":
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.end_headers()
            self.wfile.write(b"\x00" * 512)

        elif path == "/html_error":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body>Video Removed or Not Found</body></html>")

        elif path == "/not_found":
            self.send_response(404)
            self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


@pytest.fixture
def http_server(monkeypatch):
    # Unblock urllib.request.urlopen for loopback server during this fixture
    monkeypatch.undo()

    server = http.server.HTTPServer(("127.0.0.1", 0), MockMediaHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    host, port = server.server_address

    class ServerHelper:
        def url(self, path):
            return f"http://{host}:{port}{path}"

        @property
        def host_port(self):
            return f"{host}:{port}"

    yield ServerHelper()
    server.shutdown()


def test_direct_mp4_bytes(http_server):
    result = validate_media(http_server.url("/video.mp4"), [http_server.host_port, "127.0.0.1"])
    assert result.passed is True
    assert result.metrics["media_kind"] == "direct"
    assert result.metrics["segment_bytes"] > 0


def test_hls_master_to_media_segment(http_server):
    result = validate_media(http_server.url("/master.m3u8"), [http_server.host_port, "127.0.0.1"])
    assert result.passed is True
    assert result.metrics["media_kind"] == "hls"
    assert result.metrics["segment_bytes"] > 0


def test_dash_mpd_to_segment(http_server):
    result = validate_media(http_server.url("/dash.mpd"), [http_server.host_port, "127.0.0.1"])
    assert result.passed is True
    assert result.metrics["media_kind"] == "dash"
    assert result.metrics["segment_bytes"] > 0


def test_pipe_suffixed_kodi_url(http_server):
    kodi_url = f"{http_server.url('/video.mp4')}|User-Agent=CustomUA&Referer=http%3A%2F%2Fexample.test"
    result = validate_media(kodi_url, [http_server.host_port, "127.0.0.1"])
    assert result.passed is True


def test_html_returned_with_200_is_rejected(http_server):
    result = validate_media(http_server.url("/html_error"), [http_server.host_port, "127.0.0.1"])
    assert result.passed is False
    assert result.classification == "HTML_PAYLOAD"


def test_disallowed_host_is_rejected(http_server):
    result = validate_media(http_server.url("/video.mp4"), ["other.host"])
    assert result.passed is False
    assert result.classification == "HOST_DISALLOWED"


def test_expired_link_404_is_rejected(http_server):
    result = validate_media(http_server.url("/not_found"), [http_server.host_port, "127.0.0.1"])
    assert result.passed is False
    assert result.classification == "MEDIA_HTTP_ERROR"
