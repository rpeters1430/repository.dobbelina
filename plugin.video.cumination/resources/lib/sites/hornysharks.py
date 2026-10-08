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
    "hornysharks",
    "[COLOR hotpink]HornySharks[/COLOR]",
    "https://hornysharks.com/",
    "hornysharks.png",
    "hornysharks",
    category="Video Tubes",
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
    List(site.url + "latest-updates/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    spec = {
        "items": "div.item",
        "url": {"selector": "a[href*='/video/']", "attr": "href"},
        "title": {
            "selector": "a[title]",
            "attr": "title",
            "fallback_selectors": ["img[alt]", "strong.title"],
        },
        "thumbnail": {
            "selector": "img",
            "attr": "data-original",
            "fallback_attrs": ["data-src", "src"],
        },
        "duration": {"selector": ".duration"},
        "pagination": {
            "selector": "ul.pagination li a, .pagination a",
            "attr": "href",
        },
    }

    utils.soup_videos_list(site, soup, spec)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)

    for item in soup.select("div.item, a[href*='/categories/']"):
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
    if "kt_player('kt_player'" in vpage:
        vp.progress.update(60, "[CR]kt_player detected[CR]")
        vp.play_from_kt_player(vpage, url)
    else:
        soup = utils.parse_html(vpage)
        source = soup.find("source", src=True) or soup.find("video", src=True)
        if source and source.get("src"):
            vp.play_from_direct_link(urljoin(url, source["src"]))
        else:
            utils.notify("No playable stream found", "HornySharks")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = url.format(quote_plus(keyword))
        List(search_url)
