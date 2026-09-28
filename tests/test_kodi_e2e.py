"""Unit tests for the headless-Kodi e2e harness (scripts/kodi_e2e).

The pure parts (checks, log parsing, reports) run everywhere. The real
end-to-end self-test needs Kodi + Xvfb + ffmpeg and only runs with
KODI_E2E=1 (the kodi-e2e workflow sets it).
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.kodi_e2e import checks as C
from scripts.kodi_e2e.driver import StepResult, redact, strip_markup
from scripts.kodi_e2e.logparse import parse_log_lines
from scripts.kodi_e2e.report import diff_baseline, summarise, to_html, to_markdown

ROOT = Path(__file__).resolve().parents[1]
P = "plugin://plugin.video.cumination/"


def vid(title, n=0, thumb="image://http%3a%2f%2fx%2ft.jpg/", mode="site.Playvid"):
    return {"label": title, "filetype": "file", "file": f"{P}?url=u{n}&mode={mode}", "thumbnail": thumb}


def folder(title, mode="site.List", n=0):
    return {"label": title, "filetype": "directory", "file": f"{P}?url=f{n}&mode={mode}", "thumbnail": ""}


def codes(found):
    return {i["code"] for i in found}


# --------------------------------------------------------------------------
# item classification
# --------------------------------------------------------------------------
def test_strip_markup():
    assert strip_markup("[COLOR hotpink]Next Page[/COLOR] [B]2[/B]") == "Next Page 2"


def test_actions_are_not_videos():
    assert C.is_video(vid("Nice video"))
    assert not C.is_video(vid("One time search", mode="utils.oneSearch"))
    assert not C.is_video(vid("Refresh Chaturbate images", mode="chaturbate.clean_database"))
    assert not C.is_video(vid("No videos found. Clear all filters.", mode="pornhub.ResetFilters"))


def test_split_items_finds_next_search_categories_and_settings():
    items = [vid("a"), folder("[COLOR hotpink]Next Page (2)[/COLOR]"), folder("Search", "site.Search"),
             folder("Categories", "site.Categories"), folder("Country:  USA", "xvideos.Country"),
             folder("Category:  Straight", "xvideos.Category")]
    parts = C.split_items(items)
    assert C.label(parts["next"]) == "Next Page (2)"
    assert C.label(parts["search"]) == "Search"
    assert [C.label(c) for c in parts["categories"]] == ["Categories"]
    assert {C.label(s) for s in parts["settings"]} == {"Country:  USA", "Category:  Straight"}


# --------------------------------------------------------------------------
# listing / titles
# --------------------------------------------------------------------------
def test_empty_listing_is_error():
    assert codes(C.check_listing([], "main")) == {"LISTING_EMPTY"}


def test_blank_folders_and_missing_next_page():
    items = [vid(f"Video number {chr(65 + i)}", i) for i in range(12)] + [folder(""), folder("  ")]
    found = codes(C.check_listing(items, "main"))
    assert {"BLANK_FOLDERS", "NO_NEXT_PAGE"} <= found


def test_healthy_listing_has_no_issues():
    items = [vid(f"Beach walk part {chr(65 + i)}", i) for i in range(20)] + [folder("Next Page (2)")]
    assert C.check_listing(items, "main") == []


def test_title_problems_detected():
    titles = ["Hot &amp; Wild", "<b>Studio</b> take", "12:34 Beach day 88123456", "08:15 Pool 77123456",
              "22:10 Picnic 55123456", "Lake trip 99123456"]
    found = codes(C.check_titles([vid(t, i) for i, t in enumerate(titles)], "main"))
    assert {"TITLE_HTML_ENTITIES", "TITLE_HTML_TAGS", "TITLE_NUMBER_NOISE"} <= found


def test_single_number_in_one_title_is_not_noise():
    titles = [f"Garden party scene {c}" for c in "ABCDEFGHI"] + ["Top 10000 moments"]
    assert "TITLE_NUMBER_NOISE" not in codes(C.check_titles([vid(t, i) for i, t in enumerate(titles)], "m"))


def test_handles_and_duplicates():
    vids = [vid(f"@user{i % 2} 1193906{i}", i) for i in range(10)]
    found = codes(C.check_titles(vids, "main"))
    assert "TITLE_HANDLE" in found


# --------------------------------------------------------------------------
# thumbnails
# --------------------------------------------------------------------------
def test_thumbnails_broken_placeholder_and_tiny():
    items = [vid(f"v{i}", i) for i in range(8)]
    fetched = [{"ok": False, "status": 404, "thumb": f"http://x/{i}.jpg"} for i in range(5)] + [
        {"ok": True, "status": 200, "sha1": "abc", "width": 40, "height": 30, "thumb": "http://x/t.jpg", "elapsed": 0.1}
        for _ in range(3)]
    found = codes(C.check_thumbnails(items, fetched, "main"))
    assert {"THUMBS_BROKEN", "THUMBS_PLACEHOLDER", "THUMBS_LOW_RES"} <= found


def test_thumbnails_missing_default_art_counts_as_missing():
    items = [vid(f"v{i}", i, thumb="image://DefaultVideo.png/") for i in range(6)]
    assert "THUMBS_MISSING" in codes(C.check_thumbnails(items, [], "main"))


def test_good_thumbnails_pass():
    items = [vid(f"v{i}", i) for i in range(6)]
    fetched = [{"ok": True, "status": 200, "sha1": f"h{i}", "width": 320, "height": 180, "elapsed": 0.2}
               for i in range(6)]
    assert C.check_thumbnails(items, fetched, "main") == []


# --------------------------------------------------------------------------
# pagination / playback / hints
# --------------------------------------------------------------------------
def test_pagination_same_and_empty():
    page1 = [vid(f"v{i}", i) for i in range(10)]
    same = StepResult("list", "p2", ok=True, items=list(page1))
    empty = StepResult("list", "p2", ok=True, items=[])
    assert codes(C.check_pagination(page1, same, "p2")) == {"NEXT_PAGE_SAME"}
    assert codes(C.check_pagination(page1, empty, "p2")) == {"NEXT_PAGE_EMPTY"}


def test_playback_reason_and_low_quality():
    failed = StepResult("play", "v", ok=False, log={"notifications": ["Oh oh | Could not find a supported link"]},
                        extra={"started": False})
    assert "Could not find a supported link" in C.playback_failure_reason(failed)
    ok = StepResult("play", "v", ok=True, elapsed=5, extra={"width": 176, "height": 144})
    assert codes(C.check_playback(ok, "main")) == {"LOW_QUALITY_STREAM"}


@pytest.mark.parametrize("note,expect", [
    ("Oh oh | It looks like this website is too slow.", "unreachable"),
    ("Oh oh | Cloudflare protection detected. Enable FlareSolverr in addon settings.", "FlareSolverr"),
    ("Oh oh | It looks like this website is down.", "server error"),
    ("Oh oh | It looks like the page does not exist.", "not found"),
])
def test_blocked_hint_from_addon_notifications(note, expect):
    step = StepResult("list", "main", log={"notifications": [note]})
    assert expect in C.blocked_hint(step)


def test_site_status():
    assert C.site_status([]) == "pass"
    assert C.site_status([C.issue("X", "info", "a", "m")]) == "pass"
    assert C.site_status([C.issue("X", "warn", "a", "m")]) == "warn"
    assert C.site_status([C.issue("X", "error", "a", "m"), C.issue("Y", "warn", "a", "m")]) == "fail"


# --------------------------------------------------------------------------
# kodi.log parsing (samples copied from a Kodi 20.5 log)
# --------------------------------------------------------------------------
KODI_LOG = """\
2026-09-28 02:56:07.966 T:3278     info <general>: @@@@Cumination: Notification: Oh oh | Could not find a supported link
2026-09-28 02:56:24.030 T:3395    error <general>: EXCEPTION Thrown (PythonToCppException) : -->Python callback/script returned the following error<--
                                                    - NOTE: IGNORING THIS CAN LEAD TO MEMORY LEAKS!
                                                   Error Type: <class 'ValueError'>
                                                   Error Contents: selftest: simulated scraper crash
                                                   Traceback (most recent call last):
                                                     File "/k/.kodi/addons/plugin.video.cumination/default.py", line 534, in <module>
                                                       sys.exit(main())
                                                     File "/k/.kodi/addons/plugin.video.cumination/resources/lib/sites/e2ebroken.py", line 43, in Crash
                                                       raise ValueError("selftest: simulated scraper crash")
                                                   ValueError: selftest: simulated scraper crash
                                                   -->End of Python script error report<--
