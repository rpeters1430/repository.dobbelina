"""
Cumination
Copyright (C) 2023 Cumination

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
from random import randint
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.decrypters.kvsplayer import kvs_decode

site = AdultSite(
    "watchmdh",
    "[COLOR hotpink]WatchMDH[/COLOR]",
    "https://watchdirty.is/",
    "watchmdh.png",
    "watchmdh",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Models[/COLOR]",
        site.url
        + "models/?mode=async&function=get_block&block_id=list_models_models_list&sort_by=title&_=",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url + "latest-updates/")
    utils.eod()


@site.register()
def List(url):
    utils.kodilog(url)
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return

    cm = []
    cm_lookupinfo = utils.addon_sys + "?mode=" + str("watchmdh.Lookupinfo") + "&url="
    cm.append(
        ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + cm_lookupinfo + ")")
    )
    cm_related = utils.addon_sys + "?mode=" + str("watchmdh.Related") + "&url="
    cm.append(
        ("[COLOR deeppink]Related videos[/COLOR]", "RunPlugin(" + cm_related + ")")
    )

    for item in soup.select(".item"):
        link = item.select_one("a[href][title]")
        if not link:
            continue

        videopage = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(utils.safe_get_attr(link, "title", default=""))
        thumb = utils.safe_get_attr(
            item.select_one("[data-original]"), "data-original", ["src"]
        )
        duration = utils.safe_get_text(item.select_one(".duration"), default="")
        quality = utils.safe_get_text(item.select_one(".is-hd"), default="")

        if not videopage or not name:
            continue

        site.add_download_link(
            name,
            videopage,
            "watchmdh.Playvid",
            thumb,
            name,
            duration=duration,
            quality=quality,
            contextm=cm,
        )

    next_link = soup.select_one(
        ".next[data-block-id][data-parameters]"
    ) or soup.select_one(".next[href]")
    if next_link:
        block_id = utils.safe_get_attr(next_link, "data-block-id", default="")
        params = utils.safe_get_attr(next_link, "data-parameters", default="")
        npage_match = re.search(r"from[^:]*:(\d+)", params)
        current_page = int(npage_match.group(1)) if npage_match else 1
        npage = current_page + 1

        params = params.replace(";", "&").replace(":", "=")
        rnd = 1000000000000 + randint(0, 999999999999)
        base = url.split("?")[0]
        nurl = (
            f"{base}?mode=async&function=get_block&block_id={block_id}&{params}&_={rnd}"
        )
        nurl = nurl.replace("+from_albums", "")
        nurl = re.sub(r"&from([^=]*)=\d+", r"&from\1={}".format(npage), nurl)

        match_lp = re.search(r'from[^:]*:(\d+)"', listhtml, re.DOTALL | re.IGNORECASE)
        lpparam = "&lp={}".format(match_lp.group(1)) if match_lp else "&lp=0"
        lptxt = "/{}".format(match_lp.group(1)) if match_lp else ""

        cm_page = (
            utils.addon_sys
            + "?mode=watchmdh.GotoPage"
            + "&url="
            + urllib_parse.quote_plus(nurl)
            + "&np="
            + str(npage)
            + lpparam
            + "&listmode=watchmdh.List"
        )
        cm = [("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")]

        site.add_dir(
            "[COLOR hotpink]Next Page...[/COLOR] (" + str(npage) + lptxt + ")",
            nurl,
            "List",
            site.img_next,
            contextm=cm,
        )

    utils.eod()


@site.register()
def GotoPage(url, np, lp, listmode):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = re.sub(r"&from([^=]*)=\d+", r"&from\1={}".format(pg), url, re.IGNORECASE)
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        contexturl = (
            utils.addon_sys
            + "?mode="
            + listmode
            + "&url="
            + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        searchUrl = "{}{}/".format(searchUrl, keyword.replace(" ", "-"))
        List(searchUrl)


@site.register()
def Categories(url):
    url = url + str(1000000000000 + randint(0, 999999999999))
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    if not soup:
        utils.eod()
        return

    for item in soup.select(".item[href][title]"):
        catpage = utils.safe_get_attr(item, "href", default="")
        name = utils.cleantext(utils.safe_get_attr(item, "title", default=""))
        videos_elem = item.select_one(".videos")
        videos = utils.safe_get_text(videos_elem, default="")
        if not catpage or not name:
            continue
        name = name + " [COLOR deeppink]" + videos + "[/COLOR]" if videos else name
        site.add_dir(name, catpage, "List", "")

    current_page_elem = soup.select_one(".page-current span")
    next_link = soup.select_one(".next[data-block-id][data-parameters]")
    if current_page_elem and next_link:
        current_page_text = utils.safe_get_text(current_page_elem, default="1")
        npage = int(current_page_text) + 1 if current_page_text.isdigit() else 1
        block_id = utils.safe_get_attr(next_link, "data-block-id", default="")
        params = utils.safe_get_attr(next_link, "data-parameters", default="")
        params = params.replace(";", "&").replace(":", "=")
        rnd = 1000000000000 + randint(0, 999999999999)
        nurl = url.split("?")[
            0
        ] + "?mode=async&function=get_block&block_id={0}&{1}&_={2}".format(
            block_id, params, str(rnd)
        )
        nurl = nurl.replace("+from_albums", "")
        nurl = re.sub(r"&from([^=]*)=\d+", r"&from\1={}".format(npage), nurl)

        # Find last page from "Letzte" link
        last_page_link = None
        for link in soup.select("a[data-parameters]"):
            if "Letzte" in utils.safe_get_text(link, default=""):
                last_page_link = link
                break

        lp_text = ""
        lpparam = "&lp=0"
        if last_page_link:
            lp_params = utils.safe_get_attr(
                last_page_link, "data-parameters", default=""
            )
            lp_match = re.search(r"from[^:]*:(\d+)", lp_params)
            if lp_match:
                lp_text = "/" + lp_match.group(1)
                lpparam = "&lp=" + lp_match.group(1)
                utils.kodilog(lp_match.group(1))

        cm_page = (
            utils.addon_sys
            + "?mode=watchmdh.GotoPage"
            + "&url="
            + urllib_parse.quote_plus(nurl)
            + "&np="
            + str(npage)
            + lpparam
            + "&listmode=watchmdh.Categories"
        )
        cm = [("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")]

        site.add_dir(
            "[COLOR hotpink]Next Page...[/COLOR] (" + str(npage) + lp_text + ")",
            nurl,
            "Categories",
            site.img_next,
            contextm=cm,
        )

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videohtml = utils.getHtml(url)
    match = re.compile(
        r"video(?:_|_alt_)url\d*: '([^']+)'.+?video(?:_|_alt_)url\d*_text: '([^']+)'",
        re.DOTALL | re.IGNORECASE,
    ).findall(videohtml)

    sources = {}
    if match:
        for video in match:
            sources[video[1]] = video[0]
    else:
        match = re.compile(
            r"video_url:\s+'([^']+)'", re.DOTALL | re.IGNORECASE
        ).findall(videohtml)
        sources["0p"] = match[0]
    vp.progress.update(75, "[CR]Video found[CR]")
    videourl = utils.prefquality(
        sources, sort_by=lambda x: int(x.replace(" 4k", "")[:-1]), reverse=True
    )
    if videourl:
        if videourl.startswith("function/"):
            license = re.findall(r"license_code:\s*'([^']+)", videohtml)[0]
            videourl = kvs_decode(videourl, license)
        videourl += "|Referer=" + url
        vp.play_from_direct_link(videourl)


@site.register()
def Lookupinfo(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    if not soup:
        return

    lookup_items = []

    # Find tags
    for link in soup.select('a[href*="/tags/"]'):
        tag_url = utils.safe_get_attr(link, "href", default="")
        tag_name = utils.cleantext(utils.safe_get_text(link, default=""))
        if tag_url and tag_name and "/tags/" in tag_url:
            lookup_items.append(("Tags", tag_name, tag_url))

    # Find models
    for link in soup.select('a[href*="/models/"]'):
        model_url = utils.safe_get_attr(link, "href", default="")
        model_name = utils.cleantext(utils.safe_get_text(link, default=""))
        if model_url and model_name and "/models/" in model_url:
            lookup_items.append(("Models", model_name, model_url))

    if not lookup_items:
        utils.notify("Lookup", "No tags or models found")
        return

    utils.kodiDB(lookup_items, "watchmdh.List")


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("watchmdh.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")
