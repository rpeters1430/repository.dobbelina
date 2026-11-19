"""Search checks in the live smoke harness must hit the site's real search URL."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# run_site_child installs Kodi stubs and patches utils globally, so each run
# happens in its own interpreter, the same way run_parent runs sites.
_CHILD = """
import json, sys
search_html = sys.argv[1] or None  # read before run_site_child rewrites sys.argv
sys.path.insert(0, ".")
from pathlib import Path
from scripts import live_smoke_test
live_smoke_test.run_site_child("xnxx", steps=[])
from resources.lib import utils
listing = Path("tests/fixtures/sites/xnxx/listing.html").read_text(encoding="utf-8")
requested = []
def fake_get_html(url, *args, **kwargs):
    requested.append(url)
    if "/search/" in url and search_html is not None:
        return search_html
    return listing
utils.getHtml = fake_get_html
record = live_smoke_test.run_site_child(
    "xnxx", steps=["main", "search", "search_play"], keyword="test"
)
print(json.dumps({"record": record, "requested": requested}))
"""


def _run_xnxx(search_html):
    proc = subprocess.run(
        [sys.executable, "-c", _CHILD, search_html or ""],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    )
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    return payload["record"], payload["requested"]


def test_search_uses_search_url_from_main():
    record, requested = _run_xnxx(search_html=None)
    assert any(u.endswith("/search/test") for u in requested), requested
    assert record["steps"]["search"]["status"] == "PASS"
    assert record["steps"]["search"]["sample_url"].endswith("/search/")
    # The first search result is what gets played.
    assert "No search result" not in record["steps"]["search_play"]["message"]


def test_empty_search_fails_the_site():
    record, _ = _run_xnxx(search_html="<html><body></body></html>")
    assert record["steps"]["search"]["status"] == "FAIL"
    assert record["steps"]["search_play"]["status"] == "FAIL"
    assert record["overall"] == "FAIL"


@pytest.mark.parametrize("stage", ["search", "search_play"])
def test_strict_monitor_requires_search_stages(stage):
    from scripts.strict_site_monitor import evaluate_record

    profile = {
        "strict_contract": {
            "min_video_items": 1,
            "required_stages": ["listing", stage],
        }
    }
    record = {
        "site": "example",
        "status": "PASS",
        "listing_samples": [
            {"name": f"Video {i}", "url": f"https://example.test/{i}", "mode": "play"}
            for i in range(5)
        ],
        "steps": {stage: {"status": "FAIL", "message": "Search for 'test' returned no videos"}},
    }
    report = evaluate_record(record, profile)
    assert report["state"] == "BROKEN"
    assert report["failed_stage"] == stage


def test_strict_monitor_skips_search_when_profile_disables_it():
    from scripts.strict_site_monitor import evaluate_record

    profile = {
        "supports": {"search": False},
        "strict_contract": {"min_video_items": 1, "required_stages": ["listing", "search", "search_play"]},
    }
    record = {
        "site": "example",
        "status": "PASS",
        "listing_samples": [
            {"name": f"Video {i}", "url": f"https://example.test/{i}", "mode": "play"}
            for i in range(5)
        ],
        "steps": {"search": {"status": "SKIP"}},
    }
    assert evaluate_record(record, profile)["state"] == "HEALTHY"
