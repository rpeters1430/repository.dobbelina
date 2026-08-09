import time
import pytest
from resources.lib.telemetry_store import TelemetryStore

class Clock:
    def __init__(self, start=1_700_000_000):
        self.value = start

    def __call__(self):
        return self.value

def test_installation_id_persistence(tmp_path):
    store1 = TelemetryStore(str(tmp_path))
    id1 = store1.installation_id()
    assert len(id1) == 32
    store2 = TelemetryStore(str(tmp_path))
    assert store2.installation_id() == id1

def test_cooldown_reports_suppressed_count(tmp_path):
    clock = Clock(1_700_000_000)
    store = TelemetryStore(str(tmp_path), now=clock)
    assert store.allow("same", "addon_exception") == (True, 0)
    assert store.allow("same", "addon_exception") == (False, 1)
    clock.value += 301
    assert store.allow("same", "addon_exception") == (True, 1)

def test_sample_success_is_deterministic(tmp_path):
    store = TelemetryStore(str(tmp_path))
    res1 = store.sample_success("attempt-123")
    res2 = store.sample_success("attempt-123")
    assert res1 == res2

def test_clear_removes_all_state(tmp_path):
    store = TelemetryStore(str(tmp_path), random_bytes=lambda n: b"a" * n)
    store.installation_id()
    store.enqueue({"event_id": "1", "event_type": "addon_exception", "timestamp_epoch": time.time()})
    store.clear()
    assert not (tmp_path / "telemetry").exists()
