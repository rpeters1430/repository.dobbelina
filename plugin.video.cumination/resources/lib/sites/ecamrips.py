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
    "ecamrips",
    "[COLOR hotpink]eCamRips[/COLOR]",
    "https://www.ecamrips.com/",
    "ecamrips.png",
    "ecamrips",
    category="Cams & Live",
    requires_flaresolverr=True,
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "en/search.php?key={0}",
        "Search",
        site.img_search,
    )
    List(site.url + "en/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    spec = {
        "items": "li[id^='li'], .cam-item",
        "url": {"selector": "a.moiclick1[href], a[href*='show-cam-sex-movies']", "attr": "href"},
        "title": {
            "selector": "a[title]",
            "attr": "title",
            "fallback_selectors": ["img[alt]", "a.moiclick1"],
        },
        "thumbnail": {
            "selector": "img",
            "attr": "data-src",
            "fallback_attrs": ["data-original", "src"],
        },
        "pagination": {
            "selector": ".pagination a, div.pages a, a.next",
            "attr": "href",
        },
    }

    utils.soup_videos_list(site, soup, spec)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    vpage = utils.getHtml(url, site.url)
    soup = utils.parse_html(vpage)

    video_url = None
    # 1. Direct source / video tag
    source = soup.find("source", src=True) or soup.find("video", src=True)
    if source and source.get("src"):
        video_url = source["src"]

    # 2. Check iframe loading_video.php
    if not video_url:
        iframe = soup.find("iframe", src=re.compile(r"loading_video\.php", re.IGNORECASE))
        if iframe and iframe.get("src"):
            iframe_url = urljoin(url, iframe["src"])
            vp.progress.update(50, "[CR]Resolving embed[CR]")
            frame_html = utils.getHtml(iframe_url, url)
            frame_soup = utils.parse_html(frame_html)
            f_src = frame_soup.find("source", src=True) or frame_soup.find("video", src=True)
            if f_src and f_src.get("src"):
                video_url = f_src["src"]
            else:
                matches = re.findall(r'https?://[^\s"\'<>]+\.(?:mp4|m3u8)[^\s"\'<>]*', frame_html)
                if matches:
                    video_url = matches[0]

    # 3. Direct regex match on video page
    if not video_url:
        matches = re.findall(r'https?://[^\s"\'<>]+\.(?:mp4|m3u8)[^\s"\'<>]*', vpage)
        if matches:
            video_url = matches[0]

    if video_url:
        video_url = urljoin(url, video_url)
        vp.progress.update(80, "[CR]Playing video[CR]")
        vp.play_from_direct_url(video_url)
    else:
        utils.notify("No playable stream found", "eCamRips")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = url.format(quote_plus(keyword))
        List(search_url)
