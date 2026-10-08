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
    "fapello",
    "[COLOR hotpink]Fapello[/COLOR]",
    "https://fapello.com/",
    "fapello.png",
    "fapello",
    category="Amateur & Social",
    requires_flaresolverr=True,
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Trending Videos[/COLOR]",
        site.url + "trending/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Top This Week[/COLOR]",
        site.url + "video/week/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/{0}/",
        "Search",
        site.img_search,
    )
    List(site.url + "videos/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    spec = {
        "items": "div:has(> a[href*='/video/']), a[href*='/video/']",
        "url": {"selector": "a[href*='/video/']", "attr": "href"},
        "title": {
            "selector": "img[alt]",
            "attr": "alt",
            "fallback_selectors": ["a", "span"],
        },
        "thumbnail": {
            "selector": "img",
            "attr": "src",
            "fallback_attrs": ["data-src"],
        },
        "pagination": {
            "selector": "a[href*='/page/'], #pagination a, a.next",
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

    source = soup.find("source", src=True) or soup.find("video", src=True)
    video_url = None

    if source and source.get("src"):
        video_url = source["src"]
    else:
        matches = re.findall(r'https?://[^\s"\'<>]+\.(?:mp4|m3u8)[^\s"\'<>]*', vpage)
        if matches:
            video_url = matches[0]

    if video_url:
        video_url = urljoin(url, video_url)
        vp.progress.update(75, "[CR]Playing video[CR]")
        vp.play_from_direct_url(video_url)
    else:
        utils.notify("No playable stream found", "Fapello")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = url.format(quote_plus(keyword))
        List(search_url)
