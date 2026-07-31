import http.server
import json
import threading
import pytest
from scripts.kodi_jsonrpc import KodiClient
from scripts.kodi_site_probe import probe_site


class MockProbeHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        req = json.loads(body)
        method = req.get("method")
        req_id = req.get("id", 1)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if method == "Files.GetDirectory":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "files": [
                        {"file": "plugin://plugin.video.cumination/?mode=pornhub.Play&url=https%3A%2F%2Fpornhub.com%2Fview1", "label": "Video 1", "filetype": "file"},
                        {"file": "plugin://plugin.video.cumination/?mode=pornhub.Play&url=https%3A%2F%2Fpornhub.com%2Fview2", "label": "Video 2", "filetype": "file"},
                    ]
                },
            }
        elif method == "Player.Open":
            res = {"jsonrpc": "2.0", "id": req_id, "result": "OK"}
        elif method == "Player.GetActivePlayers":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": [{"playerid": 1, "type": "video"}],
            }
        elif method == "Player.GetItem":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"item": {"label": "Video 1", "file": "http://cdn.test/v.mp4"}},
            }
        elif method == "Player.Stop":
            res = {"jsonrpc": "2.0", "id": req_id, "result": "OK"}
        else:
            res = {"jsonrpc": "2.0", "id": req_id, "result": "pong"}

        self.wfile.write(json.dumps(res).encode("utf-8"))

    def log_message(self, format, *args):
        pass


@pytest.fixture
def kodi_probe_server():
    server = http.server.HTTPServer(("127.0.0.1", 0), MockProbeHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    host, port = server.server_address
    client = KodiClient(url=f"http://{host}:{port}/jsonrpc", timeout=5.0)
    yield client
    server.shutdown()


def test_probe_site_successful_directory_and_playback(kodi_probe_server):
    result = probe_site(kodi_probe_server, "pornhub", timeout=2.0)
    assert result["passed"] is True
    assert result["item_count"] == 2
    assert result["playback_started"] is True


def test_probe_site_handles_empty_directory(monkeypatch):
    class EmptyClient:
        def call(self, method, params=None):
            if method == "Files.GetDirectory":
                return {"files": []}
            return {}

    result = probe_site(EmptyClient(), "pornhub", timeout=2.0)
    assert result["passed"] is False
    assert result["item_count"] == 0
    assert "Empty directory" in result["message"]
