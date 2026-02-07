"""
Cumination
Copyright (C) 2020 Team Cumination

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
from resources.lib.decrypters.kvsplayer import kvs_decode
from resources.lib.adultsite import AdultSite
import time

site = AdultSite(
    "vipporns",
    "[COLOR hotpink]VIP Porns[/COLOR]",
    "https://www.vipporns.com/",
    "vipporns.png",
    "vipporns",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Cat",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "vp-search/",
        "Search",
        site.img_search,
    )
    List(site.url + "new-porn-video/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    # Try to find the main container to narrow down listing
    container = soup.select_one(
        ".list-albums, .box.tag, #list_videos_common_videos_list"
    )
    if container:
        video_items = container.select(".item")
    else:
        video_items = soup.select(".item")

    for item in video_items:
        try:
            link = item.select_one("a[href]")
            if not link:
                continue

            videopage = utils.safe_get_attr(link, "href")
            img_tag = item.select_one("img")
            img = utils.safe_get_attr(img_tag, "data-original", ["src"])

            name = utils.safe_get_attr(link, "title")
            if not name:
                name_tag = item.select_one(".title, .le")
                name = utils.safe_get_text(name_tag)

            duration_tag = item.select_one(".duration, .on")
            duration = utils.safe_get_text(duration_tag)

            if not videopage or not name:
                continue

            name = utils.cleantext(name.strip())
            site.add_download_link(
                name, videopage, "Playvid", img, name, duration=duration
            )
        except Exception as e:
            utils.kodilog("Error parsing video item in vipporns: " + str(e))
            continue

    match = re.search(
        r'class="next">.+?data-block-id="([^"]+)" data-parameters="([^"]+)"',
        listhtml,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        block_id = match.group(1)
        params = match.group(2).replace(";", "&").replace(":", "=")
        npage = params.split("=")[-1]
        nurl = url.split("?")[
            0
        ] + "?mode=async&function=get_block&block_id={0}&{1}&_={2}".format(
            block_id, params, int(time.time() * 1000)
        )
        nurl = nurl.replace("+from_albums", "")
        site.add_dir(
            "[COLOR hotpink]Next Page...[/COLOR] (" + npage + ")",
            nurl,
            "List",
            site.img_next,
        )

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "-")
        searchUrl = "{0}{1}/".format(url, title)
        List(searchUrl)


@site.register()
def Cat(url):
    cathtml = utils.getHtml(url, "")
    soup = utils.parse_html(cathtml)

    categories = []
    cat_items = soup.select(".item")
    for item in cat_items:
        try:
            link = item.select_one("a[href]")
            if not link:
                continue

            catpage = utils.safe_get_attr(link, "href")
            name_tag = item.select_one(".title")
            name = utils.safe_get_text(name_tag)

            count_tag = item.select_one(".videos")
            videos = utils.safe_get_text(count_tag)

            img_tag = item.select_one("img")
            img = (
                utils.safe_get_attr(img_tag, "src")
                if "no image" not in str(item)
                else ""
            )

            if name and catpage:
                display_name = "{0} [COLOR deeppink][I]({1})[/I][/COLOR]".format(
                    utils.cleantext(name.strip()), videos
                )
                categories.append((display_name, catpage, img, name.lower()))
        except Exception as e:
            utils.kodilog("Error parsing category in vipporns: " + str(e))
            continue

    for display_name, catpage, img, _ in sorted(categories, key=lambda x: x[3]):
        site.add_dir(display_name, catpage, "List", img)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    html = utils.getHtml(url, site.url)
    surl = re.search(r"video(?:_alt)?_url:\s*'([^']+)", html)
    if surl:
        vp.progress.update(50, "[CR]Video found[CR]")
        surl = surl.group(1)
        if surl.startswith("function/"):
            lcode = re.findall(r"license_code:\s*'([^']+)", html)[0]
            surl = kvs_decode(surl, lcode)
        if "get_file" in surl:
            surl = utils.getVideoLink(surl, site.url)
        surl = "{0}|User-Agent=iPad&Referer={1}".format(surl, site.url)
        vp.play_from_direct_link(surl)
    else:
        vp.progress.close()
        utils.notify("Oh oh", "No video found")
        return
