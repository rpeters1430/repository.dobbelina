"""
Cumination
Copyright (C) 2026 Team Cumination

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import annotations

import re

from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "film1k",
    "[COLOR hotpink]Film1k[/COLOR]",
    "https://www.film1k.com/",
    "film1k.png",
    category="Movies",
    is_new=True,
)


def _absolute_url(url):
    if not url:
        return ""
    return urllib_parse.urljoin(site.url, url)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Latest[/COLOR]", site.url, "List", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url,
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "?s=",
        "Search",
        site.img_search,
    )
    List(site.url)


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    seen = set()
    for item in soup.select("article.loop-post, article.post"):
        link = item.select_one("a.film1k-card__link[href], .film1k-card__title a[href], a[href]")
        if not link:
            continue

        video_url = _absolute_url(utils.safe_get_attr(link, "href"))
        if not video_url or video_url in seen or video_url.rstrip("/") == site.url.rstrip("/"):
            continue
        seen.add(video_url)

        img_tag = item.select_one("img")
        thumb = _absolute_url(
            utils.safe_get_attr(img_tag, "data-src", ["src"])
        )
        title = utils.cleantext(
            utils.safe_get_text(item.select_one(".film1k-card__title"))
            or utils.safe_get_attr(link, "aria-label")
            or utils.safe_get_attr(link, "title")
            or utils.safe_get_attr(img_tag, "alt")
            or utils.safe_get_text(link)
        )
        if title:
            site.add_download_link(title, video_url, "Playvid", thumb, title)

    next_link = soup.select_one(
        ".pagination a.next[href], .nav-links a.next[href], a.next.page-numbers[href]"
    )
    if next_link:
        next_url = _absolute_url(utils.safe_get_attr(next_link, "href"))
        if next_url and next_url != url:
            site.add_dir("Next Page", next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    seen = set()
    for link in soup.select("nav a[href*='/category/'], .menu a[href*='/category/']"):
        cat_url = _absolute_url(utils.safe_get_attr(link, "href"))
        if not cat_url or cat_url in seen:
            continue
        seen.add(cat_url)
        title = utils.cleantext(utils.safe_get_text(link))
        if title:
            site.add_dir(title, cat_url, "List", site.img_cat)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
        return
    search_url = url + urllib_parse.quote_plus(keyword.strip())
    List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    html = utils.getHtml(url, site.url)
    if not html:
        vp.progress.close()
        return

    soup = utils.parse_html(html)
    for src_tag in soup.select("video source[src], video[src]"):
        media_url = _absolute_url(utils.safe_get_attr(src_tag, "src"))
        if not media_url:
            continue
        parsed = urllib_parse.urlparse(media_url)
        if "/e/" in parsed.path:
            match = re.search(r"/e/([0-9a-zA-Z]+)", parsed.path)
            if match:
                try:
                    from resolveurl.plugins.byse import ByseResolver

                    resolved = ByseResolver().get_media_url(parsed.netloc, match.group(1))
                    if resolved:
                        vp.play_from_direct_link(resolved)
                        return
                except Exception:
                    pass
            vp.play_from_link_to_resolve(media_url)
            return
        if any(ext in parsed.path.lower() for ext in (".mp4", ".m3u8")) and "abyssplayer.com" not in parsed.netloc.lower():
            vp.play_from_direct_link("{0}|Referer={1}".format(media_url, url))
            return
        vp.play_from_link_to_resolve(media_url)
        return

    for iframe in soup.select("iframe[src]"):
        iframe_url = utils.safe_get_attr(iframe, "src")
        if iframe_url and iframe_url != "about:blank":
            vp.play_from_link_to_resolve(_absolute_url(iframe_url))
            return

    vp.play_from_html(html)
