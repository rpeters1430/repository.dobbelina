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
    "analdin",
    "[COLOR hotpink]Analdin[/COLOR]",
    "https://www.analdin.com/",
    "analdin.png",
    category="Video Tubes",
)


def _absolute_url(url):
    if not url:
        return ""
    return urllib_parse.urljoin(site.url, url)


def _normalize_listing_url(url):
    if not url:
        return site.url + "latest-updates/"
    if url.rstrip("/") == site.url.rstrip("/"):
        return site.url + "latest-updates/"
    if url.rstrip("/") == site.url.rstrip("/") + "/videos":
        return site.url + "latest-updates/"
    return url


def _extract_next_page(soup):
    next_link = soup.select_one(".pagination li.next a[href], .pagination li a[href]")
    if next_link:
        href = utils.safe_get_attr(next_link, "href")
        if href and href != "#search":
            return _absolute_url(href)
    return ""


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Latest[/COLOR]",
        site.url + "latest-updates/",
        "List",
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
    url = _normalize_listing_url(url)
    try:
        html = utils.getHtml(url, site.url)
    except Exception as e:
        utils.kodilog("@@@@Cumination: failure in analdin: {}".format(e))
        utils.notify(msg="List blocked/challenged in harness")
        utils.eod()
        return
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    added = 0
    seen_urls = set()
    items = soup.select(
        ".list-videos .item, .list-videos .item-video, .list-videos .video-item, .item"
    )
    for item in items:
        link = item.select_one("a.popup-video-link[href]") or item.select_one("a[href]")
        if not link:
            continue

        video_url = _absolute_url(utils.safe_get_attr(link, "href"))
        if not video_url or "/videos/" not in video_url or video_url in seen_urls:
            continue
        seen_urls.add(video_url)

        title = utils.cleantext(utils.safe_get_text(item.select_one(".title")))
        if not title:
            title = utils.cleantext(utils.safe_get_attr(link, "title", ["data-title"]))

        img_tag = item.select_one("img")
        thumb = utils.safe_get_attr(
            img_tag, "data-original", ["data-src", "src"]
        ) or utils.safe_get_attr(link, "thumb", ["data-preview"])
        if not title:
            title = utils.cleantext(utils.safe_get_attr(img_tag, "alt"))
        if not title:
            title = utils.cleantext(utils.safe_get_text(link))

        if title and video_url:
            site.add_download_link(title, video_url, "Playvid", thumb, title)
            added += 1

    if added == 0:
        for link in soup.select(
            ".list-videos a[href*='/videos/'], .item a[href*='/videos/']"
        ):
            video_url = _absolute_url(utils.safe_get_attr(link, "href"))
            if not video_url or video_url in seen_urls:
                continue
            seen_urls.add(video_url)

            img_tag = link.select_one("img")
            title = (
                utils.cleantext(utils.safe_get_attr(link, "title", ["data-title"]))
                or utils.cleantext(utils.safe_get_attr(img_tag, "alt"))
                or utils.cleantext(utils.safe_get_text(link))
            )
            thumb = utils.safe_get_attr(
                img_tag, "data-original", ["data-src", "src"]
            ) or utils.safe_get_attr(link, "thumb", ["data-preview"])
            if title:
                site.add_download_link(title, video_url, "Playvid", thumb, title)
                added += 1

    if added == 0 and isinstance(html, str):
        for href, title in re.findall(
            r'"url"\s*:\s*"([^"]+/videos/[^"]+)"[^{}]*?"name"\s*:\s*"([^"]+)"',
            html,
            re.IGNORECASE | re.DOTALL,
        ):
            video_url = _absolute_url(href.replace("\\/", "/"))
            if not video_url or video_url in seen_urls:
                continue
            seen_urls.add(video_url)
            site.add_download_link(utils.cleantext(title), video_url, "Playvid", "", title)
            added += 1

    next_url = _extract_next_page(soup)
    if next_url:
        site.add_dir("Next Page", next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
        return
    List(site.url + "search/{}/".format(urllib_parse.quote(keyword)))


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    match = re.search(r"video_alt_url:\s*'([^']+)'", html, re.IGNORECASE)
    if not match:
        match = re.search(r"video_url:\s*'([^']+)'", html, re.IGNORECASE)

    if match:
        vp.play_from_direct_link(
            "{}|User-Agent={}&Referer={}".format(match.group(1), utils.USER_AGENT, url)
        )
        return

    if "kt_player(" in html:
        vp.play_from_kt_player(html, url)
        return

    vp.play_from_html(html, url)
