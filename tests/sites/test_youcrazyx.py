from resources.lib.sites import youcrazyx
from tests.conftest import fixture_mapped_get_html


class _Recorder:
    def __init__(self):
        self.downloads = []
        self.dirs = []

    def add_download(self, name, url, mode, iconimage, desc="", *args, **kwargs):
        self.downloads.append(
            {
                "name": name,
                "url": url,
                "mode": youcrazyx.site.get_full_mode(mode),
                "icon": iconimage,
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": youcrazyx.site.get_full_mode(mode),
            }
        )


def test_list_populates_download_links(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, youcrazyx, {"www.youcrazyx.com/": "sites/youcrazyx/list.html"}
    )
    monkeypatch.setattr(youcrazyx.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(youcrazyx.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(youcrazyx.utils, "eod", lambda *args, **kwargs: None)

    youcrazyx.List("https://www.youcrazyx.com/")

    # Check first item
    assert recorder.downloads[0] == {
        "name": "Scarlett Rosewood, Lilibet Saunders - Am I As Good As Mom? Their Wives Cancelled, But The Couples Trip Is Still On 05 02 2026",
        "url": "https://www.youcrazyx.com/video/scarlett-rosewood-lilibet-saunders-am-i-as-good-as-mom-their-wives-cancelled-but-the-couples-trip-is-still-on-05-02-2026-120131.html",
        "mode": "youcrazyx.Playvid",
        "icon": "https://images.youcrazyx.com/thumbs/6/9/8/4/7/69847c232f282.mp4/69847c232f282.mp4-2.jpg",
    }


def test_search_without_keyword(monkeypatch):
    searched = []
    monkeypatch.setattr(youcrazyx.site, "search_dir", lambda url, mode: searched.append(url))
    youcrazyx.Search("https://www.youcrazyx.com/searchgate.php?mode=search&q=")
    assert searched == ["https://www.youcrazyx.com/searchgate.php?mode=search&q="]


def test_search_with_keyword(monkeypatch):
    lists = []
    monkeypatch.setattr(youcrazyx, "List", lambda url: lists.append(url))
    
    # Test with standard search URL
    youcrazyx.Search("https://www.youcrazyx.com/searchgate.php?mode=search&q=", keyword="milf amateur")
    assert lists[0] == "https://www.youcrazyx.com/searchgate.php?mode=search&q=milf+amateur"
    
    # Test with site URL fallback (e.g. from smoke test runner)
    youcrazyx.Search("https://www.youcrazyx.com/", keyword="test query")
    assert lists[1] == "https://www.youcrazyx.com/searchgate.php?mode=search&q=test+query"
    # Wait, I need to check the icon in the fixture for the first item.
