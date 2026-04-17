"""Verify every non-testing site has a valid category."""
import importlib

VALID_CATEGORIES = {
    "Video Tubes",
    "Cams & Live",
    "JAV & Asian",
    "Hentai & Anime",
    "Amateur & Social",
    "Specialty",
    "Aggregators",
}


def test_all_sites_have_valid_category():
    from resources.lib.adultsite import AdultSite
    from resources.lib.sites import __all__ as site_names

    checked = []
    for name in site_names:
        mod = importlib.import_module(f"resources.lib.sites.{name}")
        for attr in vars(mod).values():
            if isinstance(attr, AdultSite):
                checked.append((name, attr))

    assert checked, "No AdultSite instances found — check imports"

    uncategorized = [f"{mod}.{s.name}" for mod, s in checked if not s.category]
    assert not uncategorized, (
        f"Sites missing category ({len(uncategorized)}): {sorted(uncategorized)}"
    )

    invalid = [
        f"{mod}.{s.name}"
        for mod, s in checked
        if s.category and s.category not in VALID_CATEGORIES
    ]
    assert not invalid, (
        f"Sites with unknown category string: {sorted(invalid)}"
    )
