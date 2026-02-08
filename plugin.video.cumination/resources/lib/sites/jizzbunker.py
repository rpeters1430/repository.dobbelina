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
    "[COLOR hotpink]Jizzbunker[/COLOR]",
    "https://jizzbunker.com/",
    "jizzbunker.png",
    "jizzbunker",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": "figure",
        "url": {"selector": "figcaption a", "attr": "href"},
        "title": {"selector": "figcaption a", "text": True, "clean": True},
        "thumbnail": {
            "selector": "a.img img",
            "attr": "data-original",
            "fallback_attrs": ["src"],
        },
        "duration": {"selector": "li.dur time", "text": True},
        "pagination": {
            "selector": ".pagination a",
            "text_matches": ["next", "→"],
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
        "[COLOR hotpink]Newest[/COLOR]",
        site.url + "straight/latest",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Top Rated[/COLOR]",
        site.url + "straight/top-rated",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "straight/categories",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "searching/",
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
        # Jizzbunker uses /searching/?queryString=%QUERY%
        search_url = (
            site.url + "searching/?queryString=" + urllib_parse.quote_plus(keyword)
        )
        List(search_url)


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    cat_items = soup.select(".category-item, a[href*='/category/']")

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
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])

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
    match = re.search(r"video_url:\s*[\"']([^\"']+)[\"']", html)
    if match:
        vp.play_from_direct_link(match.group(1) + "|Referer=" + url)
        return

    # Look for HLS sources
    match = re.search(r"video_url_hls:\s*[\"']([^\"']+)[\"']", html)
    if match:
        vp.play_from_direct_link(match.group(1) + "|Referer=" + url)
        return

    vp.play_from_link_to_resolve(url)
