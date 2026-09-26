from scripts.verify_site_collection import missing_sites, SITE_ALIASES
from scripts.generate_smoke_matrix import discover_site_names, load_profiles, build_strict_matrix


def test_missing_sites_complete():
    all_sites = discover_site_names()
    strict_sites = [item["site"] for item in build_strict_matrix(load_profiles())["include"]]

    broad = {"sites": [{"site": s} for s in all_sites]}
    strict = {"sites": {s: {"state": "HEALTHY"} for s in strict_sites}}

    missing_b, missing_s = missing_sites(broad, strict)
    assert missing_b == []
    assert missing_s == []


def test_missing_sites_with_aliases():
    all_sites = discover_site_names()
    strict_sites = [item["site"] for item in build_strict_matrix(load_profiles())["include"]]

    # Replace stem names with known legacy aliases
    rev_aliases = {v: k for k, v in SITE_ALIASES.items()}
    broad = {"sites": [{"site": rev_aliases.get(s, s)} for s in all_sites]}
    strict = {"sites": {s: {"state": "HEALTHY"} for s in strict_sites}}

    missing_b, missing_s = missing_sites(broad, strict)
    assert missing_b == []
    assert missing_s == []


def test_missing_sites_detects_truly_missing():
    all_sites = discover_site_names()
    strict_sites = [item["site"] for item in build_strict_matrix(load_profiles())["include"]]

    broad = {"sites": [{"site": s} for s in all_sites if s != "pornhub"]}
    strict = {"sites": {s: {"state": "HEALTHY"} for s in strict_sites if s != "pornhub"}}

    missing_b, missing_s = missing_sites(broad, strict)
    assert "pornhub" in missing_b
    assert "pornhub" in missing_s
