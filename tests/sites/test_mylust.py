from unittest.mock import MagicMock
from resources.lib.sites import mylust


def test_main(monkeypatch):
    dirs = []

    def fake_add_dir(name, url, mode, iconimage="", **kwargs):
        dirs.append({"name": name, "url": url, "mode": mode})

    list_called = []
    monkeypatch.setattr(mylust.site, "add_dir", fake_add_dir)
    monkeypatch.setattr(mylust, "List", lambda url: list_called.append(url))

    mylust.Main()

    modes = [d["mode"] for d in dirs]
    assert "Categories" in modes
    assert "Search" in modes
    assert len(list_called) == 1
    assert "videos/" in list_called[0]


def test_list_parses_videos_and_pagination(monkeypatch):
    html = """
    <html>
    <body>
        <div class="item" data-video-id="123">
            <a href="/videos/123/sample-video/" title="Sample Video Title">
                <img alt="Sample Video Title" data-jpg="https://i.mylust.com/thumbs/123.jpg" />
                <span class="duration">12:34</span>
            </a>
        </div>
        <div class="item" data-video-id="124">
            <a href="https://mylust.com/videos/124/second-video/">
                <img alt="Second Video" src="https://i.mylust.com/thumbs/124.jpg" />
                <span class="duration">05:00</span>
            </a>
        </div>
        <ul class="pagination">
            <li class="next"><a href="/videos/?page=2">Next</a></li>
        </ul>
    </body>
    </html>
    """
    added_links = []
    added_dirs = []

    monkeypatch.setattr(mylust.utils, "getHtml", lambda url, referer="": html)
    monkeypatch.setattr(
        mylust.site,
        "add_download_link",
        lambda name, url, mode, thumb, **k: added_links.append({"name": name, "url": url, "thumb": thumb, "dur": k.get("duration")}),
    )
    monkeypatch.setattr(
        mylust.site,
        "add_dir",
        lambda name, url, mode, icon, **k: added_dirs.append({"name": name, "url": url, "mode": mode}),
    )
    monkeypatch.setattr(mylust.utils, "eod", lambda: None)

    mylust.List("https://mylust.com/videos/")

    assert len(added_links) == 2
    assert added_links[0]["name"] == "Sample Video Title"
    assert "123" in added_links[0]["url"]
    assert added_links[0]["dur"] == "12:34"

    assert added_links[1]["name"] == "Second Video"
    assert "124" in added_links[1]["url"]

    assert len(added_dirs) == 1
    assert added_dirs[0]["name"] == "Next Page"
    assert "page=2" in added_dirs[0]["url"]


def test_categories(monkeypatch):
    html = """
    <html>
    <body>
        <div class="item">
            <a href="/categories/amateur/" title="Amateur">
                <img src="/contents/categories/1/s1_1.jpg" />
                <span class="video_count">1200 videos</span>
            </a>
        </div>
    </body>
    </html>
    """
    dirs = []
    monkeypatch.setattr(mylust.utils, "getHtml", lambda url, referer="": html)
    monkeypatch.setattr(
        mylust.site,
        "add_dir",
        lambda name, url, mode, thumb, **k: dirs.append({"name": name, "url": url, "thumb": thumb}),
    )
    monkeypatch.setattr(mylust.utils, "eod", lambda: None)

    mylust.Categories("https://mylust.com/categories/")

    assert len(dirs) == 1
    assert "Amateur" in dirs[0]["name"]
    assert "1200" in dirs[0]["name"]
    assert "https://mylust.com/categories/amateur/" == dirs[0]["url"]


def test_search_with_keyword(monkeypatch):
    list_calls = []
    monkeypatch.setattr(mylust, "List", lambda url: list_calls.append(url))

    mylust.Search("https://mylust.com/search/", keyword="blonde girl")

    assert len(list_calls) == 1
    assert "q=blonde+girl" in list_calls[0]


def test_search_prompt_without_keyword(monkeypatch):
    search_dirs = []
    monkeypatch.setattr(mylust.site, "search_dir", lambda url, prompt: search_dirs.append((url, prompt)))

    mylust.Search("https://mylust.com/search/", keyword=None)

    assert len(search_dirs) == 1
    assert search_dirs[0][0] == "https://mylust.com/search/"


def test_playvid_selects_highest_quality(monkeypatch):
    html = """
    <html>
    <body>
        <video>
            <source src="https://mylust.com/get_file/1/test_720p.mp4" title="720p" />
            <source src="https://mylust.com/get_file/1/test_1080p.mp4" title="1080p" />
        </video>
    </body>
    </html>
    """
    played = []

    class FakeVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = MagicMock()

        def play_from_direct_link(self, link):
            played.append(link)

    monkeypatch.setattr(mylust.utils, "getHtml", lambda url, referer="": html)
    monkeypatch.setattr(mylust.utils, "VideoPlayer", FakeVideoPlayer)

    mylust.Playvid("https://mylust.com/videos/123/", "Test Video")

    assert len(played) == 1
    assert "test_1080p.mp4" in played[0]
    assert "|verifypeer=false" in played[0]


def test_playvid_fallback_json_ld(monkeypatch):
    html = """
    <html>
    <body>
        <script type="application/ld+json">
        {
            "contentUrl": "https://mylust.com/get_file/1/fallback.mp4"
        }
        </script>
    </body>
    </html>
    """
    played = []

    class FakeVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = MagicMock()

        def play_from_direct_link(self, link):
            played.append(link)

    monkeypatch.setattr(mylust.utils, "getHtml", lambda url, referer="": html)
    monkeypatch.setattr(mylust.utils, "VideoPlayer", FakeVideoPlayer)

    mylust.Playvid("https://mylust.com/videos/123/", "Test Video")

    assert len(played) == 1
    assert "fallback.mp4" in played[0]


def test_playvid_not_found(monkeypatch):
    html = "<html><body>No video here</body></html>"
    notifications = []

    class FakeVideoPlayer:
        def __init__(self, name, download=None):
            self.progress = MagicMock()

    monkeypatch.setattr(mylust.utils, "getHtml", lambda url, referer="": html)
    monkeypatch.setattr(mylust.utils, "VideoPlayer", FakeVideoPlayer)
    monkeypatch.setattr(mylust.utils, "notify", lambda h, m: notifications.append((h, m)))

    mylust.Playvid("https://mylust.com/videos/123/", "Test Video")

    assert len(notifications) == 1
    assert "not found" in notifications[0][0].lower()
