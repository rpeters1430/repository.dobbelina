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
    "playhdporn",
    "[COLOR hotpink]PlayHDPorn[/COLOR]",
    "https://playhdporn.com/",
    "playhdporn.png",
    "playhdporn",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": ".item",
        "url": {"selector": "a", "attr": "href"},
        "title": {"selector": "strong.title", "text": True, "clean": True},
        "thumbnail": {"selector": "img.thumb", "attr": "data-original", "fallback_attrs": ["src"]},
        "duration": {"selector": ".duration", "text": True},
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
    site.add_dir("[COLOR hotpink]Latest Updates[/COLOR]", site.url + "latest-updates/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Top Rated[/COLOR]", site.url + "top-rated/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Most Viewed[/COLOR]", site.url + "most-popular/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url + "categories/", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search)
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
        # PlayHDPorn uses /search/%QUERY%/ or ?q=
        search_url = site.url + "search/" + urllib_parse.quote_plus(keyword) + "/"
        List(search_url)


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    # Categories are usually in .list-categories .item
    cat_items = soup.select(".list-categories .item, .list-categories a")
    
    entries = []
    for item in cat_items:
        # If item is already the anchor
        if item.name == "a":
            anchor = item
        else:
            anchor = item.select_one("a")
            
        if not anchor:
            continue
            
        href = utils.safe_get_attr(anchor, "href")
        if not href:
            continue
            
        title_tag = anchor.select_one(".title, strong")
        name = utils.safe_get_text(title_tag) if title_tag else utils.safe_get_text(anchor)
        if not name:
            name = utils.safe_get_attr(anchor, "title")
            
        if not name:
            continue
            
        img_tag = anchor.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-original", "data-src"])
        
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

    # Look for flashvars or video sources
    # Common pattern in KVS: flashvars.video_url
    match = re.search(r"video_url:\s*'([^']+)'", html)
    if match:
        video_url = match.group(1)
        vp.play_from_direct_link(video_url + "|Referer=" + url)
        return

    # Alternative: check for quality-based sources in script
    # var video_sources = { "720p": "...", "480p": "..." }
    match = re.search(r'video_sources\s*=\s*({[^}]+})', html)
    if match:
        try:
            sources = json.loads(match.group(1).replace("'", '"'))
            # Get best quality
            best_q = sorted(sources.keys(), reverse=True)[0]
            vp.play_from_direct_link(sources[best_q] + "|Referer=" + url)
            return
        except:
            pass

    # Standard KVS license/player URL
    # flashvars.license_code = ...
    # flashvars.video_url = ...
    
    vp.play_from_link_to_resolve(url)
