from resources.lib.sites import cloudbate
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
                "mode": cloudbate.site.get_full_mode(mode),
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
                "mode": cloudbate.site.get_full_mode(mode),
            }
        )


def test_list_populates_videos(monkeypatch):
    recorder = _Recorder()

    fixture_mapped_get_html(
        monkeypatch, cloudbate, {"latest-updates": "sites/cloudbate/list.html"}
    )
    monkeypatch.setattr(cloudbate.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(cloudbate.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(cloudbate.utils, "eod", lambda *args, **kwargs: None)

    cloudbate.List("https://www.cloudbate.com/latest-updates/")

    assert len(recorder.downloads) == 2
    assert recorder.downloads[0]["name"] == "Model Video 1"
    assert recorder.downloads[0]["icon"] == "https://www.cloudbate.com/contents/videos_screenshots/0/123/preview.webp"
    assert recorder.downloads[0]["duration"] == "10:00"
    
    # Test relative URL resolution
    assert recorder.downloads[1]["url"] == "https://www.cloudbate.com/videos/456/another-video/"
    
    # Test pagination
    assert len(recorder.dirs) == 1
    assert "Next Page (2)" in recorder.dirs[0]["name"]
    assert "of 10" in recorder.dirs[0]["name"]


def test_playvid_detects_kt_player(monkeypatch):
    html = "<html><body><script>kt_player('kt_player', 'args')</script></body></html>"
    
    play_calls = []
    class FakeVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = type('Progress', (), {'update': lambda *a: None})()
            
        def play_from_kt_player(self, html, url):
            play_calls.append((html, url))

    monkeypatch.setattr(cloudbate.utils, "getHtml", lambda *args, **kwargs: html)
    monkeypatch.setattr(cloudbate.utils, "VideoPlayer", FakeVideoPlayer)

    cloudbate.Playvid("https://www.cloudbate.com/videos/123/", "Test Video")

    assert len(play_calls) == 1
    assert play_calls[0][1] == "https://www.cloudbate.com/videos/123/"
