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
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "japteenx",
    "[COLOR hotpink]JapTeenX[/COLOR]",
    "https://www.japteenx.com/",
    "japteenx.png",
    "japteenx",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]", site.url + "tags", "Cats", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Girls[/COLOR]",
        site.url + "pornstars",
        "Pornstars",
        site.img_cat,
    )
    site.add_dir("[COLOR hotpink]Tags[/COLOR]", site.url + "tags", "Tags", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/videos?search_query=",
        "Search",
        site.img_search,
    )
    List(site.url + "videos?o=mr&type=public&page=1")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, "")
    soup = utils.parse_html(listhtml)

    items = soup.select(".well.well-sm")
    if not items:
        return

    for item in items:
        link = item.select_one("a")
        if not link:
            continue

        videopage = utils.safe_get_attr(link, "href")
        if not videopage:
            continue

        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src")
        name = utils.safe_get_attr(img_tag, "title")

        # Check for HD marker
        hd = "HD" if item.find(class_="hd") or "HD" in item.get_text() else ""

        # Get duration
        duration_tag = item.select_one(".duration")
        duration = utils.safe_get_text(duration_tag, "").strip()

        if not videopage.startswith("http"):
            videopage = site.url + videopage.lstrip("/")

        site.add_download_link(
            name, videopage, "Playvid", img, name, duration=duration, quality=hd
        )

    # Pagination
    next_link = soup.select_one("li a.prevnext")
    if next_link:
        next_url = utils.safe_get_attr(next_link, "href")
        if next_url:
            site.add_dir("Next Page...", next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.play_from_site_link(url, url)


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "+")
        searchUrl = searchUrl + title + "&type=public"
        List(searchUrl)


@site.register()
def Cats(url):
    match = [
        ("Amateur", "videos/amateur"),
        ("Gravure Idols", "videos/gravure-idols"),
        ("Hentai", "videos/hentai"),
        ("JAV", "videos/jav"),
        ("JAV Amateur", "videos/jav-amateur"),
        ("JAV Softcore", "videos/jav-softcore"),
        ("JAV Uncensored", "videos/jav-uncensored"),
        ("Southeast Asia", "videos/southeast-asia"),
        ("Western Girls", "videos/western-girls"),
    ]
    for name, catpage in match:
        site.add_dir(name, site.url + catpage + "?type=public&o=mr", "List", "")

    utils.eod()


@site.register()
def Pornstars(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    items = soup.select("a.model-sh")
    for item in items:
        catpage = utils.safe_get_attr(item, "href")
        if not catpage:
            continue

        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src")

        name_tag = item.select_one(".title-small")
        name = utils.safe_get_text(name_tag, "")

        # Get video count from fa-film icon
        videos_tag = item.find("i", class_="fa-film")
        videos = ""
        if videos_tag and videos_tag.next_sibling:
            videos = utils.safe_get_text(videos_tag.next_sibling, "").strip()

        if name:
            display_name = (
                "{} - [COLOR hotpink]{}[/COLOR]".format(name, videos)
                if videos
                else name
            )
            full_url = (
                site.url + catpage.lstrip("/")
                if not catpage.startswith("http")
                else catpage
            )
            site.add_dir(display_name, full_url, "List", img)

    # Pagination
    next_link = soup.select_one("li a.prevnext")
    if next_link:
        next_url = utils.safe_get_attr(next_link, "href")
        if next_url:
            site.add_dir("Next Page...", next_url, "Pornstars", site.img_next)

    utils.eod()


@site.register()
def Tags(url):
    listhtml = utils.getHtml(url, site.url, error=True)
    soup = utils.parse_html(listhtml)

    # Find all tag links
    tag_links = soup.find_all("a", href=re.compile(r"/tags/"))
    for link in tag_links:
        tagpage = utils.safe_get_attr(link, "href")
        if not tagpage or "tags/" not in tagpage:
            continue

        name = utils.safe_get_text(link, "").strip()
        if not name:
            continue

        # Get video count from span following the link
        videos = ""
        next_span = link.find_next_sibling("span")
        if next_span:
            videos = utils.safe_get_text(next_span, "").strip()

        display_name = (
            "{} - [COLOR hotpink]{}[/COLOR]".format(name, videos) if videos else name
        )
        full_url = site.url + tagpage.lstrip("/") + "?type=public&o=mr"
        site.add_dir(display_name, full_url, "List", "")

    utils.eod()
