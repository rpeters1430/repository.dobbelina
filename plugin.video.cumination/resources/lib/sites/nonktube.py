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
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "nonktube",
    "[COLOR hotpink]NonkTube[/COLOR]",
    "https://www.nonktube.com/",
    "nonktube.png",
    "nonktube",
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
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url + "?sorting=latest")
    utils.eod()


@site.register()
def List(url):
    utils.kodilog("nonktube.List: " + url)
    html = utils.getHtml(url, site.url)
    if "the requested search cannot be found" in html:
        utils.notify(msg="Nothing found")
        utils.eod()
        return

    soup = utils.parse_html(html)
    for item in soup.select(".video-block"):
        link = item.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage:
            continue
        name = utils.cleantext(
            utils.safe_get_attr(link, "title", default=utils.safe_get_text(link))
        )
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
        duration = utils.safe_get_text(item.select_one(".duration"), default="")
        site.add_download_link(
            name,
            videopage,
            "nonktube.Playvid",
            img,
            name,
            duration=duration,
            contextm="nonktube.Related",
        )

    next_link = soup.select_one(".page-link[href]")
    if next_link:
        next_url = utils.safe_get_attr(next_link, "href", default="")
        if next_url:
            site.add_dir(
                "Next Page",
                next_url,
                "nonktube.List",
                site.img_next,
                contextm="nonktube.GotoPage",
            )
    utils.eod()


@site.register()
def Cat(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    for item in soup.select(".video-block"):
        link = item.select_one("a[href]")
        caturl = utils.safe_get_attr(link, "href", default="")
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])
        name = utils.cleantext(
            utils.safe_get_text(item.select_one(".title"), default="")
        )
        count = utils.safe_get_text(item.select_one(".datas"), default="").strip()
        if not caturl or not name:
            continue
        name = name + " [COLOR hotpink]({0} videos)[/COLOR]".format(count)
        site.add_dir(name, caturl, "List", img)

    next_link = soup.select_one(".page-link[href]")
    if next_link and "&raquo;" in utils.safe_get_text(next_link, ""):
        np = utils.safe_get_attr(next_link, "href", default="")
        last_pg = ""
        for link in soup.select(".page-link"):
            text = utils.safe_get_text(link, default="")
            if text.isdigit():
                last_pg = text
        site.add_dir(
            "[COLOR hotpink]Next Page[/COLOR] ({0}/{1})".format("", last_pg),
            np,
            "Cat",
            site.img_next,
        )
    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = url.replace("page/{}".format(np), "page/{}".format(pg)).replace(
            "page-{}".format(np), "page-{}".format(pg)
        )
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
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("nonktube.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}".format(url, keyword.replace(" ", "%20"))
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download, direct_regex="<source src='([^']+)'")
    vp.progress.update(25, "[CR]Loading video page[CR]")

    videohtml = utils.getHtml(url, site.url)
    match = re.compile(
        r'<meta itemprop="contentURL" content="([^"]+)"', re.IGNORECASE | re.DOTALL
    ).search(videohtml)
    if match:
        videolink = match.group(1) + "|Referer:" + site.url
        vp.progress.update(75, "[CR]Loading video page[CR]")
        vp.play_from_direct_link(videolink)
