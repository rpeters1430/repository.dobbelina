from resources.lib import telemetry_privacy as privacy

def test_url_keeps_only_origin():
    assert privacy.sanitize_url("https://u:p@example.com/private?q=x#y") == {
        "scheme": "https", "domain": "example.com"
    }

def test_event_removes_secrets_unknowns_and_paths(tmp_path):
    event = {
        "event_id": "a" * 32,
        "timestamp": "2026-08-08T12:00:00Z",
        "level": "error",
        "message": "https://host/private?token=abc",
        "tags": {"site": "xvideos", "password": "bad", "unknown": "drop"},
        "contexts": {"http": {"domain": "host", "cookie": "sid=1"}},
        "extra": {"search": "private words"}
    }
    text = repr(privacy.sanitize_event(event, str(tmp_path))).lower()
    for forbidden in ("/private", "abc", "password", "cookie", "private words", "unknown"):
        assert forbidden not in text

def test_exception_has_no_locals_or_raw_url(tmp_path):
    try:
        # This value is intentionally present in locals to verify it is redacted.
        _secret = "must-not-leak"
        raise RuntimeError("https://host/path?token=abc")
    except RuntimeError as exc:
        result = privacy.safe_exception(exc, str(tmp_path))
    assert result["values"][0]["type"] == "RuntimeError"
    assert "must-not-leak" not in repr(result)
    st = result["values"][0]["stacktrace"]
    assert all("locals" not in frame for frame in st["frames"])
    assert any(frame.get("in_app") for frame in st["frames"])
