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
from resources.lib.decrypters.kvsplayer import kvs_decode
from resources.lib.sites.soup_spec import SoupSiteSpec

site = AdultSite(
    "notfans",
    "[COLOR hotpink]NotFans[/COLOR]",
    "https://notfans.com/",
    "notfans.png",
    "notfans",
    category="Amateur & Social",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": ".item",
        "url": {"selector": "a[href]", "attr": "href"},
        "title": {"selector": "strong.title", "text": True, "clean": True},
        "thumbnail": {
            "selector": "img",
            "attr": "src",
            "fallback_attrs": ["data-src", "data-original"],
        },
        "pagination": {
            "selector": ".pagination a",
            "text_matches": ["Next"],
            "attr": "href",
            "mode": "List",
        },
    }
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Latest[/COLOR]", site.url + "latest-updates/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Top Today[/COLOR]", site.url + "day/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Top This Week[/COLOR]", site.url + "week/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Top This Month[/COLOR]", site.url + "month/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search)
    List(site.url + "latest-updates/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.eod()
        return
    soup = utils.parse_html(listhtml)
    VIDEO_LIST_SPEC.run(site, soup, base_url=site.url)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = site.url + "search/" + urllib_parse.quote_plus(keyword) + "/"
        List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    license_match = re.search(r"license_code:\s*'([^']+)'", html, re.IGNORECASE)
    license_code = license_match.group(1) if license_match else ""

    sources = {}
    for idx, raw_url in enumerate(
        re.findall(r"video_url\s*:\s*'([^']+)'", html, re.IGNORECASE), start=1
    ):
        stream_url = raw_url
        if stream_url.startswith("function/"):
            if license_code:
                try:
                    stream_url = kvs_decode(stream_url, license_code)
                except Exception:
                    stream_url = re.sub(r"^function/\d+/", "", stream_url)
            else:
                stream_url = re.sub(r"^function/\d+/", "", stream_url)
        if stream_url and stream_url.startswith("http"):
            sources["Source {}".format(idx)] = stream_url

    if sources:
        stream_url = (
            utils.selector("Select quality", sources)
            if len(sources) > 1
            else next(iter(sources.values()))
        )
        if stream_url:
            vp.play_from_direct_link(stream_url + "|Referer=" + url)
            return

    vp.play_from_link_to_resolve(url)
