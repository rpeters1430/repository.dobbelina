"""
Cumination
Copyright (C) 2026 Team Cumination

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import re
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.sites.soup_spec import SoupSiteSpec

site = AdultSite(
    "jizzbunker",
    "[COLOR hotpink]JizzBunker[/COLOR]",
    "https://jizzbunker.com/",
    "jizzbunker.png",
    "jizzbunker",
    category="Video Tubes",
    requires_flaresolverr=True,
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": "a.video-card",
        "url": {"attr": "href"},
        "title": {"selector": ".video-card__title", "text": True, "clean": True},
        "thumbnail": {
            "selector": ".video-card__thumb img",
            "attr": "src",
        },
        "duration": {"selector": ".video-card__duration", "text": True},
        "pagination": {
            "selector": ".pagination a",
            "text_matches": ["next", "→", ">"],
            "attr": "href",
            "mode": "List",
        },
    }
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Trending[/COLOR]",
        site.url + "straight/trending",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Popular[/COLOR]",
        site.url + "straight/popular1",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Newest[/COLOR]",
        site.url + "newest",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "channels",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search?query=",
        "Search",
        site.img_search,
    )
    List(site.url + "straight/trending")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    VIDEO_LIST_SPEC.run(site, soup, base_url=url)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = site.url + "search?query=" + urllib_parse.quote_plus(keyword)
        List(search_url)


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    # Categories are in a grid of links
    cat_items = soup.select("a.category-card, a[href*='/category/']")

    entries = []
    for anchor in cat_items:
        href = utils.safe_get_attr(anchor, "href")
        if not href:
            continue

        name = utils.safe_get_text(anchor.select_one(".category-card__title")) or utils.safe_get_text(anchor)
        if not name:
            name = utils.safe_get_attr(anchor, "title")
        if not name:
            continue

        img_tag = anchor.select_one("img")
        img = utils.safe_get_attr(img_tag, "src")

        entries.append((name, urllib_parse.urljoin(site.url, href), img))

    for name, cat_url, img in sorted(entries):
        site.add_dir(name, cat_url, "List", img)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    # Check for direct MP4 links or quality sources in script
    # Look for video_url or similar in scripts
    match = re.search(r"video_url\s*[:=]\s*[\"']([^\"']+)[\"']", html)
    if match:
        vp.play_from_direct_link(match.group(1).replace("\\/", "/") + "|Referer=" + url)
        return

    # Look for HLS sources
    match = re.search(r"video_url_hls\s*[:=]\s*[\"']([^\"']+)[\"']", html)
    if match:
        vp.play_from_direct_link(match.group(1).replace("\\/", "/") + "|Referer=" + url)
        return

    vp.play_from_link_to_resolve(url)
