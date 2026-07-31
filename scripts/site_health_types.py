import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


class HealthState(str, Enum):
    HEALTHY = "HEALTHY"
    BROKEN = "BROKEN"
    BLOCKED = "BLOCKED"
    HARNESS_ERROR = "HARNESS_ERROR"
    NOT_TESTED = "NOT_TESTED"


@dataclass
class ValidationResult:
    passed: bool
    classification: str
    message: str
    metrics: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)


SENSITIVE_PARAM_KEYS = {
    "token",
    "auth",
    "authorization",
    "cookie",
    "key",
    "signature",
    "sig",
    "expires",
    "hdntl",
}


def redact_url(url: str) -> str:
    """Redact sensitive query parameter values from a URL."""
    if not url:
        return url
    try:
        parsed = urlparse(url)
        if not parsed.query:
            return url
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        redacted_params = []
        for k, vals in query_params.items():
            if k.lower() in SENSITIVE_PARAM_KEYS:
                redacted_params.append((k, "REDACTED"))
            else:
                for v in vals:
                    redacted_params.append((k, v))
        new_query = urlencode(redacted_params)
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        ))
    except Exception:
        return url


def failure_signature(result: dict[str, Any]) -> str:
    """Build a deterministic signature ignoring volatile URLs and timing."""
    state = str(result.get("state", ""))
    failed_stage = str(result.get("failed_stage", ""))
    classification = str(result.get("classification", ""))
    message = str(result.get("message", "")).strip().lower()
    raw = f"{state}|{failed_stage}|{classification}|{message}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def validate_site_profile(profile: dict[str, Any], is_tier_1: bool = False) -> None:
    """Validate that a profile has required fields, especially strict_contract for Tier 1."""
    if is_tier_1:
        contract = profile.get("strict_contract")
        if not contract or not isinstance(contract, dict):
            raise ValueError("Tier 1 site missing strict_contract profile")
        required_keys = {"min_video_items", "min_unique_title_ratio", "min_unique_url_ratio"}
        if not required_keys.issubset(contract.keys()):
            raise ValueError(f"Tier 1 strict_contract missing required keys: {required_keys - contract.keys()}")
