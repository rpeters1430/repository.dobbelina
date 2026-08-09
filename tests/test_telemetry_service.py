import pytest
from resources.lib import playback_monitor as pbm

def test_playback_service_instantiation():
    sm = pbm.PlaybackStateMachine(attempt={"attempt_id": "test"}, created_at=100.0)
    assert sm.state == "pending"
