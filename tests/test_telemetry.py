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
