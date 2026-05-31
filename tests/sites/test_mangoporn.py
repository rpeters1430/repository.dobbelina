from unittest.mock import MagicMock

from resources.lib.sites import mangoporn


def test_site_is_marked_new_specialty():
    assert mangoporn.site.category == "Specialty"
    assert mangoporn.site.is_new is True


def test_list_parses_movie_cards(monkeypatch):
    html = """
    <article class="item movies">
        <div class="poster">
            <img
                src="https://mangoporn.net/blank.gif"
                data-wpfc-original-src="https://img.example/movie.jpg"
                alt="Watch Movie One Porn Online Free"
            />
            <span class="duration">1 hrs. 43 mins.</span>
            <a href="https://mangoporn.net/movies/movie-one/"><div class="see play4"></div></a>
        </div>
        <div class="data">
            <h3><a href="https://mangoporn.net/movies/movie-one/">Movie One</a></h3>
        </div>
    </article>
    <div class="pagination"><a class="next" href="https://mangoporn.net/page/2/">Next</a></div>
    """
    downloads = []
    dirs = []

    monkeypatch.setattr(mangoporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(mangoporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        mangoporn.site,
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
        mangoporn.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )

    mangoporn.List("https://mangoporn.net/")

    assert downloads == [
        {
            "name": "Movie One",
            "url": "https://mangoporn.net/movies/movie-one/",
            "mode": "Playvid",
            "icon": "https://img.example/movie.jpg",
            "duration": "1 hrs. 43 mins.",
        }
    ]
    assert dirs == [
        {
            "name": "Next Page",
            "url": "https://mangoporn.net/page/2/",
            "mode": "List",
        }
    ]


def test_categories_parse_genre_links(monkeypatch):
    html = """
    <nav>
        <a href="https://mangoporn.net/genre/anal/">Anal</a>
        <a href="/genre/asian/">Asian</a>
        <a href="#">Genres</a>
    </nav>
    """
    dirs = []

    monkeypatch.setattr(mangoporn.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(mangoporn.utils, "eod", lambda: None)
    monkeypatch.setattr(
        mangoporn.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )

    mangoporn.Categories("https://mangoporn.net/")

    assert dirs == [
        {"name": "Anal", "url": "https://mangoporn.net/genre/anal/", "mode": "List"},
        {"name": "Asian", "url": "https://mangoporn.net/genre/asian/", "mode": "List"},
    ]


def test_search_uses_wordpress_query(monkeypatch):
    called_urls = []
    monkeypatch.setattr(mangoporn, "List", lambda url: called_urls.append(url))

    mangoporn.Search("https://mangoporn.net/?s=", keyword="anal movie")

    assert called_urls == ["https://mangoporn.net/?s=anal+movie"]


def test_playvid_uses_host_link_list(monkeypatch):
    html = """
    <ul id="playeroptionsul">
        <li data-fl-url="https://doodstream.com/d/abc123">
            <a href="https://doodstream.com/e/abc123">DoodStream</a>
        </li>
        <li data-fl-source="https://nitroflare.com/view/file/movie.mp4"></li>
    </ul>
    """

    monkeypatch.setattr(mangoporn.utils, "getHtml", lambda *a, **k: html)
    mock_vp_class = MagicMock()
    monkeypatch.setattr("resources.lib.utils.VideoPlayer", mock_vp_class)

    mangoporn.Playvid("https://mangoporn.net/movies/movie-one/", "Movie One")

    mock_vp_class.return_value.play_from_link_list.assert_called_once_with(
        [
            "https://doodstream.com/d/abc123",
            "https://doodstream.com/e/abc123",
            "https://nitroflare.com/view/file/movie.mp4",
        ]
    )
