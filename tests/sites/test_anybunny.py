from resources.lib.sites import anybunny
from tests.conftest import read_fixture


class _Recorder:
    def __init__(self):
        self.downloads = []
        self.dirs = []

    def add_download(self, name, url, mode, iconimage, desc="", *args, **kwargs):
        self.downloads.append(
            {
                "name": name,
                "url": url,
                "mode": anybunny.site.get_full_mode(mode),
                "icon": iconimage,
            }
        )

    def add_dir(self, name, url, mode, *args, **kwargs):
        self.dirs.append(
            {
                "name": name,
                "url": url,
                "mode": anybunny.site.get_full_mode(mode),
            }
        )


def test_list_populates_download_links(monkeypatch):
    """List() extracts video items and pagination from a category page."""
    recorder = _Recorder()

    def fake_cf_get_html(url, *args, **kwargs):
        assert url == "https://anybunny.org/top/Indian"
        return read_fixture("sites/anybunny/listing.html"), False

    monkeypatch.setattr(anybunny.utils, "get_html_with_cloudflare_retry", fake_cf_get_html)

    monkeypatch.setattr(anybunny.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(anybunny.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(anybunny.utils, "eod", lambda *args, **kwargs: None)

    anybunny.List("https://anybunny.org/top/Indian")

    assert recorder.downloads == [
        {
            "name": "First Video Title",
            "url": "https://anybunny.org/too/111-first_video_title",
            "mode": "anybunny.Playvid",
            "icon": "https://cdn.anybunny.org/thumb-first.jpg",
        },
        {
            "name": "Second Video Title",
            "url": "https://anybunny.org/too/222-second_video_title",
            "mode": "anybunny.Playvid",
            "icon": "https://cdn.anybunny.org/thumb-second.jpg",
        },
    ]

    assert recorder.dirs == [
        {
            "name": "Next Page",
            "url": "https://anybunny.org/top/Indian?p=2",
            "mode": "anybunny.List",
        }
    ]


def test_list_filters_out_category_links(monkeypatch):
    """List() skips a.nuyrfe items pointing to /top/ (categories, not videos)."""
    recorder = _Recorder()

    monkeypatch.setattr(
        anybunny.utils,
        "get_html_with_cloudflare_retry",
        lambda url, *args, **kwargs: (read_fixture("sites/anybunny/listing.html"), False),
    )

    monkeypatch.setattr(anybunny.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(anybunny.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(anybunny.utils, "eod", lambda *args, **kwargs: None)

    anybunny.List("https://anybunny.org/top/Indian")

    for dl in recorder.downloads:
        assert "/too/" in dl["url"], f"Expected /too/ in URL, got {dl['url']}"


def test_search_results_list_videos(monkeypatch):
    """Search results page produces video downloads with no pagination."""
    recorder = _Recorder()

    monkeypatch.setattr(
        anybunny.utils,
        "get_html_with_cloudflare_retry",
        lambda url, *args, **kwargs: (read_fixture("sites/anybunny/search.html"), False),
    )

    monkeypatch.setattr(anybunny.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(anybunny.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(anybunny.utils, "eod", lambda *args, **kwargs: None)

    anybunny.List("https://anybunny.org/top/blonde")

    assert [d["name"] for d in recorder.downloads] == [
        "Search Result One",
        "Search Result Two",
    ]
    assert recorder.dirs == []


def test_categories2_extracts_category_links(monkeypatch):
    """Categories2() lists categories from the root page (a.nuyrfe -> /top/)."""
    recorder = _Recorder()

    monkeypatch.setattr(
        anybunny.utils,
        "get_html_with_cloudflare_retry",
        lambda url, *args, **kwargs: (read_fixture("sites/anybunny/categories.html"), False),
    )

    monkeypatch.setattr(anybunny.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(anybunny.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(anybunny.utils, "eod", lambda *args, **kwargs: None)

    anybunny.Categories2("https://anybunny.org/")

    cat_names = [d["name"] for d in recorder.dirs]
    assert "Indian" in cat_names
    assert "Big Tits" in cat_names
    assert not any(d["url"].rstrip("/").endswith("/top") for d in recorder.dirs)


def test_playvid_extracts_mp4_from_file_param(monkeypatch):
    """Playvid() extracts an MP4 URL from a Playerjs file: parameter."""
    captured = {}

    class _DummyVP:
        def __init__(self, name, download=False, **kwargs):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_direct_link(self, url):
            captured["direct_url"] = url

    monkeypatch.setattr(anybunny.utils, "VideoPlayer", _DummyVP)

    playerjs_html = (
        '<html><script>'
        'playerjs({id:"player", file:"https://anybunny.org/video/hls/123/abc/ts/video.m3u8?jtry=1'
        ':cast:https://anybunny.org/video/hls/123/abc/ts/video.m3u8?jtry=1'
        ' or https://anybunny.org/video/mp4/123/abc/ts/video.mp4'
        ':cast:https://anybunny.org/video/mp4/123/abc/ts/video.mp4"});'
        '</script></html>'
    )

    def mock_get_html(url, *args, **kwargs):
        return playerjs_html, None

    monkeypatch.setattr(anybunny.utils, "get_html_with_cloudflare_retry", mock_get_html)

    anybunny.Playvid("https://anybunny.org/too/123-video", "Example")

    assert captured["direct_url"].split("|")[0] == "https://anybunny.org/video/mp4/123/abc/ts/video.mp4"


def test_playvid_extracts_html5_source(monkeypatch):
    """Playvid() extracts modern HTML5 video sources."""
    captured = {}

    class _DummyVP:
        def __init__(self, name, download=False, **kwargs):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_direct_link(self, url):
            captured["direct_url"] = url

    monkeypatch.setattr(anybunny.utils, "VideoPlayer", _DummyVP)

    video_html = (
        '<html><body>'
        '<video id="tube-mov">'
        '<source src="https://mov.anybunny.tv/key=abc,end=123/video.mp4" type="video/mp4"/>'
        '</video>'
        '</body></html>'
    )

    monkeypatch.setattr(anybunny.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (video_html, None))

    anybunny.Playvid("https://anybunny.tv/movie/123/test.html", "Example")

    assert captured["direct_url"].split("|")[0] == "https://mov.anybunny.tv/key=abc,end=123/video.mp4"


def test_playvid_uses_iframe_fallback(monkeypatch):
    """Playvid() falls back to fetching an iframe when no file: param is present."""
    captured = {}

    class _DummyVP:
        def __init__(self, name, download=False, **kwargs):
            self.progress = type("P", (), {"update": lambda *a, **k: None})()

        def play_from_direct_link(self, url):
            captured["direct_url"] = url

    monkeypatch.setattr(anybunny.utils, "VideoPlayer", _DummyVP)

    def mock_get_html(url, *args, **kwargs):
        if "/iframe/" in url:
            return '<html>var video = "https://stream1.anybunny.org/vid.mp4";</html>', None
        return '<html><iframe src="http://anybunny.org/iframe/123"></iframe></html>', None

    monkeypatch.setattr(anybunny.utils, "get_html_with_cloudflare_retry", mock_get_html)

    anybunny.Playvid("http://anybunny.org/too/123-video", "Example")

    assert captured["direct_url"].split("|")[0] == "https://stream1.anybunny.org/vid.mp4"


def test_main_populates_directories(monkeypatch):
    """Main() creates top-level directories and loads a default video feed."""
    recorder = _Recorder()
    list_calls = []

    monkeypatch.setattr(anybunny.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(anybunny, "List", lambda url: list_calls.append(url))
    monkeypatch.setattr(anybunny.utils, "eod", lambda *args, **kwargs: None)

    anybunny.Main()

    assert len(recorder.dirs) == 4
    assert any("Latest" in d["name"] for d in recorder.dirs)
    assert any("Top Rated" in d["name"] for d in recorder.dirs)
    assert any("Categories" in d["name"] for d in recorder.dirs)
    assert any("Search" in d["name"] for d in recorder.dirs)
    assert list_calls == [anybunny.DEFAULT_LIST_URL]


def test_categories2_parses_search_tags(monkeypatch):
    """Categories2() parses popular search/tag links from the homepage."""
    recorder = _Recorder()
    sample_html = """
    <html><body>
        <a href="/search/interracial-orgy.html">Interracial Orgy</a>
        <a href="/search/milf-blowjob.html">Milf Blowjob</a>
        <a href="/movie/123/video.html">Ignore Video Link</a>
    </body></html>
    """
    monkeypatch.setattr(anybunny.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (sample_html, None))
    monkeypatch.setattr(anybunny.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(anybunny.utils, "eod", lambda *a, **k: None)

    anybunny.Categories2("https://anybunny.tv/")

    assert len(recorder.dirs) == 2
    names = [d["name"] for d in recorder.dirs]
    assert "Interracial Orgy" in names
    assert "Milf Blowjob" in names


def test_list_numeric_pagination(monkeypatch):
    """List() adds numeric Next Page link when >= 20 items are found."""
    recorder = _Recorder()
    items_html = "".join([
        f'<li class="thumb"><a class="thumb_img_wrap" href="/movie/{i}/test.html"><span class="thumb_title">Video {i}</span></a></li>'
        for i in range(25)
    ])
    html = f"<html><body><ul>{items_html}</ul></body></html>"

    monkeypatch.setattr(anybunny.utils, "get_html_with_cloudflare_retry", lambda *a, **k: (html, None))
    monkeypatch.setattr(anybunny.site, "add_download_link", recorder.add_download)
    monkeypatch.setattr(anybunny.site, "add_dir", recorder.add_dir)
    monkeypatch.setattr(anybunny.utils, "eod", lambda *a, **k: None)

    anybunny.List("https://anybunny.tv/latest/")

    assert len(recorder.downloads) == 25
    assert len(recorder.dirs) == 1
    assert "Next Page" in recorder.dirs[0]["name"]
    assert "page=2" in recorder.dirs[0]["url"]

