"""
Cumination
Copyright (C) 2026 Team Cumination

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import annotations

from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "hentaihaven",
    "[COLOR hotpink]Hentai Haven[/COLOR]",
    "https://hentaihaven.xxx/",
    "hentaihaven.png",
    category="Hentai",
    is_new=True,
)


def _absolute_url(url):
    if not url:
        return ""
    return urllib_parse.urljoin(site.url, url)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Latest[/COLOR]",
        site.url + "watch/?sort=latest",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Trending[/COLOR]",
        site.url + "browse/trending/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Uncensored[/COLOR]",
        site.url + "series/uncensored/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Rule 34[/COLOR]",
        site.url + "rule34/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "watch/",
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
    for link in soup.select("a[href*='/watch/'], a[href*='/rule34/video/']"):
        img_tag = link.select_one("img")
        if not img_tag:
            continue

        video_url = _absolute_url(utils.safe_get_attr(link, "href"))
        if not video_url or video_url in seen or video_url.rstrip("/").endswith("/watch"):
            continue
        seen.add(video_url)

        thumb = _absolute_url(
            utils.safe_get_attr(img_tag, "data-src", ["src"])
        )
        title = utils.cleantext(
            utils.safe_get_attr(img_tag, "alt")
            or utils.safe_get_attr(link, "title")
            or utils.safe_get_text(link)
        )
        if title:
            site.add_download_link(title, video_url, "Playvid", thumb, title)

    next_link = soup.select_one("a[rel='next'][href], a.next[href]")
    if next_link:
        next_url = _absolute_url(utils.safe_get_attr(next_link, "href"))
        if next_url and next_url != url:
            site.add_dir("Next Page", next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
        return
    search_url = "{0}?q={1}".format(
        url.rstrip("/") + "/", urllib_parse.quote_plus(keyword.strip())
    )
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
        if media_url:
            vp.play_from_direct_link("{0}|Referer={1}".format(media_url, site.url))
            return

    vp.play_from_html(html)
