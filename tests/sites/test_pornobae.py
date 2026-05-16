from unittest.mock import MagicMock

from resources.lib.sites import pornobae


def test_site_is_marked_new_video_tube():
    assert pornobae.site.category == "Video Tubes"
    assert pornobae.site.is_new is True


def test_list_parses_wordpress_video_cards(monkeypatch):
    html = """
    <article class="post type-post">
        <a href="https://pornobae.com/video-one/" title="Video One">
            <div class="post-thumbnail">
                <img src="https://img.example/one.jpg" alt="Video One">
                <span class="duration">12:34</span>
            </div>
            <header class="entry-header"><span>Video One</span></header>
        </a>
    </article>
    <a class="next page-numbers" href="https://pornobae.com/page/2/">Next</a>
    """
    downloads = []
    dirs = []

    monkeypatch.setattr(pornobae.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        pornobae.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "duration": kwargs.get("duration"),
            }
        ),
    )
    monkeypatch.setattr(
        pornobae.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(pornobae.utils, "eod", lambda: None)

    pornobae.List("https://pornobae.com/")

    assert downloads == [
        {
            "name": "Video One",
            "url": "https://pornobae.com/video-one/",
            "mode": "Playvid",
            "icon": "https://img.example/one.jpg",
            "duration": "12:34",
        }
    ]
    assert dirs == [
        {
            "name": "Next Page",
            "url": "https://pornobae.com/page/2/",
            "mode": "List",
        }
    ]


def test_categories_parse_category_links(monkeypatch):
    html = """
    <ul>
        <li class="menu-item-object-category">
            <a href="https://pornobae.com/category/anal/">Anal</a>
        </li>
        <li class="menu-item-object-category">
            <a href="/category/milf/">MILF</a>
        </li>
    </ul>
    """
    dirs = []

    monkeypatch.setattr(pornobae.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        pornobae.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(pornobae.utils, "eod", lambda: None)

    pornobae.Categories("https://pornobae.com/")

    assert dirs == [
        {
            "name": "Anal",
            "url": "https://pornobae.com/category/anal/",
            "mode": "List",
        },
        {
            "name": "MILF",
            "url": "https://pornobae.com/category/milf/",
            "mode": "List",
        },
    ]


def test_search_uses_wordpress_query(monkeypatch):
    called_urls = []
    monkeypatch.setattr(pornobae, "List", lambda url: called_urls.append(url))

    pornobae.Search("https://pornobae.com/?s=", keyword="anal milf")

    assert called_urls == ["https://pornobae.com/?s=anal+milf"]


def test_playvid_resolves_video_player_iframe(monkeypatch):
    html = """
    <div class="video-player">
        <iframe src="https://tubexplayer.com/embed-abc123.html"></iframe>
    </div>
    """

    monkeypatch.setattr(pornobae.utils, "getHtml", lambda *a, **k: html)
    mock_vp_class = MagicMock()
    monkeypatch.setattr("resources.lib.utils.VideoPlayer", mock_vp_class)

    pornobae.Playvid("https://pornobae.com/video-one/", "Video One")

    mock_vp_class.return_value.play_from_link_to_resolve.assert_called_once_with(
        "https://tubexplayer.com/embed-abc123.html"
    )
