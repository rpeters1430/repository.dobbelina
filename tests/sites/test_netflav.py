from pathlib import Path

from resources.lib.sites import netflav

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "netflav"


def load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_list_parses_videos_and_next_page(monkeypatch):
    html = load_fixture("listing.html")

    downloads = []
    dirs = []

    monkeypatch.setattr(netflav.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(netflav.utils, "eod", lambda *a, **k: None)

    def fake_add_download_link(name, url, mode, iconimage, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "icon": iconimage,
                "plot": desc,
                "context": kwargs.get("contextm"),
            }
        )

    def fake_add_dir(name, url, mode, iconimage=None, desc="", **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "section": kwargs.get("section"),
            }
        )

    monkeypatch.setattr(netflav.site, "add_download_link", fake_add_download_link)
    monkeypatch.setattr(netflav.site, "add_dir", fake_add_dir)

    netflav.List("https://netflav.com/all?page=1", section="all")

    assert len(downloads) == 2
    assert downloads[0]["name"] == "Sample Title One"
    assert downloads[0]["url"].endswith("video?id=abc123")
    assert "2024-11-15" in downloads[0]["plot"]
    assert downloads[0]["context"]

    assert downloads[1]["name"] == "Sample Title Two"
    assert downloads[1]["url"].endswith("video?id=def456")
    assert "2024-11-10" in downloads[1]["plot"]

    next_pages = [d for d in dirs if "Next Page" in d["name"]]
    assert next_pages
    assert next_pages[0]["url"].endswith("page=2")
    assert next_pages[0]["section"] == "all"


def test_genres_groups_and_sorts(monkeypatch):
    html = load_fixture("genres.html")

    dirs = []

    monkeypatch.setattr(netflav.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(netflav.utils, "eod", lambda *a, **k: None)

    def fake_add_dir(name, url, mode, iconimage=None, desc="", **kwargs):
        dirs.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
            }
        )

    monkeypatch.setattr(netflav.site, "add_dir", fake_add_dir)

    netflav.Genres("https://netflav.com/genre")

    assert len(dirs) == 5
    names = [d["name"] for d in dirs]
    # Should be sorted within each header
    assert names[:3] == [
        "Popular Genres - Action",
        "Popular Genres - Comedy",
        "Popular Genres - Romance",
    ]
    assert names[3:] == [
        "Sub Genres - Drama",
        "Sub Genres - Horror",
    ]

    for dir_item in dirs:
        assert dir_item["url"].startswith("https://netflav.com/")
        assert "page=1" in dir_item["url"]
