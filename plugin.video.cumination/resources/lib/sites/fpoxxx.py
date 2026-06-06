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
    "fpoxxx",
    "[COLOR hotpink]FPOXXX[/COLOR]",
    "https://www.fpo.xxx/",
    "fpoxxx.png",
    "fpoxxx",
    category="Video Tubes",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": ".item",
        "url": {"selector": "a[href]", "attr": "href"},
        "title": {"selector": "a", "attr": "title", "fallback_attrs": [], "text": False},
        "thumbnail": {
            "selector": "img",
            "attr": "data-original",
            "fallback_attrs": ["src"],
        },
        "duration": {"selector": ".duration", "text": True},
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
    site.add_dir("[COLOR hotpink]Latest[/COLOR]", site.url + "new-1/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Most Viewed[/COLOR]", site.url + "most-popular/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Pornstars[/COLOR]", site.url + "models-2/?sort_by=today_videos&from=1", "Pornstars", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search)
    List(site.url + "new-1/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.eod()
        return
    soup = utils.parse_html(listhtml)
    # Strip whitespace from Next href (fpoxxx embeds tabs in href attributes)
    for a in soup.select(".pagination a"):
        if a.get("href"):
            a["href"] = a["href"].strip()
    VIDEO_LIST_SPEC.run(site, soup, base_url=site.url)
    utils.eod()


@site.register()
def Pornstars(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return
    soup = utils.parse_html(html)
    for anchor in soup.select("a.item[href]"):
        href = utils.safe_get_attr(anchor, "href")
        name = utils.safe_get_attr(anchor, "title") or utils.safe_get_text(anchor.select_one("strong.title"))
        if not href or not name:
            continue
        img_tag = anchor.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"]) if img_tag else ""
        videos = utils.safe_get_text(anchor.select_one(".videos"), default="")
        label = "{} [COLOR hotpink][{}][/COLOR]".format(name, videos) if videos else name
        star_url = urllib_parse.urljoin(site.url, href) + "?sort_by=post_date&from=1"
        site.add_dir(label, star_url, "List", img)

    next_el = soup.select_one(".pagination a[data-parameters*='from:']")
    if next_el:
        np_match = re.search(r"from:(\d+)", utils.safe_get_attr(next_el, "data-parameters", default=""))
        if np_match:
            np = np_match.group(1)
            base = url.split("?")[0]
            site.add_dir("Next Page ({})".format(np), "{}?sort_by=today_videos&from={}".format(base, np), "Pornstars", site.img_next)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        kw_path = urllib_parse.quote_plus(keyword.replace(" ", "-"))
        kw_q = urllib_parse.quote_plus(keyword)
        search_url = "{}search/{}/".format(site.url, kw_path) + "?q={}&from_videos=1&from_albums=1".format(kw_q)
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
