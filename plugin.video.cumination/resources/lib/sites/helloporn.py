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

import re
from urllib.parse import quote_plus, urljoin

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "helloporn",
    "[COLOR hotpink]HelloPorn[/COLOR]",
    "https://helloporn.com/",
    "helloporn.png",
    "helloporn",
    category="Video Tubes",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Channels[/COLOR]",
        site.url + "channels",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search?q={0}",
        "Search",
        site.img_search,
    )
    List(site.url + "videos")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    spec = {
        "items": "div.videoBoxWrapper",
        "url": {"selector": "a.videoBox[href], a[href*='/video-']", "attr": "href"},
        "title": {
            "selector": "a.videoBoxTitle",
            "attr": "title",
            "fallback_selectors": ["a.videoBoxTitle", "img[alt]"],
        },
        "thumbnail": {
            "selector": "img",
            "attr": "data-src",
            "fallback_attrs": ["src"],
        },
        "duration": {"selector": ".videoBoxMeta"},
        "pagination": {
            "selector": "li.page-item a.page-link, .pagination a",
            "attr": "href",
        },
    }

    utils.soup_videos_list(site, soup, spec)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)

    for link in soup.select("a[href*='/category/'], a[href*='/channels/']"):
        href = urljoin(site.url, link.get("href", ""))
        img = link.find("img")
        thumb = img.get("src") or img.get("data-src") if img else site.img_cat
        title = link.get_text(strip=True) or (img.get("alt") if img else "")
        if title:
            site.add_dir(title, href, "List", thumb)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    vpage = utils.getHtml(url, site.url)
    soup = utils.parse_html(vpage)

    # 1. Look for embed player iframe (voe, streamtape, etc.)
    iframe = soup.find("iframe", class_="embedPlayer") or soup.find("iframe", src=True)
    if iframe and iframe.get("src"):
        src = urljoin(url, iframe["src"])
        if vp.resolveurl.HostedMediaFile(src).valid_url():
            vp.progress.update(60, "[CR]Resolving embed[CR]")
            vp.play_from_link_to_resolve(src)
            return

    # 2. Look for direct video tag / source
    source = soup.find("source", src=True) or soup.find("video", src=True)
    if source and source.get("src"):
        vp.play_from_direct_link(urljoin(url, source["src"]))
        return

    # 3. Regex for mp4 / m3u8
    matches = re.findall(r'https?://[^\s"\'<>]+\.(?:mp4|m3u8)[^\s"\'<>]*', vpage)
    for m in matches:
        if "preview" not in m.lower():
            vp.play_from_direct_link(m)
            return

    utils.notify("No playable stream found", "HelloPorn")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = url.format(quote_plus(keyword))
        List(search_url)
