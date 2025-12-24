"""
Cumination
Copyright (C) 2022 Team Cumination

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

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "trannyteca",
    "[COLOR hotpink]Trannyteca[/COLOR]",
    "https://www.trannyteca.com/",
    "trannyteca.png",
    "trannyteca",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]", site.url, "Categories", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return

    for article in soup.select("article"):
        img_tag = article.select_one("img[src]")
        link = article.select_one("a[href]")
        if not link:
            continue

        vurl = utils.safe_get_attr(link, "href", default="")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"])
        name = utils.cleantext(utils.safe_get_text(link, default=""))

        if vurl and name:
            site.add_download_link(name, vurl, "Playvid", img, name)

    next_link = soup.select_one("a.next.page-numbers[href]")
    if next_link:
        nextp = utils.safe_get_attr(next_link, "href", default="")
        if nextp:
            curr_pg_elem = soup.select_one(".page-numbers.current")
            curr_pg = utils.safe_get_text(curr_pg_elem, default="")

            # Find last page number
            last_pg = ""
            for page_link in soup.select(".page-numbers"):
                page_text = utils.safe_get_text(page_link, default="")
                if page_text.isdigit():
                    last_pg = page_text

            if curr_pg and last_pg:
                site.add_dir(
                    "Next Page... (Currently in Page {0} of {1})".format(
                        curr_pg, last_pg
                    ),
                    nextp,
                    "List",
                    site.img_next,
                )
            else:
                site.add_dir("Next Page...", nextp, "List", site.img_next)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    links = re.findall(r"px_repros\[.+?=\s*'([^']+)", html)
    if not links:
        utils.notify("Oh oh", "No playable video found")
        vp.progress.close()
        return
    pattern = r"""<iframe.+?src=['"]([^'"]+)"""
    links = [
        re.findall(pattern, utils._bdecode(x), re.DOTALL | re.IGNORECASE)[0]
        for x in links
    ]
    vp.play_from_link_list(links)


@site.register()
def Categories(url):
    cathtml = utils._getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    if not soup:
        utils.eod()
        return

    # Select menu items matching the pattern (menu-item-4xx, 6xx, 7xx)
    for menu_id in ["4", "6", "7"]:
        for item in soup.select(f'[id^="menu-item-{menu_id}"]'):
            link = item.select_one("a[href]")
            if not link:
                continue

            catpage = utils.safe_get_attr(link, "href", default="")
            name = utils.cleantext(utils.safe_get_text(link, default=""))

            if catpage and name:
                site.add_dir(name, catpage, "List", "")

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
