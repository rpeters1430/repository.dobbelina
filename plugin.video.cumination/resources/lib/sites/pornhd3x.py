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
    "pornhd3x",
    "[COLOR hotpink]PornHD3x[/COLOR]",
    "https://www9.pornhd3x.tv/",
    "pornhd3x.png",
    "pornhd3x",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": ".ml-item.item",
        "url": {"selector": "a.ml-mask", "attr": "href"},
        "title": {"selector": "h2", "text": True, "clean": True},
        "thumbnail": {
            "selector": "img",
            "attr": "data-original",
            "fallback_attrs": ["src"],
        },
        "quality": {"selector": ".mli-quality", "text": True},
        "pagination": {
            "selector": ".pagination a",
            "text_matches": ["next", "last", "»"],
            "attr": "href",
            "mode": "List",
        },
    }
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Movies[/COLOR]",
        site.url + "porn-hd-free-full-1080p",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]RealityKings[/COLOR]",
        site.url + "studio/realitykings",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]NaughtyAmerica[/COLOR]",
        site.url + "studio/naughtyamerica",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Brazzers[/COLOR]",
        site.url + "studio/brazzers",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
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
        # PornHD3x uses /search/%QUERY%
        search_url = site.url + "search/" + urllib_parse.quote_plus(keyword)
        List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    # Check for sources in script
    # var sources = [{"file":"...","label":"720p"}]
    match = re.search(r"sources\s*:\s*(\[[^\]]+\])", html)
    if match:
        try:
            sources_list = json.loads(match.group(1))
            sources = {
                s.get("label", "Video"): s.get("file")
                for s in sources_list
                if s.get("file")
            }
            if sources:
                best_url = utils.selector("Select quality", sources)
                if best_url:
                    vp.play_from_direct_link(best_url + "|Referer=" + url)
                    return
        except Exception:
            pass

    # Alternative: check for direct MP4 links in HTML
    match = re.search(r"file:\s*[\"']([^\"']+\.mp4[^\"']*)[\"']", html)
    if match:
        vp.play_from_direct_link(match.group(1) + "|Referer=" + url)
        return

    vp.play_from_link_to_resolve(url)
