import pytest
from scripts.listing_validator import validate_listing


def default_contract():
    return {
        "min_video_items": 5,
        "min_unique_title_ratio": 0.8,
        "min_unique_url_ratio": 0.8,
        "max_count_drop_ratio": 0.7,
        "allowed_hosts": ["example.test", "cdn.example.test"],
        "disallowed_modes": ["category", "categories", "login", "logout", "search", "genre"],
    }


def video(name="Video Title", url="https://example.test/watch/1", mode="play", icon="https://cdn.example.test/img.jpg", desc="Description"):
    return {
        "name": name,
        "url": url,
        "mode": mode,
        "icon": icon,
        "desc": desc,
    }


def test_healthy_five_item_listing():
    items = [
        video(f"Video {i}", f"https://example.test/watch/{i}")
        for i in range(1, 6)
    ]
    result = validate_listing(items, default_contract())
    assert result.passed is True
    assert result.classification == "NONE"
    assert result.metrics["item_count"] == 5
    assert result.metrics["unique_title_ratio"] == 1.0
    assert result.metrics["unique_url_ratio"] == 1.0


def test_zero_items_is_broken():
    result = validate_listing([], default_contract())
    assert result.passed is False
    assert result.classification == "PARSER"
    assert "Insufficient items" in result.message


def test_duplicate_flood_is_broken():
    items = [video("A", "https://example.test/watch/1") for _ in range(5)]
    result = validate_listing(items, default_contract())
    assert result.passed is False
    assert result.classification == "PARSER"
    assert "Duplicate URL ratio" in result.message or "ratio" in result.message


def test_blank_titles_is_broken():
    items = [
        video("", f"https://example.test/watch/{i}")
        for i in range(1, 6)
    ]
    result = validate_listing(items, default_contract())
    assert result.passed is False
    assert result.classification == "PARSER"
    assert "Blank titles" in result.message


def test_non_http_urls_is_broken():
    items = [
        video(f"Video {i}", f"ftp://example.test/watch/{i}")
        for i in range(1, 6)
    ]
    result = validate_listing(items, default_contract())
    assert result.passed is False
    assert result.classification == "PARSER"


def test_disallowed_host_is_broken():
    items = [
        video(f"Video {i}", f"https://evil.test/watch/{i}")
        for i in range(1, 6)
    ]
    result = validate_listing(items, default_contract())
    assert result.passed is False
    assert result.classification == "HOST_DISALLOWED"


def test_disallowed_mode_is_broken():
    items = [
        video(f"Category {i}", f"https://example.test/cat/{i}", mode="category")
        for i in range(1, 6)
    ]
    result = validate_listing(items, default_contract())
    assert result.passed is False
    assert result.classification == "PARSER"
    assert "Disallowed mode" in result.message


def test_challenge_page_evidence_is_blocked():
    items = [
        video("Just a moment...", "https://example.test/cloudflare"),
        video("Attention Required! | Cloudflare", "https://example.test/cf2"),
    ]
    result = validate_listing(items, default_contract())
    assert result.passed is False
    assert result.classification == "CHALLENGE"


def test_baseline_count_drop_is_broken():
    items = [
        video(f"Video {i}", f"https://example.test/watch/{i}")
        for i in range(1, 6)
    ]
    # Baseline had 20 items, current has 5 -> drop ratio is 1 - 5/20 = 0.75 > max 0.7
    baseline = {"item_count": 20}
    result = validate_listing(items, default_contract(), baseline=baseline)
    assert result.passed is False
    assert result.classification == "COUNT_DROP"
