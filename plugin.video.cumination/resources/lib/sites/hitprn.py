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
    "hitprn",
    "[COLOR hotpink]Hitprn[/COLOR]",
    "https://www.hitprn.net/",
    "hitprn.png",
    "hitprn",
    category="Video Tubes",
)

addon = utils.addon


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Sites[/COLOR]", site.url, "Sites", "", "")
    site.add_dir(
        "[COLOR hotpink]Most Viewed[/COLOR]",
        site.url + "page/1/?filter=most-viewed",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Longest[/COLOR]",
        site.url + "page/1/?filter=longest",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Popular[/COLOR]",
        site.url + "page/1/?filter=popular",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Random[/COLOR]",
        site.url + "page/1/?filter=random",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url + "page/1/?filter=latest")


@site.register()
def List(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    video_items = soup.select("article.thumb-block")
    for item in video_items:
        try:
            link = item.select_one("a[href]")
            if not link:
                continue
            videopage = utils.safe_get_attr(link, "href")
            name = utils.safe_get_attr(link, "title") or utils.safe_get_text(link)

            img_tag = item.select_one("img")
            img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-main-thumb"]) or utils.safe_get_attr(item, "data-main-thumb")

            if not videopage or not name:
                continue

            name = utils.cleantext(name)

            contexturl = (
                utils.addon_sys
                + "?mode=hitprn.Lookupinfo"
                + "&url="
                + urllib_parse.quote_plus(videopage)
            )
            contextmenu = [
                ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + contexturl + ")")
            ]

            site.add_download_link(
                name, videopage, "Play", img, name, contextm=contextmenu
            )
        except Exception as e:
            utils.kodilog("Error parsing video item in hitprn: " + str(e))
            continue

    next_page_tag = None
    for a in soup.select('.pagination a'):
        if a.get_text().strip() == 'Next':
            next_page_tag = a
            break
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
def Sites(url):
    siteshtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(siteshtml)

    # Based on regex: class="level-\d+" value="([^"]+)">([^<]+)</option
    options = soup.select('option[class^="level-"]')
    for option in options:
        try:
            sitepage = utils.safe_get_attr(option, "value")
            name = utils.safe_get_text(option, strip=False)
            if sitepage and name:
                name = name.replace("\xa0\xa0\xa0", "- ").replace(
                    "&nbsp;&nbsp;&nbsp;", "- "
                )
                name = utils.cleantext(name)
                siteurl = site.url + "?cat=" + sitepage
                site.add_dir(name, siteurl, "List")
        except Exception as e:
            utils.kodilog("Error parsing site option in hitprn: " + str(e))
            continue
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url += keyword.replace(" ", "+")
        List(url)


@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    html = utils.getHtml(url, site.url)
    vp.play_from_html(html, url)


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Site", r'/(sites/[^"]+)"\s+rel="category tag">([^<]+)<', ""),
        ("Pornstar", r'/(pornstar/[^"]+)"\s+rel="tag">([^<]+)<', ""),
        ("Tag", r'/(tag/[^"]+)"\s+rel="tag">([^<]+)<', ""),
    ]

    lookupinfo = utils.LookupInfo(site.url, url, "hitprn.List", lookup_list)
    lookupinfo.getinfo()
