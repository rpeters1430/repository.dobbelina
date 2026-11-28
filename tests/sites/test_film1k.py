from unittest.mock import MagicMock

from resources.lib.sites import film1k


def test_site_is_marked_new_movie_site():
    assert film1k.site.category == "Movies"
    assert film1k.site.is_new is True


def test_list_parses_cards_and_pagination(monkeypatch):
    html = """
    <article class="loop-post post-84179">
        <figure class="film1k-card__media">
            <a class="film1k-card__link" href="https://www.film1k.com/sample-1993.html" aria-label="Sample Movie (1993)">
                <img src="https://img.film1k.com/video-thumbs/sample.webp" alt="Sample Movie (1993)">
            </a>
        </figure>
        <h2 class="film1k-card__title"><a href="https://www.film1k.com/sample-1993.html">Sample Movie (1993)</a></h2>
    </article>
    <div class="pagination"><a class="next" href="https://www.film1k.com/page/2">Next</a></div>
    """
    downloads = []
    dirs = []

    monkeypatch.setattr(film1k.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(
        film1k.site,
        "add_download_link",
        lambda name, url, mode, iconimage, desc="", **kwargs: downloads.append(
            {"name": name, "url": url, "mode": mode, "icon": iconimage}
        ),
    )
    monkeypatch.setattr(
        film1k.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(film1k.utils, "eod", lambda: None)

    film1k.List("https://www.film1k.com/")

    assert downloads == [
        {
            "name": "Sample Movie (1993)",
            "url": "https://www.film1k.com/sample-1993.html",
            "mode": "Playvid",
            "icon": "https://img.film1k.com/video-thumbs/sample.webp",
        }
    ]
    assert dirs == [
        {
            "name": "Next Page",
            "url": "https://www.film1k.com/page/2",
            "mode": "List",
        }
    ]


def test_categories_and_search(monkeypatch):
    cat_html = """
    <nav>
        <a href="https://www.film1k.com/category/action">Action</a>
        <a href="/category/drama">Drama</a>
    </nav>
    """
    dirs = []
    called_urls = []

    monkeypatch.setattr(film1k.utils, "getHtml", lambda *a, **k: cat_html)
    monkeypatch.setattr(
        film1k.site,
        "add_dir",
        lambda name, url, mode, iconimage="", **kwargs: dirs.append(
            {"name": name, "url": url, "mode": mode}
        ),
    )
    monkeypatch.setattr(film1k.utils, "eod", lambda: None)

    film1k.Categories("https://www.film1k.com/")
    assert dirs == [
        {"name": "Action", "url": "https://www.film1k.com/category/action", "mode": "List"},
        {"name": "Drama", "url": "https://www.film1k.com/category/drama", "mode": "List"},
    ]

    monkeypatch.setattr(film1k, "List", lambda url: called_urls.append(url))
    film1k.Search("https://www.film1k.com/?s=", "anna 2005")
    assert called_urls == ["https://www.film1k.com/?s=anna+2005"]


def test_playvid_direct_mp4_and_byse_embed(monkeypatch):
    vp = MagicMock()
    monkeypatch.setattr(film1k.utils, "VideoPlayer", lambda *a, **k: vp)

    direct_html = '<video><source src="https://cdn.film1k.com/movie.mp4"></video>'
    monkeypatch.setattr(film1k.utils, "getHtml", lambda *a, **k: direct_html)
    film1k.Playvid("https://www.film1k.com/sample.html", "Sample")
    vp.play_from_direct_link.assert_called_once_with(
        "https://cdn.film1k.com/movie.mp4|Referer=https://www.film1k.com/sample.html"
    )

    embed_html = '<video><source src="https://film1k.xyz/e/abc/movie.mp4"></video>'
    monkeypatch.setattr(film1k.utils, "getHtml", lambda *a, **k: embed_html)
    film1k.Playvid("https://www.film1k.com/sample.html", "Sample")
    vp.play_from_link_to_resolve.assert_called_once_with(
        "https://film1k.xyz/e/abc/movie.mp4"
    )
