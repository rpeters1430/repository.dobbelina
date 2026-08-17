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
    "erothots",
    "[COLOR hotpink]EroThots[/COLOR]",
    "https://erothots.co/",
    "erothots.png",
    category="Amateur & Social",
    is_new=True,
)


def _absolute_url(url):
    if not url:
        return ""
    return urllib_parse.urljoin(site.url, url)


def _clean_title(value):
    title = utils.cleantext(value or "")
    return title.strip()


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Hot Leaks[/COLOR]", site.url + "videos/hot", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]New Leaks[/COLOR]", site.url + "videos/new", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]OnlyFans Leaks[/COLOR]", site.url + "onlyfans-leaks", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Porn Tube[/COLOR]", site.url + "free-porn", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search)
    List(site.url + "videos")


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    seen = set()
    for a in soup.select("a.video, a.video-media, a[href*='/video/']"):
        video_url = _absolute_url(utils.safe_get_attr(a, "href"))
        if not video_url or "/video/" not in video_url or video_url in seen or video_url.rstrip("/") == site.url.rstrip("/") + "videos":
            continue
        seen.add(video_url)

        img = a.select_one("img")
        thumb = utils.safe_get_attr(img, "data-src", ["src"])
        title = (
            _clean_title(utils.safe_get_attr(img, "alt"))
            or _clean_title(utils.safe_get_attr(a, "title"))
            or _clean_title(utils.safe_get_text(a))
        )
        duration = utils.safe_get_text(a.select_one(".caption, .duration, .time"))
        duration = duration.replace("\n", " ").strip()

        if title:
            site.add_download_link(
                title, video_url, "Playvid", thumb, title, duration=duration
            )

    # Pagination: check for load more / next link or calculate p+1
    next_link = soup.select_one("a[href*='?p='], a[href*='&p='], a.next[href], a.pagination-next[href]")
    if next_link:
        next_url = _absolute_url(utils.safe_get_attr(next_link, "href"))
        if next_url and next_url != url:
            site.add_dir("Next Page", next_url, "List", site.img_next)
    else:
        # Check if current URL has ?p= or &p=, or if we have at least 15 items on page
        if len(seen) >= 15:
            p_match = re.search(r"[?&]p=(\d+)", url)
            if p_match:
                curr_p = int(p_match.group(1))
                next_p = curr_p + 1
                next_url = re.sub(r"([?&]p=)\d+", r"\g<1>" + str(next_p), url)
            else:
                sep = "&" if "?" in url else "?"
                next_url = f"{url}{sep}p=2"
            site.add_dir("Next Page", next_url, "List", site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
        return
    search_url = site.url + "search/?q=" + urllib_parse.quote_plus(keyword) + "&type=videos"
    List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    soup = utils.parse_html(html)
    video_source = soup.select_one("video.v-player source[src], video source[src], video[src]")
    if video_source:
        src = utils.safe_get_attr(video_source, "src")
        if src:
            video_stream = _absolute_url(src)
            vp.play_from_direct_link(video_stream)
            return

    vp.play_from_html(html, url)
