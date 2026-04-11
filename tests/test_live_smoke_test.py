from scripts import live_smoke_test


def test_classify_message_detects_age_verification_blocks():
    assert (
        live_smoke_test.classify_message(
            "Due to legal requirements in your country you must verify your age"
        )
        == "BLOCKED"
    )
    assert (
        live_smoke_test.classify_message(
            "Texas law requiring porn sites verify user ages"
        )
        == "BLOCKED"
    )
