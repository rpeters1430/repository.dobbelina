"""
Cumination
Copyright (C) 2025 Cumination

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

import re
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.sites.soup_spec import SoupSiteSpec
from six.moves import urllib_parse


site = AdultSite(
    "longvideos",
    "[COLOR hotpink]WOW.xxx[/COLOR]",
    "https://www.wow.xxx/",
    "longvideos.png",
    "longvideos",
    category="Video Tubes",
)


VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": "div.item",
        "url": {"selector": "a.thumb_img", "attr": "href"},
        "title": {
            "selector": "strong.title",
            "fallback_selectors": ["a.thumb_title", "a[title]"],
            "text": True,
            "clean": True,
        },
        "thumbnail": {
            "selector": "img",
            "attr": "data-src",
            "fallback_attrs": ["src"],
        },
        "duration": {"selector": "span.duration", "text": True},
        "pagination": {
            "selector": "div.pagination a",
            "text_matches": ["Next", ">"],
            "attr": "href",
            "mode": "List",
        },
    }
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Latest[/COLOR]",
        site.url + "latest-updates/",
        "List",
        site.img_cat,
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
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/?q=",
        "Search",
        site.img_search,
    )
    List(site.url + "latest-updates/")
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
        search_url = url + urllib_parse.quote_plus(keyword)
        List(search_url)


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    cat_items = soup.select(".category-item, a[href*='/categories/']")

    entries = []
    for anchor in cat_items:
        if anchor.name != "a":
            anchor = anchor.select_one("a")
        if not anchor:
            continue

        href = utils.safe_get_attr(anchor, "href")
        if not href:
            continue

        name = utils.safe_get_text(anchor.select_one(".category-name")) or utils.safe_get_text(anchor)
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
    vp.progress.update(25, "[CR]Loading video page[CR]")
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    # Check for direct sources in script or player markup
    match = re.compile(
        r'<source src="([^"]+)" title="([^"]+)"', re.IGNORECASE | re.DOTALL
    ).findall(html)
    if match:
        sources = {m[1]: site.url[:-1] + m[0].replace("&amp;", "&") for m in match}
        videourl = utils.prefquality(sources, reverse=True)
        if videourl:
            vp.play_from_direct_link(videourl)
            return

    # Standard resolution
    vp.play_from_link_to_resolve(url)
