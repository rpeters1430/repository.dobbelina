"""
Cumination
Copyright (C) 2023 Whitecream

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
    "vaginanl",
    "[COLOR hotpink]Vagina.nl[/COLOR] [COLOR orange](Dutch)[/COLOR]",
    "https://vagina.nl/",
    "https://c749a9571b.mjedge.net/img/logo-default.png",
    "vaginanl",
)


@site.register(default_mode=True)
def main(url):
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "sexfilms/search?q=",
        "Search",
        site.img_search,
    )
    List(url + "sexfilms/newest")


@site.register()
def List(url):
    html = utils.getHtml(url, "")
    if "Geen zoekresultaten gevonden" in html or "Nothing found" in html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    if not soup:
        utils.eod()
        return

    for card in soup.select(".card"):
        link = card.select_one("a.thumbnail-link[href]")
        if not link:
            continue

        videourl = urllib_parse.urljoin(
            site.url, utils.safe_get_attr(link, "href", default="")
        )
        name = utils.cleantext(
            utils.safe_get_attr(
                link, "title", default=utils.safe_get_text(link, default="")
            )
        )
        if not videourl or not name:
            continue

        img_tag = card.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])
        duration_elem = (
            card.select_one(".duration")
            or card.select_one(".time")
            or card.select_one(".video-duration")
        )
        duration = utils.safe_get_text(duration_elem, default="")

        site.add_download_link(name, videourl, "Playvid", img, name, duration=duration)

    pagination = soup.select_one(".pagination") or soup.select_one(
        'nav[aria-label*="pagination" i]'
    )
    next_link = soup.select_one('a[rel="next"]') or (
        pagination.select_one(".next a[href]") if pagination else None
    )
    if next_link:
        next_url = urllib_parse.urljoin(
            site.url, utils.safe_get_attr(next_link, "href", default="")
        )
        page_numbers = []
        if pagination:
            for node in pagination.find_all(["a", "span"]):
                text = utils.safe_get_text(node, default="")
                if text.isdigit():
                    page_numbers.append(int(text))
        last_page = str(max(page_numbers)) if page_numbers else ""
        np_match = re.search(r"(\d+)(?!.*\d)", next_url)
        next_page_num = np_match.group(1) if np_match else ""
        if next_url:
            suffix = ""
            if next_page_num and last_page:
                suffix = f" ({next_page_num}/{last_page})"
            elif next_page_num:
                suffix = f" ({next_page_num})"
            site.add_dir(f"Next Page{suffix}", next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    vp.play_from_site_link(url)


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "%20")
        searchUrl = searchUrl + title
        utils.kodilog(searchUrl)
        List(searchUrl)


@site.register()
def Categories(url):
    html = utils.getHtml(url, "")
    soup = utils.parse_html(html)
    if not soup:
        utils.eod()
        return

    for card in soup.select(".card"):
        link = card.select_one("a[href]")
        caturl = urllib_parse.urljoin(
            site.url, utils.safe_get_attr(link, "href", default="")
        )
        img_tag = card.select_one("img")
        catimg = utils.safe_get_attr(img_tag, "data-src", ["src"])
        catname = utils.cleantext(
            utils.safe_get_attr(
                img_tag, "alt", default=utils.safe_get_text(link, default="")
            )
        )

        if not caturl or not catname:
            continue

        site.add_dir(catname, caturl, "List", catimg)
    utils.eod()
