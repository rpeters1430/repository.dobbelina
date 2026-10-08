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
    "hentaicity",
    "[COLOR hotpink]Hentai City[/COLOR]",
    "https://www.hentaicity.com/",
    "hentaicity.png",
    "hentaicity",
    category="Hentai & Anime",
)


def _strip_click_tracker(value, item=None):
    # Listing links go through /click/<n>-<n>/ redirects to the video page.
    return re.sub(r"/click/\d+-\d+/", "/", value or "")


VIDEO_LIST_SPEC = {
    "items": "div.item",
    "url": {
        "selector": "a.thumb-img[href*='/video/']",
        "attr": "href",
        "transform": _strip_click_tracker,
    },
    "title": {
        "selector": "a.thumb-img img[alt]",
        "attr": "alt",
        "fallback_selectors": ["a.video-title"],
        "text": True,
    },
    "thumbnail": {
        "selector": "a.thumb-img img",
        "attr": "src",
        "fallback_attrs": ["data-src"],
    },
    "duration": {"selector": ".time", "text": True},
    "quality": {"selector": ".flag-hd", "text": True},
    "pagination": {"selector": "a#nextpage[href], a.next[href]", "attr": "href"},
}


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "customsearch.php?search={0}&search_type=video",
        "Search",
        site.img_search,
    )
    List(site.url + "videos/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    utils.soup_videos_list(site, soup, VIDEO_LIST_SPEC)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)

    # The page lists every category twice: once for videos, once for galleries.
    for item in soup.select("div.item.video-category"):
        link = item.select_one("a.thumb-img[href*='/videos/']")
        if not link:
            continue
        img = item.find("img")
        title = utils.safe_get_attr(img, "alt") or utils.safe_get_text(
            item.select_one(".item-date a")
        )
        if not title:
            continue
        thumb = utils.safe_get_attr(img, "src", ["data-src"])
        site.add_dir(
            title,
            urljoin(site.url, link["href"]),
            "List",
            urljoin(site.url, thumb) if thumb else site.img_cat,
        )

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    vpage = utils.getHtml(url, site.url)
    soup = utils.parse_html(vpage)

    # Related-video cards carry <video> trailers, so target the main player.
    source = (
        soup.select_one("video#video-id source[src]")
        or soup.select_one("video#video-id[src]")
        or soup.select_one("video[playsinline][src]")
    )
    if source:
        vp.progress.update(75, "[CR]Playing video[CR]")
        vp.play_from_direct_link(
            "{}|Referer={}".format(urljoin(url, source["src"]), site.url)
        )
    else:
        vp.progress.close()
        utils.notify("No playable stream found", "Hentai City")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = url.format(quote_plus(keyword))
        List(search_url)