2026-09-28 02:56:24.101 T:3394    error <general>: GetDirectory - Error getting plugin://plugin.video.cumination/?mode=e2ebroken.Crash
2026-09-28 02:56:24.228 T:3402  warning <CAddonSettings[0@plugin.video.cumination]>: failed to parse enable condition "eq(-1,true)" of old setting definition for "telemetry_test_report"
2026-09-28 02:56:25.000 T:3402    error <general>: CCurlFile::Open failed with code 403 for https://cdn.example.com/v.mp4?token=secret
2026-09-28 02:56:26.000 T:3402    error <general>: Cumination: incompatible site module (badsite): No module named 'foo'
2026-09-28 02:56:27.000 T:3402    error <general>: GUIFontManager::LoadTTF: Couldn't load font name
"""


def test_parse_kodi_log():
    res = parse_log_lines(KODI_LOG.splitlines())
    assert res["notifications"] == ["Oh oh | Could not find a supported link"]
    exc = res["exceptions"][0]
    assert exc["type"] == "ValueError"
    assert exc["message"] == "selftest: simulated scraper crash"
    assert exc["where"] == "plugin.video.cumination/resources/lib/sites/e2ebroken.py:43 in Crash"
    assert res["directory_errors"]
    assert res["addon_settings"] and "telemetry_test_report" in res["addon_settings"][0]
    assert res["curl_errors"] == [{"code": "403", "host": "cdn.example.com", "what": "open"}]
    assert res["import_errors"] == [{"module": "badsite", "error": "No module named 'foo'"}]
    assert "other_errors" not in res  # font noise filtered


def test_redact_drops_tokens():
    assert redact("https://cdn.x.com/a/b.m3u8?token=abc|Referer=https://y/") == "https://cdn.x.com/a/b.m3u8"


# --------------------------------------------------------------------------
# reports
# --------------------------------------------------------------------------
def _site(name, status, codes_=()):
    return {"site": name, "title": name, "status": status, "message": "m", "hint": None, "duration": 3,
            "issues": [C.issue(c, "error" if status == "fail" else "warn", "listing", c) for c in codes_],
            "notes": [], "notifications": [], "steps": [], "playback": [], "playback_started": status != "fail"}


def test_summary_markdown_html_and_baseline_diff():
    sites = [_site("a", "fail", ["PLAYBACK_FAILED"]), _site("b", "warn", ["NO_NEXT_PAGE"]), _site("c", "pass")]
    baseline = {"sites": [{"site": "a", "status": "pass", "codes": []},
                          {"site": "c", "status": "fail", "codes": ["LISTING_EMPTY"]}]}
    summary = summarise({"kodi": {"major": 21, "minor": 2}}, sites, baseline)
    assert summary["totals"] == {"sites": 3, "pass": 1, "warn": 1, "fail": 1}
    assert [r["site"] for r in summary["changes"]["regressed"]] == ["a"]
    assert [r["site"] for r in summary["changes"]["fixed"]] == ["c"]
    md = to_markdown(summary, sites)
    assert "Newly broken" in md and "| a |" in md
    html = to_html(summary, sites)
    assert "<details class=site data-status=fail" in html
    assert diff_baseline(sites, None) == {}


# --------------------------------------------------------------------------
# profile helpers
# --------------------------------------------------------------------------
def test_profile_dependency_list_reads_addon_xml():
    from scripts.kodi_e2e.profile import read_requires

    reqs = dict(read_requires(ROOT / "plugin.video.cumination"))
    assert "script.module.resolveurl" in reqs
    assert reqs["inputstream.adaptive"] is True  # optional


def test_gui_settings_enable_local_jsonrpc():
    from scripts.kodi_e2e.profile import gui_settings

    s = gui_settings(8099)
    assert s["services.webserver"] == "true" and s["services.webserverport"] == "8099"


# --------------------------------------------------------------------------
# the real thing: Kodi + local fake sites
# --------------------------------------------------------------------------
@pytest.mark.skipif(os.environ.get("KODI_E2E") != "1" or not shutil.which("kodi"),
                    reason="needs Kodi, Xvfb and ffmpeg; set KODI_E2E=1")
def test_selftest_in_real_kodi(tmp_path):
    out = tmp_path / "out"
    proc = subprocess.run([sys.executable, "-m", "scripts.kodi_e2e", "selftest", "--out", str(out)],
                          cwd=ROOT, capture_output=True, text=True, timeout=900)
    print(proc.stdout[-3000:])
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-2000:]
    good = json.loads((out / "sites" / "e2egood.json").read_text())
    assert good["status"] == "pass" and good["playback_started"]
