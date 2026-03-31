"""
Cumination
Copyright (C) 2026 Team Cumination

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import annotations

from collections import OrderedDict
import re
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "anysex",
    "[COLOR hotpink]AnySex.com[/COLOR]",
    "https://anysex.com/",
    "anysex.png",
    "anysex",
)


def _absolute_url(url):
    if not url:
        return ""
    return urllib_parse.urljoin(site.url, url)


def _latest_url():
    return site.url + "videos/new/"


def _categories_url():
    return site.url + "videos/categories/"


def _search_url():
    return site.url + "search/?q="


def _extract_quality(label):
    match = re.search(r"(\d{3,4})p", label or "", re.IGNORECASE)
    return int(match.group(1)) if match else 0


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Latest[/COLOR]",
        _latest_url(),
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        _categories_url(),
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        _search_url(),
        "Search",
        site.img_search,
    )
    List(_latest_url())


@site.register()
def List(url):
    html, _ = utils.get_html_with_cloudflare_retry(
        url, referer=site.url, retry_on_empty=True
    )
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    item_selectors = (
        ".list-videos .item, "
        "#list_videos_custom_videos_list_items .item, "
        ".list-videos.grid-default .item, "
        ".item[data-video-id]"
    )
    for item in soup.select(item_selectors):
        link = item.select_one("a[href*='/video/'], a[href*='/videos/']")
        if not link:
            continue

        video_url = _absolute_url(utils.safe_get_attr(link, "href"))
        title = utils.cleantext(
            utils.safe_get_attr(link, "title")
            or utils.safe_get_text(item.select_one(".title"))
            or utils.safe_get_attr(item.select_one("img"), "alt")
        )
        img_tag = item.select_one("img")
        thumb = utils.safe_get_attr(
            img_tag, "data-original", ["data-jpg", "src", "data-src"]
        )

        if title and video_url:
            site.add_download_link(title, video_url, "Playvid", thumb, title)

    # Pagination
    next_link = soup.select_one('link[rel="next"], a[rel="next"], .pagination li.next a')
    if next_link:
        next_url = _absolute_url(utils.safe_get_attr(next_link, "href"))
        if next_url:
            site.add_dir("Next Page", next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Categories(url):
    html, _ = utils.get_html_with_cloudflare_retry(
        url, referer=site.url, retry_on_empty=True
    )
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    for item in soup.select(".list-categories .item, .main-menu a[href*='/videos/categories/']"):
        link = item if getattr(item, "name", "") == "a" else item.select_one("a[href]")
        if not link:
            continue

        cat_url = _absolute_url(utils.safe_get_attr(link, "href"))
        title = utils.cleantext(
            utils.safe_get_text(item.select_one(".title"))
            or utils.safe_get_text(link)
        )
        count = utils.safe_get_text(item.select_one(".videos"))

        display_name = title
        if count:
            display_name += " [COLOR yellow]({})[/COLOR]".format(count)

        if title and cat_url:
            site.add_dir(display_name, cat_url, "List", site.img_cat)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
        return
    base_url = url if "q=" in url else _search_url()
    List(base_url + urllib_parse.quote_plus(keyword))


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html, _ = utils.get_html_with_cloudflare_retry(
        url, referer=site.url, retry_on_empty=True
    )
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    soup = utils.parse_html(html)
    sources = OrderedDict()

    for source in soup.select("video source[src]"):
        source_url = utils.safe_get_attr(source, "src")
        if not source_url:
            continue
        label = (
            utils.safe_get_attr(source, "title")
            or utils.safe_get_attr(source, "label")
            or utils.safe_get_attr(source, "data-quality")
            or source.get("res")
            or "direct"
        )
        sources[label] = source_url.replace("\\/", "/")

    if sources:
        best_label = max(sources, key=_extract_quality)
        video_url = sources[best_label]
        if video_url.startswith("//"):
            video_url = "https:" + video_url
        vp.play_from_direct_link(
            "{}|User-Agent={}&Referer={}".format(video_url, utils.USER_AGENT, url)
        )
        return

    video_url = None
    flashvars_match = re.search(r"flashvars\s*=\s*({[\s\S]+?})", html, re.IGNORECASE)
    if flashvars_match:
        js_obj = flashvars_match.group(1)
        video_url_match = re.search(r'video_url\s*:\s*["\']([^"\']+)["\']', js_obj)
        if video_url_match:
            video_url = video_url_match.group(1)

    if not video_url:
        video_url_match = re.search(r'video_url\s*:\s*["\']([^"\']+)["\']', html)
        if video_url_match:
            video_url = video_url_match.group(1)

    if video_url:
        if video_url.startswith('//'):
            video_url = 'https:' + video_url
        video_url = video_url.replace('\\/', '/')

        vp.play_from_direct_link("{}|User-Agent={}&Referer={}".format(video_url, utils.USER_AGENT, url))
        return

    # Fallback to generic player helpers
    if "kt_player(" in html:
        vp.play_from_kt_player(html, url)
        return

    vp.play_from_html(html, url)
