"""
Cumination
Copyright (C) 2026 Team Cumination

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import annotations

import base64
import re
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "pornmd",
    "[COLOR hotpink]PornMD[/COLOR]",
    "https://www.pornmd.com/",
    "pornmd.png",
    category="Video Tubes",
)


def _absolute_url(url):
    if not url:
        return ""
    return urllib_parse.urljoin(site.url, url)


def _extract_url_from_redirect(href):
    if not href or "/out/?l=" not in href:
        return ""
    try:
        # Extract the base64 part
        parts = href.split("/out/?l=")
        if len(parts) < 2:
            return ""
        l_val = parts[1].split("&")[0]
        # Decode the base64 value
        decoded = base64.b64decode(urllib_parse.unquote(l_val)).decode('utf-8', errors='ignore')
        match = re.search(r'(https?://[^\s\x00-\x1f\x7f-\xff]+)', decoded)
        if match:
            return match.group(1)
    except Exception as e:
        utils.kodilog("@@@@Cumination: pornmd redirect decode error: {}".format(e))
    return ""


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Popular[/COLOR]",
        site.url + "popular",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]New[/COLOR]",
        site.url + "new",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Top Rated[/COLOR]",
        site.url + "rating",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "searching/",
        "Search",
        site.img_search,
    )
    List(site.url + "new")


@site.register()
def List(url):
    try:
        html, _ = utils.get_html_with_cloudflare_retry(url, site.url)
    except Exception as e:
        utils.kodilog("@@@@Cumination: failure in pornmd: {}".format(e))
        utils.notify(msg="List blocked/challenged in harness")
        utils.eod()
        return
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    added = 0

    cards = soup.select(".card")
    for card in cards:
        link_el = card.select_one("a.item-title[href]")
        if not link_el:
            link_el = card.select_one("a[href*='/out/?l=']")
        if not link_el:
            continue

        href = link_el.get("href")
        title = link_el.get("title") or link_el.get_text(strip=True)
        if title == "No video available":
            title_span = link_el.select_one("span:not(.hidden)")
            if title_span:
                title = title_span.get_text(strip=True)

        title = utils.cleantext(title)
        if not title:
            continue

        img_el = card.select_one("img.item-image")
        thumb = img_el.get("src") if img_el else ""
        if thumb and thumb.startswith("/"):
            thumb = _absolute_url(thumb)

        duration_el = card.select_one("span.badge")
        duration = utils.cleantext(duration_el.get_text(strip=True)) if duration_el else ""

        video_url = _extract_url_from_redirect(href)
        if not video_url:
            video_url = _absolute_url(href)

        if title and video_url:
            site.add_download_link(title, video_url, "Playvid", thumb, title, duration=duration)
            added += 1

    next_link = soup.select_one("a[aria-label='Next page'][href]")
    if next_link:
        next_url = _absolute_url(next_link.get("href"))
        if next_url:
            site.add_dir("Next Page", next_url, "List", site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
        return
    List(site.url + "searching/?queryString={}".format(urllib_parse.quote(keyword)))


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    # Since PornMD is a search engine, we resolved to the actual target site in List step.
    # Therefore, url is already the resolved target URL (e.g. Eporner, FapHouse, etc.).
    # We can pass it directly to the resolver.
    vp.play_from_link_to_resolve(url)
