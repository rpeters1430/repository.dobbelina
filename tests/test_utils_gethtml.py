"""Tests for _getHtml handling in utils."""

import gzip
import io


from resources.lib import utils


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
