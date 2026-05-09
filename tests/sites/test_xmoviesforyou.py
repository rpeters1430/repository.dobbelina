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
        monkeypatch,
        xmoviesforyou,
        {"xmoviesforyou.com/": "sites/xmoviesforyou/list.html"},
    )
    monkeypatch.setattr(xmoviesforyou.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(xmoviesforyou.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(xmoviesforyou.utils, "eod", lambda *args, **kwargs: None)

    xmoviesforyou.List("https://xmoviesforyou.com/")

    assert len(recorder.downloads) == 2
    assert recorder.downloads[0]["name"] == "Video One"
    assert recorder.downloads[0]["url"] == "https://xmoviesforyou.com/video1/"

    # Check pagination
    assert len(recorder.dirs) == 1
    assert "Next" in recorder.dirs[0]["name"]


def test_search_delegates_to_list(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch,
        xmoviesforyou,
        {
            "q=test": "sites/xmoviesforyou/list.html",
        },
    )
    monkeypatch.setattr(xmoviesforyou.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(xmoviesforyou.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(xmoviesforyou.utils, "eod", lambda *args, **kwargs: None)

    xmoviesforyou.Search("https://xmoviesforyou.com/", keyword="test")

    assert len(recorder.downloads) == 2
