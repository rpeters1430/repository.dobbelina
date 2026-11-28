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
from resources.lib.decrypters.kvsplayer import kvs_decode

site = AdultSite(
    "pornxpert",
    "[COLOR hotpink]PornXpert[/COLOR]",
    "https://www.pornxpert.com/",
    "pornxpert.png",
    category="Video Tubes",
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
        site.url + "latest-updates/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Highest Rated[/COLOR]",
        site.url + "top-rated/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Most Popular[/COLOR]",
        site.url + "most-popular/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/",
        "Search",
        site.img_search,
    )
    List(site.url + "latest-updates/")


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    seen = set()
    for item in soup.select(".list-videos .item, div.item"):
        link = item.select_one("a[href*='/video/']")
        if not link:
            continue

        video_url = _absolute_url(utils.safe_get_attr(link, "href"))
        if not video_url or video_url in seen:
            continue
        seen.add(video_url)

        img_tag = item.select_one("img")
        thumb = _absolute_url(
            utils.safe_get_attr(img_tag, "data-original", ["data-src", "src"])
        )
        title = utils.cleantext(
            utils.safe_get_attr(link, "title")
            or utils.safe_get_text(item.select_one(".title"))
            or utils.safe_get_attr(img_tag, "alt")
            or utils.safe_get_text(link)
        )
        duration = utils.safe_get_text(item.select_one(".duration"))
        if title:
            site.add_download_link(
                title, video_url, "Playvid", thumb, title, duration=duration
            )

    next_link = soup.select_one(
        ".load-more a[href], a[data-parameters][href], li.next a[href], .pagination a.next[href]"
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
    for cat in soup.select("a.item[href*='/categories/'], .list-categories a[href]"):
        cat_url = _absolute_url(utils.safe_get_attr(cat, "href"))
        if not cat_url or cat_url in seen:
            continue
        seen.add(cat_url)

        title = utils.cleantext(
            utils.safe_get_attr(cat, "title")
            or utils.safe_get_text(cat.select_one(".title"))
            or utils.safe_get_text(cat)
        )
        img_tag = cat.select_one("img")
        thumb = _absolute_url(
            utils.safe_get_attr(img_tag, "data-original", ["data-src", "src"])
        )
        if title:
            site.add_dir(title, cat_url, "List", thumb)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
        return
    query = urllib_parse.quote_plus(keyword.strip())
    search_url = "{0}?q={1}".format(url.rstrip("/") + "/", query)
    List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    html = utils.getHtml(url, site.url)
    if not html:
        vp.progress.close()
        return

    license_match = re.search(r"license_code:\s*'([^']+)'", html)
    if license_match:
        license_code = license_match.group(1)
        for key in ("video_alt_url", "video_url"):
            match = re.search(r"{0}:\s*'([^']+)'".format(key), html)
            if not match:
                continue
            stream_url = match.group(1)
            if stream_url.startswith("function/"):
                stream_url = kvs_decode(stream_url, license_code)
            if stream_url and "redirect_cs.php" not in stream_url:
                vp.play_from_direct_link(
                    "{0}|Referer={1}".format(stream_url, site.url)
                )
                return

    vp.play_from_kt_player(html, url)
