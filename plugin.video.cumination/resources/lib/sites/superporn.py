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
        site.url + "videos/latest",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Popular[/COLOR]",
        site.url + "videos/popular",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Top Rated[/COLOR]", site.url + "videos", "List", site.img_cat
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
    if (not listhtml) and any(
        dead in url.rstrip("/") for dead in ("/latest", "/most-popular", "/top-rated")
    ):
        listhtml = utils.getHtml(site.url, site.url)
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
    cat_items = soup.select("a.thumb-duracion.icon-category")
    if not cat_items:
        cat_items = soup.select("a.dropdown__item[href]")

    entries = []
    seen = set()
    for anchor in cat_items:
        if anchor.name != "a":
            anchor = anchor.select_one("a")
        if not anchor:
            continue

        href = utils.safe_get_attr(anchor, "href")
        if not href:
            continue

        name_tag = anchor.select_one(".category__name, h3, span")
        name = (
            utils.safe_get_text(name_tag) if name_tag else utils.safe_get_text(anchor)
        )
        if not name:
            name = utils.safe_get_attr(anchor, "title")
        if not name:
            continue

        img_tag = anchor.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src", "data-original"])
        cat_url = urllib_parse.urljoin(site.url, href)
        key = (name.lower(), cat_url)
        if key in seen:
            continue
        seen.add(key)

        entries.append((name, cat_url, img))

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

    # Pattern 1: video_url with colon or equals
    match = re.search(r"video_url\s*[:=]\s*[\"']([^\"']+)[\"']", html)
    if match:
        vp.play_from_direct_link(match.group(1) + "|Referer=" + url)
        return

    # Pattern 2: video_sources dictionary
    match = re.search(r"video_sources\s*[:=]\s*({[^}]+})", html)
    if match:
        try:
            sources_str = match.group(1).replace("'", '"')
            sources = json.loads(sources_str)
            if sources:
                # Get highest quality
                best_q = sorted(sources.keys(), reverse=True)[0]
                vp.play_from_direct_link(sources[best_q] + "|Referer=" + url)
                return
        except Exception:
            pass

    # Pattern 3: sources array with quality levels
    match = re.search(r"sources\s*:\s*(\[[^\]]+\])", html)
    if match:
        try:
            sources_list = json.loads(match.group(1))
            sources = {
                s.get("label", s.get("quality", "Video")): s.get("file", s.get("src"))
                for s in sources_list
                if s.get("file") or s.get("src")
            }
            if sources:
                best_url = utils.selector("Select quality", sources)
                if best_url:
                    vp.play_from_direct_link(best_url + "|Referer=" + url)
                    return
        except Exception:
            pass

    # Pattern 4: Direct file: pattern
    match = re.search(r"file:\s*[\"']([^\"']+)[\"']", html)
    if match:
        video_url = match.group(1)
        if video_url and not video_url.endswith((".jpg", ".png", ".gif")):
            vp.play_from_direct_link(video_url + "|Referer=" + url)
            return

    # Pattern 5: Check for video tag
    soup = utils.parse_html(html)
    video_tag = soup.find("video")
    if video_tag:
        source = video_tag.find("source")
        if source and source.get("src"):
            vp.play_from_direct_link(source["src"] + "|Referer=" + url)
            return

    # Pattern 6: Check for iframes (embedded players)
    iframe = soup.find("iframe")
    if iframe and iframe.get("src"):
        iframe_url = urllib_parse.urljoin(url, iframe["src"])
        vp.play_from_link_to_resolve(iframe_url)
        return

    vp.play_from_link_to_resolve(url)
