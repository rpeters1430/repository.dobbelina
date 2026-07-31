import http.server
import json
import threading
import urllib.parse
import pytest
from scripts.kodi_jsonrpc import KodiClient, KodiJSONRPCError


class MockKodiHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        req = json.loads(body)
        method = req.get("method")
        req_id = req.get("id", 1)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if method == "JSONRPC.Ping":
            res = {"jsonrpc": "2.0", "id": req_id, "result": "pong"}
        elif method == "Files.GetDirectory":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "files": [
                        {"file": "plugin://plugin.video.cumination/?mode=play1", "label": "Video 1", "filetype": "file"}
                    ]
                },
            }
        elif method == "JSONRPC.ErrorMethod":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": "Method not found"},
            }
        else:
            res = {"jsonrpc": "2.0", "id": req_id, "result": {}}

        self.wfile.write(json.dumps(res).encode("utf-8"))

    def log_message(self, format, *args):
        pass


@pytest.fixture
def kodi_server():
    server = http.server.HTTPServer(("127.0.0.1", 0), MockKodiHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    host, port = server.server_address
    client = KodiClient(url=f"http://{host}:{port}/jsonrpc", timeout=5.0)
    yield client
    server.shutdown()


def test_kodi_client_ping(kodi_server):
    res = kodi_server.call("JSONRPC.Ping")
    assert res == "pong"


def test_kodi_client_get_directory(kodi_server):
    res = kodi_server.call("Files.GetDirectory", {"directory": "plugin://plugin.video.cumination/"})
    assert "files" in res
    assert len(res["files"]) == 1
    assert res["files"][0]["label"] == "Video 1"


def test_kodi_client_raises_typed_error(kodi_server):
    with pytest.raises(KodiJSONRPCError) as exc_info:
        kodi_server.call("JSONRPC.ErrorMethod")
    assert exc_info.value.code == -32601
    assert "Method not found" in exc_info.value.message


def test_kodi_client_wait_until_ready(kodi_server):
    ready = kodi_server.wait_until_ready(timeout=2.0)
    assert ready is True
