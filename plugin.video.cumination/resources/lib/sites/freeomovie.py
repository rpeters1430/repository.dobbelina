"""
Cumination
Copyright (C) 2023 Team Cumination

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
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "freeomovie",
    "[COLOR hotpink]FreeOMovie[/COLOR]",
    "https://www.freeomovie.to/",
    "freeomovies.png",
    "freeomovie",
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url, "Cat", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        "{0}?s=".format(site.url),
        "Search",
        site.img_search,
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, "")
    soup = utils.parse_html(listhtml)

    video_items = soup.select(".thumi")
    for item in video_items:
        try:
            link = item.select_one("a[href]")
            if not link:
                continue

            videopage = utils.safe_get_attr(link, "href")
            name = utils.safe_get_attr(link, "title") or utils.safe_get_text(link)

            img_tag = item.select_one("img")
            img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])

            if not videopage or not name:
                continue

            name = utils.cleantext(name)

            contextmenu = []
            contexturl = (
                utils.addon_sys
                + "?mode="
                + str("freeomovie.Lookupinfo")
                + "&url="
                + urllib_parse.quote_plus(videopage)
            )
            contextmenu.append(
                ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + contexturl + ")")
            )

            site.add_download_link(
                name, videopage, "Playvid", img, name, contextm=contextmenu
            )
        except Exception as e:
            utils.kodilog("Error parsing video item in freeomovie: " + str(e))
            continue

    next_page_tag = soup.select_one('a[rel="next"]')
    if next_page_tag:
        next_url = utils.safe_get_attr(next_page_tag, "href")
        if next_url:
            page_num = next_url.split("/")[-2] if "/" in next_url else "Next"
            site.add_dir(
                "Next Page... ({0})".format(page_num),
                next_url,
                "List",
                site.img_next,
            )

    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "+")
        searchUrl = searchUrl + title
        List(searchUrl)


@site.register()
def Cat(url):
    listhtml = utils.getHtml(url, "")
    soup = utils.parse_html(listhtml)

    cat_items = soup.select(".cat-item")
    for item in cat_items:
        try:
            link = item.select_one("a[href]")
            if not link:
                continue

            catpage = utils.safe_get_attr(link, "href")
            name = utils.safe_get_text(link)

            if name and catpage:
                name = utils.cleantext(name)
                site.add_dir(name, catpage, "List", "")
        except Exception as e:
            utils.kodilog("Error parsing category in freeomovie: " + str(e))
            continue
    utils.eod()


@site.register()
def Lookupinfo(url):
    lookup_list = [
        (
            "Cat",
            [
                'Categories:(.*?)<div class="clearfix">',
                '(category/[^"]+)"[^>]+>([^<]+)',
            ],
            "",
        ),
        ("Tag", '(tag/[^"]+)">([^<]+)', ""),
    ]

    lookupinfo = utils.LookupInfo(site.url, url, "freeomovie.List", lookup_list)
    lookupinfo.getinfo()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(
        name,
        download=download,
        regex=r'href="([^"]+)"\s*target="myIframe"',
        direct_regex=None,
    )
    vp.play_from_site_link(url, url)
