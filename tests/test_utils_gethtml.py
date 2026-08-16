"""Tests for _getHtml handling in utils."""

import gzip
import io


from resources.lib import utils
from resources.lib import flaresolverr


class FakeResponse:
    def __init__(self, payload, headers=None):
        self._payload = payload
        self._headers = headers or {}
        self.headers = self._headers

    def read(self, *args, **kwargs):
        return self._payload

    def info(self):
        return self._headers

    def close(self):
        pass


def test_gethtml_gzip_decodes(monkeypatch):
    content = b"<html>hello</html>"
    gzipped = io.BytesIO()
    with gzip.GzipFile(fileobj=gzipped, mode="wb") as handle:
        handle.write(content)

    response = FakeResponse(
        gzipped.getvalue(),
        headers={
            "Content-Encoding": "gzip",
            "content-type": "text/html; charset=utf-8",
        },
    )

    monkeypatch.setattr(utils, "urlopen", lambda req, timeout=30: response)

    result = utils._getHtml("https://example.com", NoCookie=True)

    assert "hello" in result


def test_gethtml_meta_charset(monkeypatch):
    body = b'<meta charset="utf-8"><div>\xe2\x9c\x93</div>'
    response = FakeResponse(body, headers={})

    monkeypatch.setattr(utils, "urlopen", lambda req, timeout=30: response)

    result = utils._getHtml("https://example.com", NoCookie=True)

    assert "\u2713" in result


def test_gethtml_http_error_404_returns_empty(monkeypatch):
    error = utils.urllib_error.HTTPError(
        "https://example.com",
        404,
        "Not Found",
        {"Content-Encoding": ""},
        io.BytesIO(b"not found"),
    )

    def _raise(_req, timeout=30):
        raise error

    monkeypatch.setattr(utils, "urlopen", _raise)

    assert utils._getHtml("https://example.com") == ""


def test_gethtml_cloudflare_flaresolverr(monkeypatch):
    body = b"__cf_chl_jschl_tk__="
    error = utils.urllib_error.HTTPError(
        "https://example.com",
        403,
        "Forbidden",
        {"Server": "cloudflare", "cf-mitigated": True},
        io.BytesIO(body),
    )

    def _raise(_req, timeout=30):
        raise error

    monkeypatch.setattr(utils, "urlopen", _raise)
    monkeypatch.setattr(utils, "flaresolve", lambda *a, **k: "solved")
    utils.addon._settings = {**utils.addon._settings, "fs_enable": "true"}

    assert utils._getHtml("https://example.com") == "solved"


def test_flaresolve_logs_stateless_request_path(monkeypatch):
    logs = []

    class _FakeResponse:
        text = "<html>solved</html>"
        status_code = 200
        url = "https://example.com"
        headers = {}
        raw_json = None

    class _FakeManager:
        def __init__(self, host):
            self.host = host

        def request(self, url):
            return _FakeResponse()

        def close(self, destroy_session=False):
            pass

    monkeypatch.setattr(flaresolverr, "FlareSolverrManager", _FakeManager)
    monkeypatch.setattr(utils, "kodilog", logs.append)
    monkeypatch.setattr(utils.time, "time", lambda: 1.0)
    utils.addon._settings = {**utils.addon._settings, "fs_host": ""}

    assert utils.flaresolve("https://example.com", None) == "<html>solved</html>"
    assert any("stateless" in message for message in logs)
    assert not any("session" in message.lower() for message in logs)


def test_gethtml_unwraps_cached_list(monkeypatch):
    monkeypatch.setattr(utils.cache, "cacheFunction", lambda *a, **k: ["<html>cached_list</html>"])
    result = utils.getHtml("https://example.com")
    assert result == "<html>cached_list</html>"


def test_gethtml_handles_cached_empty_list(monkeypatch):
    monkeypatch.setattr(utils.cache, "cacheFunction", lambda *a, **k: [])
    result = utils.getHtml("https://example.com")
    assert result == ""


def test_parse_html_handles_sequence_types():
    soup = utils.parse_html(["<div>hello</div>"])
    assert soup.find("div").text == "hello"

    soup_empty = utils.parse_html([])
    assert soup_empty is not None
