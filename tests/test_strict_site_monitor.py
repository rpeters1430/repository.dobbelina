from scripts.site_health_types import HealthState
from scripts.strict_site_monitor import evaluate_record


def sample_profile():
    return {
        "strict_contract": {
            "min_video_items": 5,
            "min_unique_title_ratio": 0.8,
            "min_unique_url_ratio": 0.8,
            "max_count_drop_ratio": 0.7,
            "sample_count": 1,
            "allowed_hosts": ["example.test"],
            "required_stages": ["listing", "playback", "media"],
            "advisory_fields": ["thumbnail", "description"],
        }
    }


def sample_video(i):
    return {
        "name": f"Video {i}",
        "url": f"https://example.test/watch/{i}",
        "mode": "play",
        "icon": "https://example.test/icon.jpg",
        "desc": "Desc",
    }


def test_evaluate_record_healthy():
    record = {
        "site": "pornhub",
        "status": "PASS",
        "listing_samples": [sample_video(i) for i in range(1, 6)],
        "steps": {
            "main": {"status": "PASS"},
            "list": {"status": "PASS"},
            "play": {"status": "PASS", "play_url": "https://example.test/video.mp4"},
        },
        "media_result": {
            "passed": True,
            "classification": "NONE",
            "message": "Direct media verified",
        },
    }

    report = evaluate_record(record, sample_profile())
    assert report["state"] == HealthState.HEALTHY
    assert report["exit_code"] == 0


def test_evaluate_record_failing_stage_broken():
    record = {
        "site": "pornhub",
        "status": "FAIL",
        "listing_samples": [sample_video(i) for i in range(1, 6)],
        "steps": {
            "main": {"status": "PASS"},
            "list": {"status": "FAIL", "message": "Parsing error"},
            "play": {"status": "SKIP"},
        },
    }

    report = evaluate_record(record, sample_profile())
    assert report["state"] == HealthState.BROKEN
    assert report["exit_code"] == 1


def test_evaluate_record_challenge_blocked():
    record = {
        "site": "pornhub",
        "status": "FAIL",
        "listing_samples": [
            {
                "name": "Just a moment...",
                "url": "https://example.test/cf",
                "mode": "play",
            }
        ]
        + [sample_video(i) for i in range(2, 6)],
        "steps": {
            "main": {"status": "FAIL", "message": "Cloudflare challenge"},
            "list": {"status": "SKIP"},
            "play": {"status": "SKIP"},
        },
    }

    report = evaluate_record(record, sample_profile())
    assert report["state"] == HealthState.BLOCKED
    assert report["exit_code"] == 1


def test_evaluate_record_infrastructure_harness_error():
    record = {
        "site": "pornhub",
        "status": "ERROR",
        "error": "Timeout or Python crash",
        "steps": {},
    }

    report = evaluate_record(record, sample_profile())
    assert report["state"] == HealthState.HARNESS_ERROR
    assert report["exit_code"] == 2


def test_evaluate_record_no_result_not_tested():
    report = evaluate_record({}, sample_profile())
    assert report["state"] == HealthState.NOT_TESTED
    assert report["exit_code"] == 2
