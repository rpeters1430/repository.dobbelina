
import pytest
from resources.lib.sites import pornhd3x
from tests.conftest import read_fixture

class Recorder:
    def __init__(self):
        self.downloads = []
        self.dirs = []

    def add_download(self, name, url, mode, iconimage, **kwargs):
        self.downloads.append(
            {
                "name": name,
                "url": url,
                "mode": pornhd3x.site.get_full_mode(mode),
                "icon": iconimage,
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": pornhd3x.site.get_full_mode(mode),
            }
        )

def test_list_videos(monkeypatch):
    recorder = Recorder()

    def mock_get_html(url, *args, **kwargs):
        return read_fixture("sites/pornhd3x.html")

    monkeypatch.setattr(pornhd3x.utils, "getHtml", mock_get_html)
    monkeypatch.setattr(pornhd3x.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(pornhd3x.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(pornhd3x.utils, "eod", lambda: None)

    pornhd3x.List("https://www9.pornhd3x.tv/")

    assert len(recorder.downloads) > 0
    first_video = recorder.downloads[0]
    assert first_video["name"] == "Dan Dangler & Angela White Fuck a Guy by the Pool, Alex Mack"
    assert first_video["url"].endswith("/movies/dan-dangler-angela-white-fuck-a-guy-by-the-pool-alex-mack")
    assert "/Cms_Data/Contents/admin/Media/images/" in first_video["icon"]
