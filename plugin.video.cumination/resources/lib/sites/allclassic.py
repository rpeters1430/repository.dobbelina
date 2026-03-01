"""
Cumination site scraper
Copyright (C) 2026 Team Cumination

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
import xbmc
import xbmcgui
from resources.lib import utils
from resources.lib.adultsite import AdultSite


site = AdultSite(
    "allclassic",
    "[COLOR hotpink]AllClassic.Porn[/COLOR]",
    "https://allclassic.porn/",
    "allclassic.png",
    "allclassic",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/{0}/",
        "Search",
        site.img_search,
    )
    List(site.url + "page/1/")
    utils.eod()


@site.register()
def List(url):
    try:
        listhtml = utils.getHtml(url)
    except Exception as e:
        utils.kodilog("@@@@Cumination: failure in allclassic: " + str(e))
        utils.notify(msg="No videos found!")
        return
    if "No videos found " in listhtml:
        utils.notify(msg="No videos found!")
        return

    soup = utils.parse_html(listhtml)
    cm_lookupinfo = utils.addon_sys + "?mode=" + str("allclassic.Lookupinfo") + "&url="
    cm_related = utils.addon_sys + "?mode=" + str("allclassic.Related") + "&url="

    for card in soup.select("a.th.item[href]"):
        if card.select_one(".th-title"):
            continue
        videopage = utils.safe_get_attr(card, "href", default="")
        if not videopage:
            continue
        videopage = utils.fix_url(videopage, site.url)

        name = utils.cleantext(
            utils.safe_get_text(card.select_one(".th-description"), default="")
        )
        if not name:
            name = utils.cleantext(utils.safe_get_attr(card, "title", default=""))

        img_tag = card.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
        img = utils.fix_url(img.replace("&amp;", "&"), site.url) if img else ""

        duration = ""
        duration_icon = card.select_one("i.la-clock-o")
        if duration_icon and duration_icon.parent:
            duration = utils.safe_get_text(duration_icon.parent, default="")
            duration = re.sub(r"[^0-9:]", "", duration)

        quoted_url = urllib_parse.quote_plus(videopage)
        cm = [
            (
                "[COLOR deeppink]Lookup info[/COLOR]",
                "RunPlugin(" + cm_lookupinfo + quoted_url + ")",
            ),
            (
                "[COLOR deeppink]Related videos[/COLOR]",
                "RunPlugin(" + cm_related + quoted_url + ")",
            ),
        ]

        site.add_download_link(
            name,
            videopage,
            "allclassic.Playvid",
            img,
            name,
            duration=duration,
            contextm=cm,
        )

    re_npurl = 'class="active">.+?href="/([^"]+)"'
    re_npnr = r'class="active">.+?href="[^"]+">0*(\d+)<'
    utils.next_page(
        site,
        "allclassic.List",
        listhtml,
        re_npurl,
        re_npnr,
        contextm="allclassic.GotoPage",
    )
    utils.eod()


@site.register()
def GotoPage(url, np, lp=None):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        url = url.replace("/{}/".format(np), "/{}/".format(pg))
        contexturl = (
            utils.addon_sys
            + "?mode="
            + "allclassic.List&url="
            + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    vpage = utils.getHtml(url, site.url)
    if "kt_player('kt_player'" in vpage:
        vp.progress.update(60, "[CR]{0}[CR]".format("kt_player detected"))
        vp.play_from_kt_player(vpage, url)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        List(url.format(keyword.replace(" ", "-")))


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    for anchor in soup.select("a.th[href]"):
        caturl = utils.safe_get_attr(anchor, "href", default="")
        img = utils.safe_get_attr(
            anchor.select_one("img"), "src", ["data-src", "data-original"]
        )
        name = utils.safe_get_attr(anchor.select_one("img"), "alt", default="")
        if not (caturl and name):
            continue
        name = utils.cleantext(name)
        site.add_dir(name, caturl, "List", img)
    utils.eod()


@site.register()
def Lookupinfo(url):
    lookup_list = [
        (
            "Actor",
            r'btn-small" href="{}(models/[^"]+)"\s*itemprop="actor">([^<]+)<'.format(
                site.url
            ),
            "",
        ),
        (
            "Studio",
            r'btn-small" href="{}(studios/[^"]+)">([^<]+)<'.format(site.url),
            "",
        ),
        (
            "Category",
            r'btn-small" href="{}(categories/[^"]+)"\s*itemprop="genre">([^<]+)<'.format(
                site.url
            ),
            "",
        ),
        (
            "Tag",
            r'btn-small" href="{}(tags/[^"]+)"\s*itemprop="keywords">([^<]+)<'.format(
                site.url
            ),
            "",
        ),
    ]
    lookupinfo = utils.LookupInfo(site.url, url, "allclassic.List", lookup_list)
    lookupinfo.getinfo()


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("allclassic.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")
