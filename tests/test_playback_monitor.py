from resources.lib import playback_monitor as pbm

def test_startup_timeout():
    sm = pbm.PlaybackStateMachine(attempt={"attempt_id": "1"}, created_at=100.0)
    res = sm.tick(129.9)
    assert res is None
    res = sm.tick(130.0)
    assert res is not None
    assert res["outcome"] == "playback_failure"

def test_stable_success():
    sm = pbm.PlaybackStateMachine(attempt={"attempt_id": "1"}, created_at=100.0)
    sm.av_started(now_ts=105.0)
    res = sm.tick(134.9)
    assert res is None
    res = sm.tick(135.0)
    assert res is not None
    assert res["outcome"] == "playback_success"

def test_early_stop_is_probable_failure():
    sm = pbm.PlaybackStateMachine(attempt={"attempt_id": "1"}, created_at=100.0)
    sm.av_started(now_ts=105.0)
    res = sm.stopped(now_ts=110.0) # elapsed 5s < 15s window
    assert res is not None
    assert res["outcome"] == "probable_failure"
