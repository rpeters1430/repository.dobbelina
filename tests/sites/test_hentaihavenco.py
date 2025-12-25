import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugin.video.cumination"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

MODULE_PATH = PLUGIN_ROOT / "resources" / "lib" / "sites" / "hentaihavenco.py"
spec = importlib.util.spec_from_file_location("hentaihavenco", MODULE_PATH)
hentaihavenco = importlib.util.module_from_spec(spec)
if spec and spec.loader:
    spec.loader.exec_module(hentaihavenco)
    sys.modules["hentaihavenco"] = hentaihavenco


FIXTURE_BASE = (
    Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "hentaihavenco"
)


def load_fixture(name: str) -> str:
    return (FIXTURE_BASE / name).read_text(encoding="utf-8")


def test_list_uses_soup_spec_and_pagination(monkeypatch):
    html = load_fixture("list.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(hentaihavenco.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hentaihavenco.utils, "eod", lambda: None)

    monkeypatch.setattr(
        hentaihavenco.site, "add_download_link", lambda *a, **k: downloads.append(a)
    )
    monkeypatch.setattr(hentaihavenco.site, "add_dir", lambda *a, **k: dirs.append(a))

    hentaihavenco.List("https://hentaihaven.co/")

    assert len(downloads) == 40
    assert downloads[0][1].startswith("https://hentaihaven.co/watch/")

    next_links = [entry for entry in dirs if entry[2] == "List"]
    assert next_links
    assert "Next Page" in next_links[0][0]


def test_categories_include_counts(monkeypatch):
    html = load_fixture("categories.html")
    dirs = []

    monkeypatch.setattr(hentaihavenco.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hentaihavenco.utils, "eod", lambda: None)

    monkeypatch.setattr(hentaihavenco.site, "add_dir", lambda *a, **k: dirs.append(a))

    hentaihavenco.Categories("https://hentaihaven.co/genres/")

    assert dirs
    labels = [entry[0] for entry in dirs]
    assert any("videos" in label for label in labels)


def test_series_handles_next(monkeypatch):
    html = load_fixture("series.html")
    dirs = []

    monkeypatch.setattr(hentaihavenco.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(hentaihavenco.utils, "eod", lambda: None)

    monkeypatch.setattr(hentaihavenco.site, "add_dir", lambda *a, **k: dirs.append(a))

    hentaihavenco.Series("https://hentaihaven.co/series/")

    assert len(dirs) >= 2
    assert any(entry[2] == "Series" and "Next Page" in entry[0] for entry in dirs)
