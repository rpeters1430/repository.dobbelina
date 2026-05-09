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
import json
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "hentaistream",
    "[COLOR hotpink]HentaiStream[/COLOR]",
    "https://tube.hentaistream.com/",
    "hentaistream.png",
    "hentaistream",
    category="Hentai & Anime",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Genres[/COLOR]",
        site.url + "genres",
        "Genres",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Most Viewed[/COLOR]",
        site.url + "hentai-most-viewed-episodes-all",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "?s=",
        "Search",
        site.img_search,
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    # Find all video items
    items = soup.select("div.post")

    for item in items:
        link_tag = item.select_one("p.posttitle a") or item.select_one("div.postimg a")
        if not link_tag:
            continue

        videopage = utils.safe_get_attr(link_tag, "href")
        name = utils.safe_get_attr(link_tag, "title") or utils.safe_get_text(link_tag)

        img_tag = item.select_one("div.postimg img")
        img = utils.safe_get_attr(img_tag, "src")

        if name and videopage:
            name = utils.cleantext(name)
            if not videopage.startswith("http"):
                videopage = urllib_parse.urljoin(site.url, videopage)
            if img and not img.startswith("http"):
                img = urllib_parse.urljoin(site.url, img)

            site.add_download_link(
                name,
                videopage,
                "Playvid",
                img,
                name,
            )

    # Handle pagination
    pagination = soup.select_one("div.navigation")
    if pagination:
        next_link = pagination.find("a", string=lambda t: t and ">" in t)
        if next_link:
            next_url = utils.safe_get_attr(next_link, "href")
            if next_url:
                if not next_url.startswith("http"):
                    next_url = urllib_parse.urljoin(site.url, next_url)
                page_match = re.search(r"page/(\d+)", next_url)
                page_num = page_match.group(1) if page_match else "Next"
                site.add_dir(
                    "Next Page ({0})".format(page_num), next_url, "List", site.img_next
                )

    utils.eod()


@site.register()
def Genres(url):
    html = utils.getHtml(url)
    soup = utils.parse_html(html)

    # Find genres in the content area
    genre_links = soup.select("ul.genres li a") or soup.select("div.genres a")
    if not genre_links:
        # Fallback to any links under /list/
        genre_links = soup.select('a[href*="/list/"]')

    for link in genre_links:
        name = utils.safe_get_text(link)
        genre_url = utils.safe_get_attr(link, "href")
        if name and genre_url:
            if not genre_url.startswith("http"):
                genre_url = urllib_parse.urljoin(site.url, genre_url)
            site.add_dir(name, genre_url, "List", "")
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "+")
        url = url + title
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    vpage = utils.getHtml(url, site.url)
    
    # Check for iframe or direct video
    soup = utils.parse_html(vpage)
    iframe = soup.select_one("iframe[src*='player'], iframe[src*='embed']")
    if iframe:
        iframe_url = utils.safe_get_attr(iframe, "src")
        if iframe_url:
            if iframe_url.startswith("//"):
                iframe_url = "https:" + iframe_url
            vp.play_from_link_to_resolve(iframe_url)
            return

    # Fallback to kt_player if present
    if "kt_player('kt_player'" in vpage:
        vp.play_from_kt_player(vpage, url)
        return

    # Fallback to direct resolution
    vp.play_from_link_to_resolve(url)
