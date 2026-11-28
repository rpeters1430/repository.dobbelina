from types import SimpleNamespace
from unittest.mock import MagicMock

import default
from resources.lib import global_search, site_status
from resources.lib.url_dispatcher import URL_Dispatcher


def test_global_search_captures_video_results(monkeypatch):
    fake_site = SimpleNamespace(
        name="demo",
        title="Demo Site",
        url="https://demo.example/",
        module_name="demo_mod",
        category="Video Tubes",
        get_clean_title=lambda: "Demo Site",
    )

    def fake_search(url, keyword=None):
        from resources.lib import url_dispatcher as ud
        from resources.lib import utils

        ud.addDir("Next Page", url + "?page=2", "demo_mod.List", "")
        ud.addDownLink(
            f"{keyword} Video 1",
            "https://demo.example/v/1",
            "demo_mod.Playvid",
            "https://demo.example/1.jpg",
        )
        ud.addDownLink(
            f"{keyword} Video 2",
            "https://demo.example/v/2",
            "demo_mod.Playvid",
            "https://demo.example/2.jpg",
        )
        utils.eod()

    monkeypatch.setitem(URL_Dispatcher.func_registry, "demo_mod.Search", fake_search)

    results = global_search.search_sites("latina", sites=[fake_site], per_site_limit=1)
    assert len(results) == 1
    assert results[0]["name"] == "latina Video 1"
    assert results[0]["site_name"] == "demo"
    assert results[0]["site_title"] == "Demo Site"
    assert results[0]["mode"] == "demo_mod.Playvid"


def test_site_status_normalize_and_cache(tmp_path, monkeypatch):
    assert site_status.normalize_status(strict_state="HEALTHY") == "healthy"
    assert site_status.normalize_status(strict_state="BLOCKED") == "blocked"
    assert site_status.normalize_status(strict_state="BROKEN") == "broken"
    assert site_status.normalize_status(broad_overall="PASS") == "healthy"
    assert site_status.normalize_status(broad_overall="FAIL") == "broken"

    monkeypatch.setattr(site_status.basics, "tempDir", str(tmp_path))

    def fake_get(url, timeout=8):
        resp = MagicMock(status_code=200)
        if "strict_health_latest" in url:
            resp.json.return_value = {
                "sites": {
                    "pornhub": {"state": "HealthState.HEALTHY", "message": "ok"},
                    "ask4porn": {"state": "BLOCKED", "message": "challenge"},
                }
            }
        else:
            resp.json.return_value = {
                "sites": [
                    {"site": "pornhub", "overall": "FAIL"},
                    {"site": "broken_site", "overall": "FAIL"},
                ]
            }
        return resp

    monkeypatch.setattr(site_status.requests, "get", fake_get)
    statuses = site_status.get_site_statuses(force_refresh=True)
    # Strict overrides broad for pornhub
    assert statuses["pornhub"]["status"] == "healthy"
    assert statuses["ask4porn"]["status"] == "blocked"
    assert statuses["broken_site"]["status"] == "broken"
    assert (tmp_path / "site_health_cache.json").is_file()


def test_default_site_status_badges_and_hide_broken(monkeypatch):
    s_ok = SimpleNamespace(name="pornhub", title="PornHub", is_new=False)
    s_bad = SimpleNamespace(name="broken_site", title="BrokenSite", is_new=False)
    status_map = {
        "pornhub": {"status": "healthy"},
        "broken_site": {"status": "broken"},
    }

    monkeypatch.setattr(
        default,
        "addon_get_setting",
        lambda key: "true" if key in ("show_site_status_badges", "hide_broken_sites") else "false",
    )

    visible = default._visible_sites([s_ok, s_bad], status_map)
    assert [s.name for s in visible] == ["pornhub"]
    assert "[OK]" in default._site_display_title(s_ok, status_map=status_map)
    assert "[BROKEN]" in default._site_display_title(s_bad, status_map=status_map)


def test_connection_tests_flaresolverr_and_doh(monkeypatch):
    dialogs = []
    monkeypatch.setattr(default.dialog, "ok", lambda title, msg: dialogs.append((title, msg)))
    monkeypatch.setattr(
        default,
        "addon_get_setting",
        lambda key: "http://127.0.0.1:8191/v1" if key == "fs_host" else "0",
    )

    import requests

    monkeypatch.setattr(requests, "get", lambda url, timeout=8: MagicMock(status_code=200))
    default.test_flaresolverr()
    assert dialogs[-1][0] == "FlareSolverr Connection Test"
    assert "Connected successfully!" in dialogs[-1][1]

    from resources.lib import doh

    monkeypatch.setattr(doh, "resolve_doh", lambda host, provider="cloudflare", timeout=6.0: "93.184.216.34")
    default.test_doh()
    assert dialogs[-1][0] == "DoH Connection Test"
    assert "93.184.216.34" in dialogs[-1][1]
