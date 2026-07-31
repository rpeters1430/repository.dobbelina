import pytest
from scripts.generate_strict_triage_requests import generate_strict_triage_requests
from scripts.site_health_types import HealthState


def sample_latest_and_history(site="pornhub", state=HealthState.BROKEN, sig="sig123", consec=0):
    latest = {
        "summary": {state: 1},
        "sites": {
            site: {
                "site": site,
                "state": state,
                "exit_code": 1,
                "failed_stage": "listing",
                "classification": "PARSER",
                "message": "Parser failed to find videos",
                "failure_signature": sig,
                "evidence": {"sample_url": "https://pornhub.com"},
            }
        },
    }
    history = {
        "sites": {
            site: {
                "consecutive_healthy": consec,
                "healthy_baseline": {"item_count": 10},
                "open_failure_signature": sig,
                "runs": [],
            }
        }
    }
    return latest, history


def test_first_broken_creates_or_reopens_issue():
    latest, history = sample_latest_and_history(state=HealthState.BROKEN, sig="sig100")
    requests = generate_strict_triage_requests(latest, history, existing_issues=[])

    assert len(requests) == 1
    req = requests[0]
    assert req["action"] == "CREATE_OR_REOPEN"
    assert req["site"] == "pornhub"
    assert "[Site Monitor] pornhub is broken" in req["title"]
    assert "<!-- strict-site-health:pornhub -->" in req["body"]
    assert "site-monitor" in req["labels"]


def test_first_blocked_creates_blocked_issue():
    latest, history = sample_latest_and_history(state=HealthState.BLOCKED, sig="sig200")
    requests = generate_strict_triage_requests(latest, history, existing_issues=[])

    assert len(requests) == 1
    req = requests[0]
    assert req["action"] == "CREATE_OR_REOPEN"
    assert req["site"] == "pornhub"
    assert "[Site Monitor] pornhub is blocked" in req["title"]
    assert "failure/blocked" in req["labels"]


def test_unchanged_signature_produces_none_action():
    latest, history = sample_latest_and_history(state=HealthState.BROKEN, sig="sig100")
    existing = [
        {
            "number": "42",
            "title": "[Site Monitor] pornhub is broken",
            "body": "<!-- strict-site-health:pornhub -->\nSig: sig100",
            "state": "OPEN",
            "signature": "sig100",
        }
    ]
    requests = generate_strict_triage_requests(latest, history, existing_issues=existing)

    assert len(requests) == 1
    assert requests[0]["action"] == "NONE"


def test_changed_signature_produces_update_action():
    latest, history = sample_latest_and_history(state=HealthState.BROKEN, sig="sig999")
    existing = [
        {
            "number": "42",
            "title": "[Site Monitor] pornhub is broken",
            "body": "<!-- strict-site-health:pornhub -->\nSig: sig100",
            "state": "OPEN",
            "signature": "sig100",
        }
    ]
    requests = generate_strict_triage_requests(latest, history, existing_issues=existing)

    assert len(requests) == 1
    req = requests[0]
    assert req["action"] == "UPDATE"
    assert req["issue_number"] == "42"


def test_harness_error_routes_to_infrastructure_title():
    latest, history = sample_latest_and_history(state=HealthState.HARNESS_ERROR, sig="sig_harness")
    requests = generate_strict_triage_requests(latest, history, existing_issues=[])

    assert len(requests) == 1
    req = requests[0]
    assert req["action"] == "CREATE_OR_REOPEN"
    assert "[Site Monitor] Monitoring infrastructure failure" in req["title"]
    assert "failure/harness" in req["labels"]


def test_one_recovery_pass_produces_none_action():
    latest, history = sample_latest_and_history(state=HealthState.HEALTHY, consec=1)
    existing = [
        {
            "number": "42",
            "title": "[Site Monitor] pornhub is broken",
            "body": "<!-- strict-site-health:pornhub -->",
            "state": "OPEN",
        }
    ]
    requests = generate_strict_triage_requests(latest, history, existing_issues=existing)

    assert len(requests) == 1
    assert requests[0]["action"] == "NONE"


def test_two_recovery_passes_produces_close_action():
    latest, history = sample_latest_and_history(state=HealthState.HEALTHY, consec=2)
    existing = [
        {
            "number": "42",
            "title": "[Site Monitor] pornhub is broken",
            "body": "<!-- strict-site-health:pornhub -->",
            "state": "OPEN",
        }
    ]
    requests = generate_strict_triage_requests(latest, history, existing_issues=existing)

    assert len(requests) == 1
    req = requests[0]
    assert req["action"] == "CLOSE"
    assert req["issue_number"] == "42"
    assert "2 consecutive healthy passes" in req["comment"]
