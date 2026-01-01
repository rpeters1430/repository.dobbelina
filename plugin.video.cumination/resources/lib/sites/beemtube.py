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
import xbmc
import xbmcgui
import json
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "beemtube",
    "[COLOR hotpink]BeemTube[/COLOR]",
    "https://beemtube.com/",
    "beemtube.png",
    "beemtube",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Channels[/COLOR]",
        site.url + "channels/",
        "Channels",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Pornstars[/COLOR]",
        site.url + "pornstars/alphabetical/",
        "Pornstars",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search?q=",
        "Search",
        site.img_search,
    )
    List(site.url + "most-recent/")
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url)
    if "Sorry, no results were found." in html:
        utils.notify(msg="Nothing found")
        utils.eod()
        return

    soup = utils.parse_html(html)
    for item in soup.select(".video-block, .content"):
        link = item.select_one("a.video-link, a.thumb, a[href]")
        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage:
            continue
        name = utils.cleantext(
            utils.safe_get_text(item.select_one("strong"), default="")
        )
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["data-original", "src"])
        duration = utils.safe_get_text(item.select_one(".duration"), default="")
        quality_el = item.select_one("span[class*='_video']")
        quality = ""
        if quality_el:
            class_name = " ".join(quality_el.get("class", []))
            quality = class_name.split("_video")[0].upper() if "_video" in class_name else ""
        site.add_download_link(
            name, videopage, "beemtube.Playvid", img, name, duration=duration, quality=quality
        )

    next_link = soup.select_one("a[rel='next'], a.next")
    if next_link:
        next_url = utils.safe_get_attr(next_link, "href", default="")
        if next_url:
            site.add_dir("Next Page", next_url, "beemtube.List", site.img_next)
    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = url.replace("page{}.html".format(np), "page{}.html".format(pg))
        url = url.replace("&page={}".format(np), "&page={}".format(pg))
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        contexturl = (
            utils.addon_sys
            + "?mode="
            + str(list_mode)
            + "&url="
            + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Channels(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    for item in soup.select(".channel_item"):
        link = item.select_one("a[href]")
        caturl = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(utils.safe_get_attr(link, "title", default=""))
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])
        count = utils.safe_get_text(item.select_one(".channel_item_videos"), default="").strip()
        if not caturl or not name:
            continue
        if count:
            name = name + "[COLOR hotpink] ({})[/COLOR]".format(count)
        site.add_dir(name, caturl, "List", img)
    utils.eod()


@site.register()
def Pornstars(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    for item in soup.select(".content.item.actors, .actors"):
        link = item.select_one("a[href]")
        caturl = utils.safe_get_attr(link, "href", default="")
        name = utils.safe_get_attr(link, "title", default="")
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])
        if not caturl or not name:
            continue
        site.add_dir(name, caturl, "List", img)
    next_link = soup.select_one("a[rel='next'], a.next")
    if next_link:
        next_url = utils.safe_get_attr(next_link, "href", default="")
        if next_url:
            site.add_dir("Next Page", next_url, "beemtube.Pornstars", site.img_next)
    utils.eod()


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    for item in soup.select(".content.categor, .category-item"):
        link = item.select_one("a[href]")
        caturl = utils.safe_get_attr(link, "href", default="")
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])
        name = utils.safe_get_text(item.select_one("strong"), default="")
        if not caturl or not name:
            continue
        site.add_dir(name.title(), caturl, "List", img)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}".format(url, keyword.replace(" ", "%20"))
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videohtml = utils.getHtml(url)
    match = re.compile(r'"embedUrl":\s+"([^"]+)"', re.IGNORECASE | re.DOTALL).findall(
        videohtml
    )
    if match:
        embedhtml = utils.getHtml(match[0])
        match = re.compile(
            r'"playlist":\s+"([^"]+)"', re.IGNORECASE | re.DOTALL
        ).findall(embedhtml)
        if match:
            playlist = utils.getHtml(match[0])
            jdata = json.loads(playlist)
            if "label" not in jdata["playlist"][0]["sources"][0].keys():
                jdata["playlist"][0]["sources"][0]["label"] = "0p"
            sources = {j["label"]: j["file"] for j in jdata["playlist"][0]["sources"]}
            videourl = utils.prefquality(sources, reverse=True)
            if videourl:
                vp.play_from_direct_link(videourl + "|referer:" + url)
