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

from urllib.parse import quote_plus, urljoin

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "hentai2w",
    "[COLOR hotpink]Hentai2W[/COLOR]",
    "https://hentai2w.com/",
    "hentai2w.png",
    "hentai2w",
    category="Hentai & Anime",
)


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
        "items": "div.item-col, div.-video",
        "url": {"selector": "a[href]", "attr": "href"},
        "title": {
            "selector": "a[title]",
            "attr": "title",
            "fallback_selectors": [".item-name", "img[alt]"],
        },
        "thumbnail": {
            "selector": "img",
            "attr": "src",
            "fallback_attrs": ["data-src"],
        },
        "duration": {"selector": ".item-time, .duration"},
        "pagination": {
            "selector": ".pagination a, ul.pagination a",
            "attr": "href",
        },
    }

    utils.soup_videos_list(site, soup, spec)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)

    for item in soup.select("div.item-col, div.category-item, a[href*='/category/']"):
        link = item if item.name == "a" else item.find("a", href=True)
        if not link:
            continue
        href = urljoin(site.url, link.get("href", ""))
        img = item.find("img") if item.name != "a" else link.find("img")
        thumb = img.get("src") if img else site.img_cat
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

    source = soup.find("source", src=True)
    video = soup.find("video", src=True)
    video_url = None

    if source and source.get("src"):
        video_url = source["src"]
    elif video and video.get("src"):
        video_url = video["src"]

    if video_url:
        video_url = urljoin(url, video_url)
        vp.progress.update(75, "[CR]Playing video[CR]")
        vp.play_from_direct_url(video_url)
    else:
        utils.notify("No playable stream found", "Hentai2W")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = url.format(quote_plus(keyword))
        List(search_url)
