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
import xbmc
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse
from kodi_six import xbmcgui, xbmcplugin
import json
from math import ceil
from six import unichr

site = AdultSite(
    "pornhits",
    "[COLOR hotpink]PornHits[/COLOR]",
    "https://www.pornhits.com/",
    "pornhits.png",
    "pornhits",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories.php",
        "Categories",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "videos.php?p=1&q=",
        "Search",
        site.img_search,
    )
    List(site.url + "videos.php?p=1&s=l")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if ">There is no data in this list.<" in listhtml:
        utils.notify(msg="Nothing found")
        utils.eod()
        return

    if "Related Videos" in listhtml:
        listhtml = listhtml.split("Related Videos")[-1].split(
            '<div class="thumb-slider">'
        )[0]
    cm = []
    cm_lookupinfo = utils.addon_sys + "?mode=pornhits.Lookupinfo&url="
    cm.append(
        ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + cm_lookupinfo + ")")
    )
    cm_related = utils.addon_sys + "?mode=pornhits.Related&url="
    cm.append(
        ("[COLOR deeppink]Related videos[/COLOR]", "RunPlugin(" + cm_related + ")")
    )

    soup = utils.parse_html(listhtml)

    def _context_menu(videopage):
        return [
            (
                label,
                action.replace(
                    "&url=", "&url=" + urllib_parse.quote_plus(videopage)
                ),
            )
            for label, action in cm
        ]

    for item in soup.select("article.item"):
        link = item.find("a", href=True)
        if not link:
            continue
        videopage = urllib_parse.urljoin(site.url, link["href"])
        name = utils.safe_get_attr(link, "title")
        if not name:
            img_tag = item.find("img")
            name = utils.safe_get_attr(img_tag, "alt") if img_tag else ""
        if not name:
            name = utils.safe_get_text(link)
        name = utils.cleantext(name)
        if not name:
            continue
        img_tag = item.find("img")
        img = utils.safe_get_attr(
            img_tag, "data-original", ["data-src", "data-lazy", "src"]
        )
        if img:
            img = urllib_parse.urljoin(site.url, img)
        duration = utils.cleantext(
            utils.safe_get_text(item.select_one(".duration"))
        )
        site.add_download_link(
            name,
            videopage,
            "pornhits.Playvid",
            img or site.image,
            name,
            duration=duration,
            contextm=_context_menu(videopage),
        )

    pagination = soup.select_one("[data-page][data-count][data-total]")
    if pagination:
        cp = pagination.get("data-page")
        count = pagination.get("data-count")
        total = pagination.get("data-total")
        if cp and count and total:
            np_url = re.sub(r"\?p=\d+", "?p={}".format(int(cp) + 1), url)
            np = str(int(cp) + 1)
            lp = str(ceil(int(total) / int(count)))
            if int(np) <= int(float(lp)):
                cm_page = (
                    utils.addon_sys
                    + "?mode=pornhits.GotoPage"
                    + "&url="
                    + urllib_parse.quote_plus(np_url)
                    + "&np="
                    + np
                    + "&lp="
                    + lp
                )
                cm_page = [
                    ("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")
                ]
                site.add_dir(
                    "Next Page ({}/{})".format(np, lp),
                    np_url,
                    "List",
                    site.img_next,
                    contextm=cm_page,
                )
    utils.eod()


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("pornhits.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        searchUrl = "{0}{1}/".format(url, keyword.replace(" ", "%20"))
        List(searchUrl)


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    for link in soup.select('a.item[href][title]'):
        caturl = utils.safe_get_attr(link, "href")
        name = utils.safe_get_attr(link, "title")
        if not caturl or not name:
            continue
        site.add_dir(name.replace(" porn videos", ""), caturl, "List", "")
    xbmcplugin.addSortMethod(utils.addon_handle, xbmcplugin.SORT_METHOD_TITLE)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    html = utils.getHtml(url)
    match = re.compile(
        r'video:url"\s+content="([^"]+)"', re.IGNORECASE | re.DOTALL
    ).findall(html)
    if match:
        embedurl = match[0]
        embedhtml = utils.getHtml(embedurl, url)
        match = re.compile(
            r"\s},\s+'([^']+)',\s+null\);", re.IGNORECASE | re.DOTALL
        ).findall(embedhtml)
        if match:
            enc_url = match[0]
            dec_url = decode_url(enc_url)
            src = json.loads(dec_url)
            sources = {
                s["format"][1:-4].replace("hq", "720p").replace("lq", "360p"): s[
                    "video_url"
                ]
                for s in src
            }

            videourl = utils.prefquality(sources, reverse=True)
            if videourl:
                replacelst = {
                    "A": "\u0410",
                    "B": "\u0412",
                    "C": "\u0421",
                    "E": "\u0415",
                    "M": "\u041c",
                }
                for key in replacelst:
                    videourl = videourl.replace(replacelst[key], key)
                url1 = utils._bdecode(videourl.split(",")[0] + "==")
                url2 = utils._bdecode(videourl.split(",")[1] + "==")
                videolink = site.url[:-1] + url1 + "?" + url2 + "|referer=" + embedurl
                vp.play_from_direct_link(videolink)


def decode_url(t):
    # does not work in python 2 !!!
    e = "\u0410\u0412\u0421D\u0415FGHIJKL\u041cNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,~"
    n = ""
    r = 0
    while r < len(t):
        o = e.index(t[r])
        i = e.index(t[r + 1])
        a = e.index(t[r + 2])
        s = e.index(t[r + 3])
        o = o << 2 | i >> 4
        i = (15 & i) << 4 | a >> 2
        c = (3 & a) << 6 | s
        n += unichr(o)
        if a != 64:
            n += unichr(i)
        if s != 64:
            n += unichr(c)
        r += 4
    return n


@site.register()
def GotoPage(url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = url.replace("?p={}".format(np), "?p={}".format(pg))
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        contexturl = (
            utils.addon_sys
            + "?mode=pornhits.List"
            + "&url="
            + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Porn Site", ["Porn Site:(.*?)</h3>", 'href="([^"]+)"[^>]*>([^<]+)<'], ""),
        ("Network", ["Network:(.*?)</h3>", 'href="([^"]+)"[^>]*>([^<]+)<'], ""),
        ("Cat", ["Categories:(.*?)</h3>", 'href="([^"]+)"[^>]*>([^<]+)<'], ""),
        ("Stars", ["Porn-stars:(.*?)</h3>", 'href="([^"]+)"[^>]*>([^<]+)<'], ""),
    ]
    lookupinfo = utils.LookupInfo(site.url, url, "pornhits.List", lookup_list)
    lookupinfo.getinfo()
