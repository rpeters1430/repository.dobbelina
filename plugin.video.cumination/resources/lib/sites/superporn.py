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
import json
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.sites.soup_spec import SoupSiteSpec

site = AdultSite(
    "superporn",
    "[COLOR hotpink]SuperPorn[/COLOR]",
    "https://www.superporn.com/",
    "superporn.png",
    "superporn",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": ".thumb-video",
        "url": {"selector": "a.thumb-video__description", "attr": "href"},
        "title": {
            "selector": "a.thumb-video__description",
            "text": True,
            "clean": True,
        },
        "thumbnail": {"selector": "img", "attr": "data-src", "fallback_attrs": ["src"]},
        "duration": {"selector": ".duracion", "text": True},
        "pagination": {
            "selector": ".pagination a",
            "text_matches": ["next", "»"],
            "attr": "href",
            "mode": "List",
        },
    }
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Latest Videos[/COLOR]",
        site.url + "latest",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Popular[/COLOR]",
        site.url + "most-popular",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Top Rated[/COLOR]", site.url + "top-rated", "List", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search", "Search", site.img_search
    )
    List(site.url)
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
        # SuperPorn uses /search?q=%QUERY%
        search_url = site.url + "search?q=" + urllib_parse.quote_plus(keyword)
        List(search_url)


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    # Categories are in .list-categories-item or similar
    cat_items = soup.select(
        ".list-categories__item, .category-item, a[href*='/category/']"
    )

    entries = []
    for anchor in cat_items:
        if anchor.name != "a":
            anchor = anchor.select_one("a")
        if not anchor:
            continue

        href = utils.safe_get_attr(anchor, "href")
        if not href:
            continue

        name = utils.safe_get_text(anchor)
        if not name:
            name = utils.safe_get_attr(anchor, "title")
        if not name:
            continue

        img_tag = anchor.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])

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

    # SuperPorn (TechPump) often uses direct MP4s in JS
    # Look for "video_url" or quality sources
    match = re.search(r"video_url\s*:\s*[\"']([^\"']+)[\"']", html)
    if match:
        vp.play_from_direct_link(match.group(1) + "|Referer=" + url)
        return

    # Alternative sources dictionary
    match = re.search(r"video_sources\s*:\s*({[^}]+})", html)
    if match:
        try:
            sources = json.loads(match.group(1).replace("'", '"'))
            best_q = sorted(sources.keys(), reverse=True)[0]
            vp.play_from_direct_link(sources[best_q] + "|Referer=" + url)
            return
        except:
            pass

    vp.play_from_link_to_resolve(url)
