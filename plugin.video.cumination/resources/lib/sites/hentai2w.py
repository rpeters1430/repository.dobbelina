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

VIDEO_LIST_SPEC = {
    "items": "div.item-col.-video",
    "url": {"selector": "a[href*='/video/']", "attr": "href"},
    "title": {
        "selector": "a[title]",
        "attr": "title",
        "fallback_selectors": ["img[alt]"],
        "fallback_attrs": ["alt"],
    },
    "thumbnail": {
        "selector": "img",
        "attr": "src",
        "fallback_attrs": ["data-src"],
    },
    "duration": {"selector": ".item-time", "text": True},
    "quality": {"selector": ".item-quality", "text": True},
}


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "channels/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Most Viewed[/COLOR]",
        site.url + "most-viewed/",
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

    utils.soup_videos_list(site, soup, VIDEO_LIST_SPEC)

    # Page links are relative ("page2.html"), so resolve against this page.
    next_link = soup.select_one(".pagination a.next[href]")
    if next_link:
        next_url = urljoin(url, next_link["href"])
        if "?" in url and "?" not in next_url:
            next_url += "?" + url.split("?", 1)[1]
        site.add_dir("Next Page", next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)

    for item in soup.select("div.item-col.-channel"):
        link = item.find("a", href=True)
        if not link:
            continue
        title = utils.safe_get_attr(link, "title") or utils.safe_get_text(
            item.select_one(".item-name")
        )
        if not title:
            continue
        thumb = utils.safe_get_attr(item.find("img"), "src", ["data-src"])
        if "catdefault" in thumb:
            thumb = ""
        site.add_dir(
            title,
            urljoin(site.url, link["href"]).split("?")[0] + "?type=videos",
            "List",
            thumb or site.img_cat,
        )

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    vpage = utils.getHtml(url, site.url)
    soup = utils.parse_html(vpage)

    source = soup.select_one("video source[src]") or soup.select_one("video[src]")
    if source:
        vp.progress.update(75, "[CR]Playing video[CR]")
        vp.play_from_direct_link(
            "{}|Referer={}".format(urljoin(url, source["src"]), site.url)
        )
    else:
        vp.progress.close()
        utils.notify("No playable stream found", "Hentai2W")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = url.format(quote_plus(keyword))
        List(search_url)
