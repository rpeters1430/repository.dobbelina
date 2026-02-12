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
from resources.lib.decrypters.kvsplayer import kvs_decode
from resources.lib.sites.soup_spec import SoupSiteSpec

site = AdultSite(
    "neporn",
    "[COLOR hotpink]Neporn[/COLOR]",
    "https://neporn.com/",
    "neporn.png",
    "neporn",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": ".item",
        "url": {"selector": 'a[href*="/video/"]', "attr": "href"},
        "title": {"selector": "strong.title", "text": True, "clean": True},
        "thumbnail": {
            "selector": "img",
            "attr": "src",
            "fallback_attrs": ["data-src", "data-original"],
        },
        "duration": {"selector": ".duracion, .duration", "text": True},
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
        site.url + "latest-updates/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Popular[/COLOR]",
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

    # Pattern 1: JSON-LD contentUrl.
    ld_json = re.search(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if ld_json:
        try:
            payload = json.loads(ld_json.group(1).strip())
            if isinstance(payload, dict):
                content_url = payload.get("contentUrl")
                if content_url:
                    vp.play_from_direct_link(content_url + "|Referer=" + url)
                    return
        except Exception:
            pass

    # Pattern 2: KVS flashvars with license decoding support.
    license_match = re.search(
        r"license_code:\s*[\"']([^\"']+)[\"']", html, re.IGNORECASE
    )
    license_code = license_match.group(1) if license_match else ""
    sources = {}
    for pattern in (
        r"video_url\s*[:=]\s*[\"']([^\"']+)[\"']",
        r"video_alt_url\d*\s*[:=]\s*[\"']([^\"']+)[\"']",
    ):
        for idx, raw_url in enumerate(
            re.findall(pattern, html, re.IGNORECASE | re.DOTALL), start=1
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
            if stream_url:
                sources["Source {}".format(idx)] = stream_url

    if sources:
        stream_url = utils.selector("Select quality", sources) if len(sources) > 1 else next(iter(sources.values()))
        if stream_url:
            vp.play_from_direct_link(stream_url + "|Referer=" + url)
            return

    # Pattern 3: fallback direct MP4/m3u8.
    match = re.search(r"(https?://[^\"'<>\\s]+\\.(?:mp4|m3u8)[^\"'<>\\s]*)", html)
    if match:
        vp.play_from_direct_link(match.group(1) + "|Referer=" + url)
        return

    # Pattern 4: Check for sources array.
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

    # Pattern 5: Check for video tag.
    soup = utils.parse_html(html)
    video_tag = soup.find("video")
    if video_tag:
        source = video_tag.find("source")
        if source and source.get("src"):
            vp.play_from_direct_link(source["src"] + "|Referer=" + url)
            return

    # Pattern 6: Check for iframes (embedded players).
    iframe = soup.find("iframe")
    if iframe and iframe.get("src"):
        iframe_url = urllib_parse.urljoin(url, iframe["src"])
        vp.play_from_link_to_resolve(iframe_url)
        return

    vp.play_from_link_to_resolve(url)
