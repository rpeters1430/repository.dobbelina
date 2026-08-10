import pytest
import time
from resources.lib import playback_monitor as pbm
import service
from resources.lib import telemetry


def test_playback_service_instantiation():
    sm = pbm.PlaybackStateMachine(attempt={"attempt_id": "test"}, created_at=100.0)
    assert sm.state == "pending"


def test_telemetry_controller_tick(tmp_path, monkeypatch):
    reporter = telemetry.TelemetryReporter(
        addon_dir=str(tmp_path),
        profile_dir=str(tmp_path),
        enabled_override=True
    )
    monkeypatch.setattr(reporter, "drain_once", lambda limit=5: None)

    controller = service.TelemetryController(reporter)

    # Tick with no active attempt
    controller.tick()
    assert controller.sm is None

    # Save active attempt
    reporter.start_playback_attempt("https://example.com/stream.mp4")
    attempt = reporter.load_playback_attempt()
    assert attempt is not None

    # First tick initializes StateMachine
    controller.tick()
    assert controller.sm is not None
    assert controller.active_id == attempt["attempt_id"]

    # Trigger player callback
    controller.on_av_started()
    assert controller.sm.state == "started"

    # Stopped callback generates probable failure and cleans up
    controller.on_playback_stopped()
    assert controller.sm is None

    peeked = reporter.store.peek(10)
    assert len(peeked) == 1
    assert peeked[0]["event"]["tags"]["event_type"] == "probable_failure"
