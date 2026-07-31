import pytest
from scripts.merge_kodi_results import merge_kodi_result
from scripts.site_health_types import HealthState


def healthy_strict_report(site="pornhub"):
    return {
        "site": site,
        "state": HealthState.HEALTHY,
        "exit_code": 0,
        "failed_stage": None,
        "classification": "NONE",
        "message": "All strict checks passed",
        "failure_signature": "",
        "listing_metrics": {"item_count": 10},
        "media_metrics": {"media_kind": "direct"},
    }


def test_matching_kodi_result_preserves_healthy():
    kodi_result = {"site": "pornhub", "passed": True, "playback_started": True, "message": "OK"}
    merged = merge_kodi_result(healthy_strict_report(), kodi_result)
    assert merged["state"] == HealthState.HEALTHY
    assert merged["exit_code"] == 0


def test_kodi_mismatch_overrides_healthy():
    kodi_result = {"site": "pornhub", "passed": False, "playback_started": False, "message": "Playback failed in Kodi"}
    merged = merge_kodi_result(healthy_strict_report(), kodi_result)
    assert merged["state"] == HealthState.BROKEN
    assert merged["failed_stage"] == "kodi_runtime"
    assert merged["classification"] == "KODI_RUNTIME_MISMATCH"
    assert merged["exit_code"] == 1


def test_kodi_infrastructure_failure_becomes_harness_error():
    kodi_result = {"site": "pornhub", "passed": False, "error": "Kodi process crashed", "infrastructure_error": True}
    merged = merge_kodi_result(healthy_strict_report(), kodi_result)
    assert merged["state"] == HealthState.HARNESS_ERROR
    assert merged["exit_code"] == 2


def test_broken_strict_report_retains_broken_state():
    broken_report = {
        "site": "pornhub",
        "state": HealthState.BROKEN,
        "exit_code": 1,
        "failed_stage": "listing",
        "classification": "PARSER",
    }
    kodi_result = {"site": "pornhub", "passed": True, "playback_started": True}
    merged = merge_kodi_result(broken_report, kodi_result)
    assert merged["state"] == HealthState.BROKEN
