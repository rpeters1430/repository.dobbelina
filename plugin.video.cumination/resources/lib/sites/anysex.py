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


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Latest[/COLOR]",
        site.url + "latest-updates/",
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
    html, _ = utils.get_html_with_cloudflare_retry(url, referer=site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    # Generic KVS-like structure or similar tube layout
    # Looking for .item and video links
    for item in soup.select(".item"):
        link = item.select_one("a[href*='/videos/']")
        if not link:
            continue

        video_url = _absolute_url(utils.safe_get_attr(link, "href"))
        title = utils.cleantext(utils.safe_get_attr(link, "title") or utils.safe_get_text(item.select_one(".title")))
        img_tag = item.select_one("img")
        thumb = utils.safe_get_attr(img_tag, "data-original", ["src", "data-src"])

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
    html, _ = utils.get_html_with_cloudflare_retry(url, referer=site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    for item in soup.select(".list-categories .item"):
        link = item.select_one("a[href]")
        if not link:
            continue

        cat_url = _absolute_url(utils.safe_get_attr(link, "href"))
        title = utils.cleantext(utils.safe_get_text(item.select_one(".title")))
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
    # Standard search format for many tube sites
    List(site.url + "search/{}/".format(urllib_parse.quote(keyword.replace(" ", "-"))))


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html, _ = utils.get_html_with_cloudflare_retry(url, referer=site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    # Match flashvars block
    video_url = None
    flashvars_match = re.search(r"flashvars\s*=\s*({[\s\S]+?})", html, re.IGNORECASE)
    if flashvars_match:
        js_obj = flashvars_match.group(1)
        # Search for video_url inside the flashvars block
        video_url_match = re.search(r'video_url\s*:\s*["\']([^"\']+)["\']', js_obj)
        if video_url_match:
            video_url = video_url_match.group(1)
    
    if not video_url:
        # Global search for video_url pattern
        video_url_match = re.search(r'video_url\s*:\s*["\']([^"\']+)["\']', html)
        if video_url_match:
            video_url = video_url_match.group(1)

    if video_url:
        # Handle potential encoding/cleanup
        if video_url.startswith('//'):
            video_url = 'https:' + video_url
        
        # Remove any escaping
        video_url = video_url.replace('\\/', '/')
        
        vp.play_from_direct_link("{}|User-Agent={}&Referer={}".format(video_url, utils.USER_AGENT, url))
        return

    # Fallback to generic player helpers
    if "kt_player(" in html:
        vp.play_from_kt_player(html, url)
        return

    vp.play_from_html(html, url)
