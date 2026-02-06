from resources.lib.sites import xmoviesforyou
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
                "mode": xmoviesforyou.site.get_full_mode(mode),
                "icon": iconimage,
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": xmoviesforyou.site.get_full_mode(mode),
            }
        )


def test_list_populates_download_links(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, xmoviesforyou, {"xmoviesforyou.com/": "sites/xmoviesforyou/list.html"}
    )
    monkeypatch.setattr(xmoviesforyou.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(xmoviesforyou.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(xmoviesforyou.utils, "eod", lambda *args, **kwargs: None)

    xmoviesforyou.List("https://xmoviesforyou.com/")

    # Check first item and title formatting
    assert recorder.downloads[0]["name"].startswith("[COLOR pink]DaughterSwap[/COLOR]")
    assert recorder.downloads[0]["url"] == "https://xmoviesforyou.com/2026/02/daughterswap-scarlett-rosewood-lilibet-saunders-am-i-as-good-as-mom-their-wives-cancelled-but-the-couples-trip-is-still-on.html"
    
    # Check pagination
    assert recorder.dirs == [
        {
            "name": "Next Page",
            "url": "https://xmoviesforyou.com/page/2",
            "mode": "xmoviesforyou.List",
        }
    ]
