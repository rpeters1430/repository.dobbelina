from scripts import generate_triage_requests


def test_build_requests_skips_environment_failures():
    diff = {
        "new_failures": [
            {
                "site": "example",
                "previous": "PASS",
                "current": "FAIL",
                "class": "ENV",
                "message": "FlareSolverr unavailable",
            }
        ],
        "step_regressions": [],
        "persistent_failures": [],
    }

    assert generate_triage_requests.build_requests(diff) == []


def test_build_requests_skips_legacy_flaresolverr_message_class():
    diff = {
        "new_failures": [
            {
                "site": "example",
                "previous": "PASS",
                "current": "FAIL",
                "class": "PLAYBACK",
                "message": (
                    "RuntimeError: FlareSolverr error for https://example.test: "
                    "Check if FlareSolverr is running at http://localhost:8191/v1"
                ),
            }
        ],
        "step_regressions": [],
        "persistent_failures": [],
    }

    assert generate_triage_requests.build_requests(diff) == []


def test_build_requests_keeps_parser_failures():
    diff = {
        "new_failures": [
            {
                "site": "example",
                "previous": "PASS",
                "current": "FAIL",
                "class": "PARSER",
                "message": "List returned no videos",
            }
        ],
        "step_regressions": [],
        "persistent_failures": [],
    }

    requests = generate_triage_requests.build_requests(diff)

    assert len(requests) == 1
    assert requests[0]["type"] == "REGRESSION"
    assert requests[0]["labels"] == [
        "status/needs-triage",
        "bug",
        "site-health",
        "site-health/regression",
        "site-health/new-failure",
        "failure/parser",
    ]
    assert "Automated site-health triage notes" in requests[0]["comment"]
    assert "Classification: `REGRESSION` / `PARSER`" in requests[0]["comment"]
    assert "--site example" in requests[0]["comment"]
    assert "listing selectors" in requests[0]["comment"]


def test_build_requests_labels_step_regressions():
    diff = {
        "new_failures": [],
        "step_regressions": [
            {
                "site": "example",
                "step": "search",
                "previous": "PASS",
                "current": "FAIL",
                "class": "NETWORK",
                "message": "HTTP 503",
            }
        ],
        "persistent_failures": [],
    }

    requests = generate_triage_requests.build_requests(diff)

    assert requests[0]["type"] == "STEP_REGRESSION"
    assert requests[0]["labels"] == [
        "status/needs-triage",
        "bug",
        "site-health",
        "site-health/step-regression",
        "failure/network",
    ]
    assert "Failing step: `search`" in requests[0]["comment"]
    assert "temporary block" in requests[0]["comment"]


def test_build_requests_labels_persistent_failures():
    diff = {
        "new_failures": [],
        "step_regressions": [],
        "persistent_failures": [
            {
                "site": "example",
                "previous": "FAIL",
                "current": "FAIL",
                "class": "PLAYBACK",
                "message": "No playable URL",
            }
        ],
    }

    requests = generate_triage_requests.build_requests(diff)

    assert requests[0]["type"] == "PERSISTENT_FAILURE"
    assert requests[0]["labels"] == [
        "status/needs-triage",
        "bug",
        "site-health",
        "site-health/persistent-failure",
        "failure/playback",
    ]
    assert "hoster, player config, or source JSON changed" in requests[0]["comment"]


def test_build_requests_skips_flaky_persistent_failures():
    diff = {
        "new_failures": [],
        "step_regressions": [],
        "persistent_failures": [
            {
                "site": "example",
                "previous": "FAIL",
                "current": "FAIL",
                "class": "PARSER",
                "message": "List returned no videos",
                "is_flaky": True,
                "stability_score": 0.33,
            }
        ],
    }

    assert generate_triage_requests.build_requests(diff) == []
