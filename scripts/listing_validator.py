import re
from typing import Any
from urllib.parse import urlparse

from scripts.site_health_types import ValidationResult, redact_url

COLOR_TAG_RE = re.compile(r"\[/?COLOR[^\]]*\]", re.IGNORECASE)
CHALLENGE_KEYWORDS = [
    "cloudflare",
    "just a moment",
    "attention required",
    "ddos-guard",
    "enable javascript",
    "security check",
    "verify you are human",
]
DEFAULT_DISALLOWED_MODES = {"category", "categories", "login", "logout", "search", "genre"}


def strip_kodi_markup(text: str) -> str:
    if not text:
        return ""
    return COLOR_TAG_RE.sub("", text).strip()


def validate_listing(
    items: list[dict[str, Any]],
    contract: dict[str, Any],
    baseline: dict[str, Any] | None = None,
) -> ValidationResult:
    """Validate listing items against strict contract requirements."""
    evidence: dict[str, Any] = {
        "sample_count": len(items),
        "samples": [
            {
                "name": strip_kodi_markup(item.get("name", "")),
                "url": redact_url(item.get("url", "")),
                "mode": item.get("mode", ""),
            }
            for item in items[:5]
        ],
    }

    # Challenge check
    for item in items:
        name = strip_kodi_markup(item.get("name", "")).lower()
        url = item.get("url", "").lower()
        for kw in CHALLENGE_KEYWORDS:
            if kw in name or kw in url:
                return ValidationResult(
                    passed=False,
                    classification="CHALLENGE",
                    message=f"Challenge page signature detected: '{kw}'",
                    evidence=evidence,
                )

    min_items = contract.get("min_video_items", 5)
    if len(items) < min_items:
        return ValidationResult(
            passed=False,
            classification="PARSER",
            message=f"Insufficient items ({len(items)} < {min_items})",
            evidence=evidence,
        )

    titles = [strip_kodi_markup(item.get("name", "")) for item in items]
    urls = [item.get("url", "") for item in items]

    # Blank title check
    blank_titles = [t for t in titles if not t]
    if blank_titles:
        return ValidationResult(
            passed=False,
            classification="PARSER",
            message=f"Blank titles detected in {len(blank_titles)} item(s)",
            evidence=evidence,
        )

    # Scheme check
    non_http = [u for u in urls if urlparse(u).scheme and urlparse(u).scheme not in ("http", "https")]
    if non_http:
        return ValidationResult(
            passed=False,
            classification="PARSER",
            message=f"Non-HTTP URLs detected in {len(non_http)} item(s)",
            evidence=evidence,
        )

    item_count = len(items)
    unique_title_ratio = len(set(titles)) / item_count
    unique_url_ratio = len(set(urls)) / item_count
    thumb_count = sum(1 for item in items if item.get("icon"))
    desc_count = sum(1 for item in items if item.get("desc"))

    metrics = {
        "item_count": item_count,
        "unique_title_ratio": round(unique_title_ratio, 4),
        "unique_url_ratio": round(unique_url_ratio, 4),
        "thumbnail_coverage": round(thumb_count / item_count, 4),
        "description_coverage": round(desc_count / item_count, 4),
    }

    min_title_ratio = contract.get("min_unique_title_ratio", 0.8)
    if unique_title_ratio < min_title_ratio:
        return ValidationResult(
            passed=False,
            classification="PARSER",
            message=f"Duplicate title ratio below threshold ({unique_title_ratio:.2f} < {min_title_ratio})",
            metrics=metrics,
            evidence=evidence,
        )

    min_url_ratio = contract.get("min_unique_url_ratio", 0.8)
    if unique_url_ratio < min_url_ratio:
        return ValidationResult(
            passed=False,
            classification="PARSER",
            message=f"Duplicate URL ratio below threshold ({unique_url_ratio:.2f} < {min_url_ratio})",
            metrics=metrics,
            evidence=evidence,
        )

    # Disallowed mode check
    disallowed_modes = set(contract.get("disallowed_modes", DEFAULT_DISALLOWED_MODES))
    for item in items:
        mode = str(item.get("mode", "")).lower()
        if mode in disallowed_modes:
            return ValidationResult(
                passed=False,
                classification="PARSER",
                message=f"Disallowed mode in listing: {mode}",
                metrics=metrics,
                evidence=evidence,
            )

    # Host validation
    allowed_hosts = contract.get("allowed_hosts", [])
    if allowed_hosts:
        for u in urls:
            host = urlparse(u).netloc.lower()
            if not any(host == ah or host.endswith("." + ah) for ah in allowed_hosts):
                return ValidationResult(
                    passed=False,
                    classification="HOST_DISALLOWED",
                    message=f"Disallowed host in listing URL: {host}",
                    metrics=metrics,
                    evidence=evidence,
                )

    # Baseline comparison
    if baseline and baseline.get("item_count"):
        prev_count = baseline["item_count"]
        max_drop = contract.get("max_count_drop_ratio", 0.7)
        drop_ratio = 1.0 - (item_count / prev_count)
        if drop_ratio > max_drop:
            return ValidationResult(
                passed=False,
                classification="COUNT_DROP",
                message=f"Item count dropped by {drop_ratio:.1%} from baseline ({prev_count} -> {item_count})",
                metrics=metrics,
                evidence=evidence,
            )

    return ValidationResult(
        passed=True,
        classification="NONE",
        message="Listing contract satisfied",
        metrics=metrics,
        evidence=evidence,
    )
