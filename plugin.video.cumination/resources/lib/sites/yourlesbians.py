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
    "yourlesbians",
    "[COLOR hotpink]YourLesbians[/COLOR]",
    "https://yourlesbians.com/",
    "yourlesbians.png",
    "yourlesbians",
    category="Video Tubes",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": ".thumbs .item",
        "url": {"selector": "a", "attr": "href"},
        "title": {"selector": "a", "attr": "title", "clean": True},
        "thumbnail": {
            "selector": "img",
            "attr": "data-original",
            "fallback_attrs": ["src"],
        },
        "duration": {"selector": ".time", "text": True},
        "quality": {"selector": ".qualtiy", "text": True},
        "pagination": {
            "selector": ".pagination a",
            "text_matches": ["next", ">", "»"],
            "attr": "href",
            "mode": "List",
        },
    }
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Latest[/COLOR]", site.url, "List", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Most Viewed[/COLOR]",
        site.url + "most-popular/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Top Rated[/COLOR]",
        site.url + "top-rated/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Longest[/COLOR]",
        site.url + "longest/",
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
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    VIDEO_LIST_SPEC.run(site, soup, base_url=url)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = site.url + "search/" + urllib_parse.quote_plus(keyword) + "/"
        List(search_url)


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    cat_items = soup.select(".list-categories .item, .list-categories a")

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

    quality_matches = [
        (1080, r"video_alt_url2:\s*['\"]([^'\"]+)['\"]"),
        (720, r"video_alt_url:\s*['\"]([^'\"]+)['\"]"),
        (480, r"video_url:\s*['\"]([^'\"]+)['\"]")
    ]
    
    candidates = {}
    for res, pattern in quality_matches:
        match = re.search(pattern, html)
        if match:
            candidates[res] = match.group(1)
            
    if candidates:
        best_res = max(candidates.keys())
        video_url = candidates[best_res]
        vp.play_from_direct_link(video_url + "|Referer=" + url)
        return

    meta = re.search(r'["\']contentUrl["\']:\s*["\']([^"\']+)["\']', html)
    if meta:
        vp.play_from_direct_link(meta.group(1) + "|Referer=" + url)
        return

    vp.play_from_link_to_resolve(url)
