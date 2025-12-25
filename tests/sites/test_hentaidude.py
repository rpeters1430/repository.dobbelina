import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugin.video.cumination"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

MODULE_PATH = PLUGIN_ROOT / "resources" / "lib" / "sites" / "hentaidude.py"
spec = importlib.util.spec_from_file_location("hentaidude", MODULE_PATH)
hentaidude = importlib.util.module_from_spec(spec)
if spec and spec.loader:
    spec.loader.exec_module(hentaidude)
    sys.modules["hentaidude"] = hentaidude


FIXTURE_BASE = Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "hentaidude"


def load_fixture(name: str) -> str:
    return (FIXTURE_BASE / name).read_text(encoding="utf-8")


def test_list_uses_soup_spec_and_next_page(monkeypatch):
    html = load_fixture("list.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(hentaidude.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hentaidude.utils, "eod", lambda: None)

    def fake_add_download_link(name, url, mode, thumb, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "thumb": thumb,
                "desc": desc,
            }
        )

    monkeypatch.setattr(hentaidude.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(hentaidude.site, "add_dir", lambda *a, **k: dirs.append(a))

    hentaidude.List(
        "https://hentaidude.xxx/genre/uncensored-hentai/page/1/?m_orderby=latest"
    )

    assert len(downloads) == 20
    assert downloads[0]["url"].startswith("https://hentaidude.xxx/watch/")
    assert "Episode" in downloads[0]["name"]

    next_entries = [entry for entry in dirs if entry[2] == "List"]
    assert next_entries
    assert "Next Page" in next_entries[0][0]


def test_search_path_shares_listing(monkeypatch):
    html = load_fixture("search.html")
    downloads = []

    monkeypatch.setattr(hentaidude.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hentaidude.utils, "eod", lambda: None)

    monkeypatch.setattr(
        hentaidude.site, "add_download_link", lambda *a, **k: downloads.append(a)
    )

    hentaidude.List("https://hentaidude.xxx/?s=query")

    assert len(downloads) == 20
