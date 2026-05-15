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
