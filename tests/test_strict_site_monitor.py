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


def test_child_import_error_is_site_code_failure():
    record = {
        "site": "pornhub",
        "overall": "ERROR",
        "error_type": "import",
        "error": "ModuleNotFoundError: optional dependency",
        "steps": {},
    }

    report = evaluate_record(record, sample_profile())
    assert report["state"] == HealthState.BROKEN
    assert report["classification"] == "CODE"
    assert report["failed_stage"] == "import"
    assert report["exit_code"] == 1


def test_child_missing_site_export_is_site_code_failure():
    record = {
        "site": "pornhub",
        "overall": "SKIP",
        "error_type": "missing_site",
        "error": "No AdultSite/default_mode exported",
        "steps": {},
    }

    report = evaluate_record(record, sample_profile())
    assert report["state"] == HealthState.BROKEN
    assert report["classification"] == "CODE"
    assert report["exit_code"] == 1


def test_required_media_stage_fails_when_not_performed():
    record = {
        "site": "pornhub",
        "overall": "PASS",
        "listing_samples": [sample_video(i) for i in range(1, 6)],
        "steps": {
            "main": {"status": "PASS"},
            "list": {"status": "PASS"},
            "play": {"status": "PASS"},
        },
    }

    report = evaluate_record(record, sample_profile())
    assert report["state"] == HealthState.BROKEN
    assert report["failed_stage"] == "media"
    assert report["classification"] == "MEDIA_VALIDATION_MISSING"
    assert report["exit_code"] == 1


def test_cloudflare_block_through_flaresolverr_is_blocked_not_untested():
    record = {
        "site": "missav",
        "overall": "SKIP",
        "steps": {
            "main": {
                "status": "SKIP",
                "message": "FlareSolverr required but unavailable in harness: "
                "RuntimeError: FlareSolverr error for https://example.test/: "
                "datacenter-ip-blocked",
            },
            "list": {"status": "SKIP", "message": "FlareSolverr failed in a previous step"},
            "play": {"status": "SKIP", "message": "FlareSolverr failed in a previous step"},
        },
    }

    report = evaluate_record(record, sample_profile())
    assert report["state"] == HealthState.BLOCKED
    assert report["classification"] == "CHALLENGE"
    assert report["failed_stage"] == "listing"
    assert report["exit_code"] == 1
    assert "datacenter-ip-blocked" in report["message"]
    assert report["failure_signature"]


def test_flaresolverr_block_at_search_reports_search_stage():
    record = {
        "site": "spankbang",
        "overall": "SKIP",
        "steps": {
            "main": {"status": "SKIP", "message": "Main disabled by site profile"},
            "search": {
                "status": "SKIP",
                "message": "FlareSolverr required but unavailable in harness: timed out",
            },
        },
    }

    report = evaluate_record(record, sample_profile())
    assert report["state"] == HealthState.BLOCKED
    assert report["failed_stage"] == "search"


def test_global_flaresolverr_outage_stays_not_tested():
    record = {
        "site": "missav",
        "overall": "SKIP",
        "steps": {
            "main": {"status": "SKIP", "message": "FlareSolverr unavailable in harness (global)"},
        },
    }

    report = evaluate_record(record, sample_profile())
    assert report["state"] == HealthState.NOT_TESTED
    assert report["exit_code"] == 2


def test_html_payload_without_challenge_is_broken():
    record = {
        "site": "youporn",
        "overall": "PASS",
        "listing_samples": [sample_video(i) for i in range(1, 6)],
        "steps": {
            "main": {"status": "PASS"},
            "list": {"status": "PASS"},
            "play": {"status": "PASS", "play_url": "https://www.youporn.com/watch/123/"},
        },
        "media_result": {
            "passed": False,
            "classification": "HTML_PAYLOAD",
            "message": "Server returned HTML page instead of media content",
        },
    }

    report = evaluate_record(record, sample_profile())
    assert report["state"] == HealthState.BROKEN
    assert report["failed_stage"] == "media"
    assert report["classification"] == "HTML_PAYLOAD"


def test_html_payload_with_challenge_notification_is_blocked():
    record = {
        "site": "youporn",
        "overall": "PASS",
        "notifications": ["Cloudflare challenge encountered"],
        "listing_samples": [sample_video(i) for i in range(1, 6)],
        "steps": {
            "main": {"status": "PASS"},
            "list": {"status": "PASS"},
            "play": {"status": "PASS", "play_url": "https://www.youporn.com/watch/123/"},
        },
        "media_result": {
            "passed": False,
            "classification": "HTML_PAYLOAD",
            "message": "Server returned HTML page instead of media content",
        },
    }

    report = evaluate_record(record, sample_profile())
    assert report["state"] == HealthState.BLOCKED
    assert report["failed_stage"] == "media"
