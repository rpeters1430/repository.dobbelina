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
    "porn4k",
    "[COLOR hotpink]Porn4K[/COLOR]",
    "https://porn4k.to/",
    "porn4k.png",
    "porn4k",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]All titles[/COLOR]",
        site.url + "filme-von-a-z/",
        "Everything",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]", site.url, "Categories", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url + "page/1/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, "")
    soup = utils.parse_html(listhtml)

    video_items = soup.select("article")
    for item in video_items:
        try:
            link = item.select_one("a[href]")
            if not link:
                continue

            videopage = utils.safe_get_attr(link, "href")
            name = utils.safe_get_attr(link, "title")

            img_tag = item.select_one("img")
            img = utils.safe_get_attr(img_tag, "src")

            if not videopage or not name:
                continue

            name = utils.cleantext(name)
            contexturl = (
                utils.addon_sys
                + "?mode={}.Lookupinfo".format(site.module_name)
                + "&url="
                + urllib_parse.quote_plus(videopage)
            )
            contextmenu = [
                ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + contexturl + ")")
            ]
            site.add_download_link(
                name, videopage, "Playvid", img, name, contextm=contextmenu
            )

        except Exception as e:
            utils.kodilog("Error parsing video item: " + str(e))
            continue

    # Handle pagination
    next_link = soup.select_one('a[rel="next"]')
    if next_link and next_link.get("href"):
        next_url = next_link.get("href")
        page_number = next_url.split("/")[-2] if "/" in next_url else ""
        site.add_dir("Next Page (" + page_number + ")", next_url, "List", site.img_next)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    sitehtml = utils.getHtml(url, site.url)
    sources = re.compile(
        '<a href="([^"]+)" target="_blank" rel="nofollow">', re.DOTALL | re.IGNORECASE
    ).findall(sitehtml)
    links = {}
    for link in sources:
        if vp.bypass_hosters_single(link):
            continue
        if vp.resolveurl.HostedMediaFile(link).valid_url():
            links[link] = link
    vp.progress.close()

    if not links:
        utils.notify("Sorry", "No playable links found")
        return
    videourl = utils.selector("Select link", links)
    if not videourl:
        return
    vp.play_from_link_to_resolve(videourl)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "+")
        List(url + title)


@site.register()
def Categories(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    category_items = soup.select("li.cat-item")
    for item in category_items:
        try:
            link = item.select_one("a[href]")
            if not link:
                continue

            catpage = utils.safe_get_attr(link, "href")
            name = utils.safe_get_text(link)

            if not catpage or not name:
                continue

            name = utils.cleantext(name.strip())
            site.add_dir(name, catpage, "List", "")

        except Exception as e:
            utils.kodilog("Error parsing category: " + str(e))
            continue

    utils.eod()


@site.register()
def Everything(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    # Look for list items with links
    movie_items = soup.select("li")
    for item in movie_items:
        try:
            link = item.select_one("a[href]")
            if not link:
                continue

            movielink = utils.safe_get_attr(link, "href")
            name = utils.safe_get_text(link)

            if not movielink or not name:
                continue

            name = utils.cleantext(name.strip())
            site.add_download_link(name, movielink, "Playvid", "", name)

        except Exception as e:
            utils.kodilog("Error parsing movie item: " + str(e))
            continue

    utils.eod()


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Cat", r'porn4k\.to/([^"]+)" rel="category tag[^>]+>([^<]+)<', ""),
        ("Tag", '/(tag[^"]+)" rel="tag[^>]+>([^<]+)<', ""),
    ]

    lookupinfo = utils.LookupInfo(
        site.url, url, "{}.List".format(site.module_name), lookup_list
    )
    lookupinfo.getinfo()
