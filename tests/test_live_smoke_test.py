from scripts import live_smoke_test


class _FakeResponse:
    def __init__(self, status=200, body=b"{}"):
        self.status = status
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._body


def test_classify_message_detects_age_verification_blocks():
    assert (
        live_smoke_test.classify_message(
            "Due to legal requirements in your country you must verify your age"
        )
        == "BLOCKED"
    )
    assert (
        live_smoke_test.classify_message(
            "Texas law requiring porn sites verify user ages"
        )
        == "BLOCKED"
    )


def test_flaresolverr_url_can_be_configured_with_env(monkeypatch):
    monkeypatch.setenv("FLARESOLVERR_URL", "http://127.0.0.1:8191/v1")

    assert live_smoke_test._get_flaresolverr_url() == "http://127.0.0.1:8191/v1"


def test_probe_flaresolverr_accepts_v1_api_when_health_is_missing(monkeypatch):
    def fake_urlopen(req, timeout=None):
        url = req.full_url
        if url.endswith("/health"):
            raise live_smoke_test.urllib.error.HTTPError(
                url, 404, "Not Found", hdrs=None, fp=None
            )
        assert url == "http://localhost:8191/v1"
        return _FakeResponse(body=b'{"sessions":[]}')

    monkeypatch.setattr(live_smoke_test.urllib.request, "urlopen", fake_urlopen)

    assert live_smoke_test._probe_flaresolverr() is True
