import json
from resources.lib import telemetry_transport as transport

DSN = "https://public_key@example.com/42"

def test_parse_dsn():
    parts = transport.parse_dsn(DSN)
    assert parts.endpoint == "https://example.com/api/42/envelope/"
    assert parts.public_key == "public_key"
    assert parts.project_id == "42"

def test_envelope_shape():
    event = {"event_id": "a" * 32, "timestamp": "2026-08-08T12:00:00Z", "message": "test"}
    envelope_bytes = transport.build_envelope(event, DSN)
    lines = envelope_bytes.decode("utf-8").splitlines()
    assert json.loads(lines[0])["dsn"] == DSN
    assert json.loads(lines[1])["type"] == "event"
    assert json.loads(lines[2])["message"] == "test"

def test_unconfigured_dsn():
    res = transport.send_event({"event_id": "1"}, "")
    assert res.ok is False
    assert res.retryable is False
    assert "not configured" in res.message.lower()
