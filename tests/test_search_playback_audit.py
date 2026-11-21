"""Verdict logic of scripts/search_playback_audit.py (no network)."""

from scripts import search_playback_audit as audit


def _rec(list_play="OK", search_play="OK", search="PASS", list_img="OK", search_img="OK"):
    def img(result):
        return {"result": result, "loaded": 0, "probed": 3, "with_icon": 0, "videos": 10, "probes": []}

    return {
        "steps": {"search": {"status": search, "message": "m"}},
        "list_play": {"result": list_play, "message": "lp"},
        "search_play": {"result": search_play, "message": "sp"},
        "list_images": img(list_img),
        "search_images": img(search_img),
    }


def test_clean_site_is_ok():
    assert audit.verdict_for(_rec())[0] == "OK"


def test_list_plays_but_search_result_does_not():
    verdict, reasons = audit.verdict_for(_rec(search_play="BROKEN"))
    assert verdict == "SEARCH_PLAY_BROKEN"
    assert "search result" in reasons[0]


def test_empty_search_is_search_broken_not_search_play_broken():
    rec = _rec(search_play="FAIL", search="FAIL")
    assert audit.verdict_for(rec)[0] == "SEARCH_BROKEN"
    assert "SEARCH_PLAY_BROKEN" not in rec["tags"]


def test_both_broken_is_play_broken():
    assert audit.verdict_for(_rec(list_play="FAIL", search_play="FAIL"))[0] == "PLAY_BROKEN"


def test_missing_search_thumbnails_flagged():
    rec = _rec(search_img="MISSING")
    assert audit.verdict_for(rec)[0] == "SEARCH_IMAGES_BROKEN"


def test_unverified_hoster_is_clean():
    verdict = audit.verdict_for(_rec(list_play="UNVERIFIED", search_play="UNVERIFIED"))[0]
    assert verdict in audit.CLEAN


def test_check_stream_marks_hoster_unverified():
    info = audit.check_stream(
        {"status": "PASS", "play_url": "https://host/embed/1", "play_via": "play_from_link_to_resolve"}, 1
    )
    assert info["result"] == "UNVERIFIED"


def test_check_images_missing_when_no_icons():
    res = audit.check_images({"video_items": 5, "image_items": 0, "thumbs": []}, "https://x/", 3, 1)
    assert res["result"] == "MISSING"
