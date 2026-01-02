"""Coverage checks for BS4-converted sites."""

import csv
from pathlib import Path

import pytest


def _normalized_site(site_name):
    return site_name.replace("-", "_")


def _collect_bs4_sites(root):
    csv_path = root / "bs4_migration_audit.csv"
    with csv_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            row["Site"].strip()
            for row in reader
            if row["BeautifulSoup"].strip().lower() == "true"
        ]


def _collect_test_stems(root):
    test_stems = {path.stem for path in (root / "tests" / "sites").glob("test_*.py")}
    test_stems.update({path.stem for path in (root / "tests").glob("test_*.py")})
    return test_stems


def _has_test_for_site(test_stems, site_name):
    normalized = _normalized_site(site_name)
    if f"test_{normalized}" in test_stems:
        return True
    return any(stem.startswith(f"test_{normalized}_") for stem in test_stems)


ROOT = Path(__file__).resolve().parents[1]
BS4_SITES = _collect_bs4_sites(ROOT)
TEST_STEMS = _collect_test_stems(ROOT)


@pytest.mark.parametrize("site_name", BS4_SITES)
def test_bs4_site_has_tests(site_name):
    """Ensure every BS4-converted site has a corresponding test file."""
    assert _has_test_for_site(TEST_STEMS, site_name), site_name
