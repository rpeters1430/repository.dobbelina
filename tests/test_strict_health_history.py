import json
from scripts.site_health_types import HealthState
from scripts.strict_health_history import merge_reports


def create_report(site, state, sig="", item_count=10):
    return {
        "site": site,
        "state": state,
        "exit_code": 0 if state == HealthState.HEALTHY else 1,
        "failed_stage": None if state == HealthState.HEALTHY else "listing",
        "classification": "NONE" if state == HealthState.HEALTHY else "PARSER",
        "message": "OK" if state == HealthState.HEALTHY else "Failed",
        "failure_signature": sig,
        "listing_metrics": {"item_count": item_count, "unique_title_ratio": 1.0},
        "media_metrics": {"media_kind": "direct", "segment_bytes": 1024},
    }


def test_merge_reports_combines_isolated_reports(tmp_path):
    r1 = tmp_path / "strict_site_pornhub.json"
    r2 = tmp_path / "strict_site_xvideos.json"

    r1.write_text(json.dumps(create_report("pornhub", HealthState.HEALTHY)), encoding="utf-8")
    r2.write_text(json.dumps(create_report("xvideos", HealthState.BROKEN, sig="sig123")), encoding="utf-8")

    latest, history = merge_reports([r1, r2], previous=None)

    assert latest["summary"]["HEALTHY"] == 1
    assert latest["summary"]["BROKEN"] == 1
    assert "pornhub" in latest["sites"]
    assert "xvideos" in latest["sites"]


def test_missing_priority_sites_default_to_not_tested(tmp_path):
    r1 = tmp_path / "strict_site_pornhub.json"
    r1.write_text(json.dumps(create_report("pornhub", HealthState.HEALTHY)), encoding="utf-8")

    latest, history = merge_reports([r1], previous=None)

    # Priority site like xnxx missing from inputs -> NOT_TESTED
    assert "xnxx" in latest["sites"]
    assert latest["sites"]["xnxx"]["state"] == HealthState.NOT_TESTED


def test_healthy_run_updates_baseline_and_consecutive_count(tmp_path):
    r1 = tmp_path / "strict_site_pornhub.json"
    r1.write_text(json.dumps(create_report("pornhub", HealthState.HEALTHY, item_count=15)), encoding="utf-8")

    latest, history = merge_reports([r1], previous=None)
    site_hist = history["sites"]["pornhub"]

    assert site_hist["consecutive_healthy"] == 1
    assert site_hist["healthy_baseline"]["item_count"] == 15


def test_failure_resets_consecutive_healthy_and_sets_open_signature(tmp_path):
    # Previous history: 2 consecutive healthy
    prev = {
        "sites": {
            "pornhub": {
                "consecutive_healthy": 2,
                "healthy_baseline": {"item_count": 10},
                "open_failure_signature": "",
                "runs": [],
            }
        }
    }

    r1 = tmp_path / "strict_site_pornhub.json"
    r1.write_text(json.dumps(create_report("pornhub", HealthState.BROKEN, sig="sig456")), encoding="utf-8")

    latest, history = merge_reports([r1], previous=prev)
    site_hist = history["sites"]["pornhub"]

    assert site_hist["consecutive_healthy"] == 0
    assert site_hist["open_failure_signature"] == "sig456"
    assert site_hist["healthy_baseline"]["item_count"] == 10  # Baseline preserved


def test_two_consecutive_healthy_passes_tracks_recovery(tmp_path):
    # Start broken
    r_broken = tmp_path / "strict_site_pornhub.json"
    r_broken.write_text(json.dumps(create_report("pornhub", HealthState.BROKEN, sig="sig111")), encoding="utf-8")
    _, history1 = merge_reports([r_broken], previous=None)

    # Pass 1 recovery
    r_pass1 = tmp_path / "strict_site_pornhub.json"
    r_pass1.write_text(json.dumps(create_report("pornhub", HealthState.HEALTHY)), encoding="utf-8")
    _, history2 = merge_reports([r_pass1], previous=history1)
    assert history2["sites"]["pornhub"]["consecutive_healthy"] == 1

    # Pass 2 recovery
    r_pass2 = tmp_path / "strict_site_pornhub.json"
    r_pass2.write_text(json.dumps(create_report("pornhub", HealthState.HEALTHY)), encoding="utf-8")
    _, history3 = merge_reports([r_pass2], previous=history2)
    assert history3["sites"]["pornhub"]["consecutive_healthy"] == 2


def test_history_bounded_to_14_runs(tmp_path):
    history = None
    for i in range(16):
        r = tmp_path / "strict_site_pornhub.json"
        r.write_text(json.dumps(create_report("pornhub", HealthState.HEALTHY, item_count=i)), encoding="utf-8")
        _, history = merge_reports([r], previous=history)

    runs = history["sites"]["pornhub"]["runs"]
    assert len(runs) == 14
