import pytest
from scripts.site_health_types import (
    HealthState,
    ValidationResult,
    redact_url,
    failure_signature,
)


def test_health_state_enum_values():
    assert HealthState.HEALTHY == "HEALTHY"
    assert HealthState.BROKEN == "BROKEN"
    assert HealthState.BLOCKED == "BLOCKED"
    assert HealthState.HARNESS_ERROR == "HARNESS_ERROR"
    assert HealthState.NOT_TESTED == "NOT_TESTED"


def test_validation_result_defaults():
    res = ValidationResult(passed=True, classification="NONE", message="OK")
    assert res.passed is True
    assert res.classification == "NONE"
    assert res.message == "OK"
    assert res.metrics == {}
    assert res.evidence == {}


def test_redact_url_removes_sensitive_values():
    value = redact_url("https://cdn.test/a.m3u8?token=secret&quality=720&auth=abc&sig=123")
    assert "token=REDACTED" in value
    assert "auth=REDACTED" in value
    assert "sig=REDACTED" in value
    assert "quality=720" in value


def test_failure_signature_ignores_volatile_urls():
    left = {"state": "BROKEN", "failed_stage": "media", "classification": "PLAYBACK", "message": "Failed to fetch media"}
    right = {**left, "sample_url": "https://cdn.test/expiring?token=x"}
    assert failure_signature(left) == failure_signature(right)
