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

site = AdultSite(
    "heavyfetish",
    "[COLOR hotpink]HeavyFetish[/COLOR]",
    "https://heavyfetish.com/",
    "heavyfetish.png",
    "heavyfetish",
    category="Specialty",
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url + "categories/", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search)
    List(site.url + "1/?&sort_by=post_date")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.eod()
        return
    soup = utils.parse_html(listhtml)
    for item in soup.select(".item.b6m-video, .hf-video-item"):
        link = item.select_one("a[href]")
        if not link:
            continue
        videopage = urllib_parse.urljoin(site.url, utils.safe_get_attr(link, "href"))
        name = utils.cleantext(utils.safe_get_attr(link, "title") or utils.safe_get_text(link))
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-webp", ["data-original", "src"]) if img_tag else ""
        if img:
            img = urllib_parse.urljoin(site.url, img)
        duration = utils.safe_get_text(item.select_one(".duration"), default="")
        site.add_download_link(name, videopage, "Playvid", img, name, duration=duration)

    # Next page: href has embedded whitespace — strip before using
    next_el = soup.select_one("li.next a")
    if next_el and next_el.get("href"):
        next_href = next_el["href"].strip()
        if next_href and not next_href.startswith("#"):
            next_url = urllib_parse.urljoin(site.url, next_href)
            page_match = re.search(r"/(\d+)/", next_href)
            page_num = page_match.group(1) if page_match else "?"
            site.add_dir("Next Page ({})".format(page_num), next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return
    soup = utils.parse_html(html)
    entries = []
    for anchor in soup.select("a.item[href*='/categories/']"):
        href = utils.safe_get_attr(anchor, "href")
        if not href:
            continue
        name = utils.safe_get_text(anchor.select_one(".title")) or utils.safe_get_attr(anchor, "title")
        if not name:
            continue
        img_tag = anchor.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"]) if img_tag else ""
        cat_url = urllib_parse.urljoin(site.url, href) + "?&sort_by=post_date"
        entries.append((name, cat_url, img))
    for name, cat_url, img in sorted(entries):
        site.add_dir(name, cat_url, "List", img)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        kw = urllib_parse.quote_plus(keyword)
        search_url = "{}search/{}/".format(site.url, kw) + "?&from_videos=1&from_albums=1"
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
