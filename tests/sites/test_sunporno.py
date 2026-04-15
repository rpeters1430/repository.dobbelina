import pytest
from resources.lib.sites import sunporno
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
                "mode": sunporno.site.get_full_mode(mode),
                "icon": iconimage,
                "desc": desc,
                "duration": kwargs.get("duration")
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": sunporno.site.get_full_mode(mode),
            }
        )


def test_list_populates_videos(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, sunporno, {"latest": "sites/sunporno/list.html"}
    )
    monkeypatch.setattr(sunporno.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(sunporno.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(sunporno.utils, "eod", lambda *args, **kwargs: None)

    sunporno.List("https://www.sunporno.com/latest")

    assert len(recorder.downloads) == 2
    assert recorder.downloads[0]["name"] == "Vasya Sylvia - When reading is out of the question!"
    assert recorder.downloads[0]["icon"] == "https://acdn.sunporno.com/contents/videos_screenshots/86000/86140/324x182/3.jpg"
    assert recorder.downloads[0]["duration"] == "24:04"
    
    # Test relative URL resolution
    assert recorder.downloads[1]["url"] == "https://www.sunporno.com/v/98892/busty-blonde-natalia-starr-fucks-her-friend-s-brother-until-her-explodes/"
    assert recorder.downloads[1]["icon"] == "https://www.sunporno.com/98892_320x180.jpg"
    
    # Test pagination
    assert len(recorder.dirs) == 1
    assert "Next Page (2)" in recorder.dirs[0]["name"]
    assert recorder.dirs[0]["url"] == "https://www.sunporno.com/recent/2/"


def test_playvid_detects_kt_player(monkeypatch):
    html = "<html><body><script>var flashvars = { video_url: 'test.mp4' }; // kt_player detected</script></body></html>"
    
    play_calls = []
    class FakeVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = type('Progress', (), {'update': lambda *a: None})()
            
        def play_from_kt_player(self, html, url):
            play_calls.append((html, url))

    monkeypatch.setattr(sunporno.utils, "getHtml", lambda *args, **kwargs: html)
    monkeypatch.setattr(sunporno.utils, "VideoPlayer", FakeVideoPlayer)

    sunporno.Playvid("https://www.sunporno.com/v/123/", "Test Video")

    assert len(play_calls) == 1
    assert play_calls[0][1] == "https://www.sunporno.com/v/123/"
