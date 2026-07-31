import pytest
from scripts import live_smoke_test
from scripts.site_health_types import validate_site_profile


def test_default_site_profile_exposes_all_core_steps():
    profile = live_smoke_test.get_site_profile("nonexistent-site")

    assert profile["supports"]["main"] is True
    assert profile["supports"]["list"] is True
    assert profile["supports"]["categories"] is True
    assert profile["supports"]["search"] is True
    assert profile["supports"]["play"] is True
    assert profile["content_type"] == "video"
    assert "strict_contract" in profile
    assert profile["strict_contract"]["min_video_items"] == 5


def test_site_profile_merges_site_specific_overrides():
    profile = live_smoke_test.get_site_profile("chaturbate")

    assert profile["content_type"] == "cam"
    assert profile["supports"]["main"] is True
    assert profile["supports"]["categories"] is False
    assert profile["supports"]["play"] is False
    assert profile["harness"]["playback_not_testable"] is True
    assert profile["harness"]["search_results_optional"] is True


def test_requires_flaresolverr_flag_is_present_for_seeded_sites():
    profile = live_smoke_test.get_site_profile("missav")

    assert profile["requires_flaresolverr"] is True


def test_all_tier_1_sites_pass_strict_contract_validation():
    profiles = live_smoke_test.SITE_PROFILES
    for site_name, site_data in profiles.get("sites", {}).items():
        if site_data.get("tier") == 1:
            profile = live_smoke_test.get_site_profile(site_name)
            validate_site_profile(profile, is_tier_1=True)


def test_validate_site_profile_rejects_missing_strict_contract():
    invalid_profile = {"content_type": "video"}
    with pytest.raises(ValueError, match="Tier 1 site missing strict_contract"):
        validate_site_profile(invalid_profile, is_tier_1=True)
