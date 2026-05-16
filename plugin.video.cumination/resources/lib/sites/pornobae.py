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
    "pornobae",
    "[COLOR hotpink]PornoBae[/COLOR]",
    "https://pornobae.com/",
    "pornobae.png",
    category="Video Tubes",
    is_new=True,
)


def _absolute_url(url):
    if not url:
        return ""
    return urllib_parse.urljoin(site.url, url)


def _clean_title(value):
    title = utils.cleantext(value or "")
    return title.replace("&#8211;", "-").strip()


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Latest[/COLOR]", site.url, "List", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "?s=",
        "Search",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url,
        "Categories",
        site.img_cat,
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
    for item in soup.select("article.post, article.type-post, .thumb-block"):
        link = item.select_one("a[href][title]") or item.select_one("a[href]")
        if not link:
            continue

        video_url = _absolute_url(utils.safe_get_attr(link, "href"))
        if not video_url or video_url in seen or video_url.rstrip("/") == site.url.rstrip("/"):
            continue
        seen.add(video_url)

        img_tag = item.select_one("img")
        thumb = utils.safe_get_attr(img_tag, "data-src", ["src"])
        title = (
            _clean_title(utils.safe_get_attr(link, "title"))
            or _clean_title(utils.safe_get_text(item.select_one(".entry-header span")))
            or _clean_title(utils.safe_get_attr(img_tag, "alt"))
            or _clean_title(utils.safe_get_text(link))
        )
        duration = utils.safe_get_text(item.select_one(".duration"))
        duration = duration.replace("\n", " ").strip()
        if title:
            site.add_download_link(
                title, video_url, "Playvid", thumb, title, duration=duration
            )

    next_link = soup.select_one("a.next.page-numbers[href], .pagination a.next[href]")
    if next_link:
        next_url = _absolute_url(utils.safe_get_attr(next_link, "href"))
        if next_url:
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
    for link in soup.select(
        "a[href*='/category/'], .menu-item-object-category a[href]"
    ):
        cat_url = _absolute_url(utils.safe_get_attr(link, "href"))
        if not cat_url or cat_url in seen:
            continue
        seen.add(cat_url)
        title = _clean_title(utils.safe_get_text(link))
        if title:
            site.add_dir(title, cat_url, "List", site.img_cat)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
        return
    List(site.url + "?s=" + urllib_parse.quote_plus(keyword))


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    soup = utils.parse_html(html)
    iframe = soup.select_one(".video-player iframe[src], iframe[src*='tubexplayer']")
    if iframe:
        iframe_url = _absolute_url(utils.safe_get_attr(iframe, "src"))
        if iframe_url:
            vp.play_from_link_to_resolve(iframe_url)
            return

    vp.play_from_html(html, url)
