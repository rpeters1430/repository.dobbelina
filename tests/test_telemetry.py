import pytest
from resources.lib import telemetry

MOCK_DSN = "https://37da8a0bff7e4f50a42174c51c2d9697@glitchtip.tailb94d9.ts.net/1"

def test_disabled_reporter_does_not_queue(tmp_path):
    reporter = telemetry.TelemetryReporter(
        addon_dir=str(tmp_path),
        profile_dir=str(tmp_path),
        enabled_override=False
    )
    with pytest.raises(RuntimeError):
        with reporter.operation_scope("xvideos.List", {}):
            raise RuntimeError("test error")
    assert len(reporter.store.peek(10)) == 0

def test_enabled_reporter_queues_and_reraises(tmp_path, monkeypatch):
    reporter = telemetry.TelemetryReporter(
        addon_dir=str(tmp_path),
        profile_dir=str(tmp_path),
        enabled_override=True
    )
    # Prevent automatic background drain so we can verify the enqueued item
    monkeypatch.setattr(reporter, "drain_once", lambda limit=5: None)

    with pytest.raises(RuntimeError):
        with reporter.operation_scope("xvideos.List", {}):
            raise RuntimeError("test error")

    peeked = reporter.store.peek(10)
    assert len(peeked) == 1
    assert peeked[0]["event"]["tags"]["event_type"] == "addon_exception"

def test_send_test_report(tmp_path):
    reporter = telemetry.TelemetryReporter(
        addon_dir=str(tmp_path),
        profile_dir=str(tmp_path),
        enabled_override=True
    )
    reporter.config = {"dsn": MOCK_DSN, "environment": "test"}
    res = reporter.send_test_report()
    assert res.ok is True


def test_note_listing_item(tmp_path):
    reporter = telemetry.TelemetryReporter(
        addon_dir=str(tmp_path),
        profile_dir=str(tmp_path),
        enabled_override=True
    )
    with reporter.operation_scope("xvideos.List", {}):
        reporter.note_listing_item()
        assert reporter.current_context["items"] == 1


def test_finish_operation_handles_empty_listings(tmp_path, monkeypatch):
    reporter = telemetry.TelemetryReporter(
        addon_dir=str(tmp_path),
        profile_dir=str(tmp_path),
        enabled_override=True
    )
    monkeypatch.setattr(reporter, "drain_once", lambda limit=5: None)

    with reporter.operation_scope("xvideos.List", {}):
        pass

    peeked = reporter.store.peek(10)
    assert len(peeked) == 1
    assert peeked[0]["event"]["tags"]["event_type"] == "site_load_failure"
    assert peeked[0]["event"]["tags"]["classification"] == "empty_listing"


def test_http_outcome(tmp_path, monkeypatch):
    reporter = telemetry.TelemetryReporter(
        addon_dir=str(tmp_path),
        profile_dir=str(tmp_path),
        enabled_override=True
    )
    monkeypatch.setattr(reporter, "drain_once", lambda limit=5: None)

    reporter.http_outcome("https://example.com/api", "timeout", status=504, elapsed_ms=1200)
    peeked = reporter.store.peek(10)
    assert len(peeked) == 1
    event = peeked[0]["event"]
    assert event["tags"]["event_type"] == "site_load_failure"
    assert event["tags"]["classification"] == "timeout"
    assert event["contexts"]["http"]["status_code"] == 504
    assert event["contexts"]["http"]["elapsed_ms"] == 1200


def test_resolve_failure(tmp_path, monkeypatch):
    reporter = telemetry.TelemetryReporter(
        addon_dir=str(tmp_path),
        profile_dir=str(tmp_path),
        enabled_override=True
    )
    monkeypatch.setattr(reporter, "drain_once", lambda limit=5: None)

    reporter.resolve_failure("resolveurl", "no_sources", "No compatible stream found")
    peeked = reporter.store.peek(10)
    assert len(peeked) == 1
    event = peeked[0]["event"]
    assert event["tags"]["event_type"] == "resolve_failure"
    assert event["tags"]["resolver"] == "resolveurl"
    assert event["contexts"]["resolver"]["error_message"] == "No compatible stream found"


def test_playback_lifecycle(tmp_path, monkeypatch):
    reporter = telemetry.TelemetryReporter(
        addon_dir=str(tmp_path),
        profile_dir=str(tmp_path),
        enabled_override=True
    )
    monkeypatch.setattr(reporter, "drain_once", lambda limit=5: None)

    # 1. Start playback attempt
    reporter.start_playback_attempt("https://example.com/stream.m3u8", inputstream_addon="inputstream.adaptive")

    attempt = reporter.load_playback_attempt()
    assert attempt is not None
    assert attempt["protocol"] == "hls"
    assert attempt["domain"] == "example.com"
    assert attempt["inputstream"] == "inputstream.adaptive"

    # 2. Report playback failure
    reporter.playback_outcome({
        "outcome": "playback_failure",
        "elapsed_ms": 5000,
        "attempt": attempt
    })

    peeked = reporter.store.peek(10)
    assert len(peeked) == 1
    event = peeked[0]["event"]
    assert event["tags"]["event_type"] == "playback_failure"
    assert event["contexts"]["playback"]["elapsed_ms"] == 5000
    assert event["contexts"]["playback"]["protocol"] == "hls"

    # 3. Clear attempt
    reporter.clear_playback_attempt()
    assert reporter.load_playback_attempt() is None
