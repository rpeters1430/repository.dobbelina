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
    "youcrazyx",
    "[COLOR hotpink]YouCrazyX[/COLOR]",
    "https://www.youcrazyx.com/",
    "youcrazyx.png",
    "youcrazyx",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "channels/",
        "Categories",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url + "most-recent/")
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if "Sorry, no results were found" in html:
        utils.notify(msg="Nothing found")
        utils.eod()
        return

    soup = utils.parse_html(html)
    items = soup.select("div.well.well-sm")
    for item in items:
        link = item.select_one("a.video-link[href]")
        if not link:
            continue
        videopage = utils.safe_get_attr(link, "href")
        if not videopage:
            continue
        videopage = urllib_parse.urljoin(site.url, videopage)
        if "modelfeed" in videopage:
            continue
        name = utils.safe_get_attr(link, "title") or utils.safe_get_text(link)
        name = utils.cleantext(name)
        if not name:
            continue
        img_tag = item.find("img")
        img = utils.safe_get_attr(
            img_tag, "data-original", ["data-src", "data-lazy", "src"]
        )
        if img:
            img = urllib_parse.urljoin(site.url, img)
        duration_tag = item.select_one(".duration")
        duration = utils.cleantext(utils.safe_get_text(duration_tag))
        quality = "HD" if "HD" in item.get_text() else ""
        site.add_download_link(
            name,
            videopage,
            "Playvid",
            img or site.image,
            name,
            contextm="youcrazyx.Related",
            duration=duration,
            quality=quality,
        )

    next_link = None
    for link in soup.select("a.prevnext"):
        if "next" in utils.safe_get_text(link).lower():
            next_link = link
            break
    if next_link:
        href = utils.safe_get_attr(next_link, "href")
        if href:
            npnr = ""
            match = re.search(r"page(\d+)\.html", href)
            if match:
                npnr = match.group(1)
            next_url = urllib_parse.urljoin(url, href)
            label = "Next Page"
            if npnr:
                label = "Next Page ({})".format(npnr)
            cm = None
            if npnr:
                cm_page = (
                    utils.addon_sys
                    + "?mode="
                    + "youcrazyx.GotoPage"
                    + "&list_mode="
                    + "youcrazyx.List"
                    + "&url="
                    + urllib_parse.quote_plus(next_url)
                    + "&np="
                    + str(npnr)
                    + "&lp="
                    + "0"
                )
                cm = [
                    ("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")
                ]
            site.add_dir(label, next_url, "List", site.img_next, contextm=cm)
    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = url.replace("page{}.html".format(np), "page{}.html".format(pg))
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
        + str("youcrazyx.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}/".format(url, keyword.replace(" ", "-"))
        List(url)


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    for link in soup.select("a[title][href]"):
        caturl = utils.safe_get_attr(link, "href")
        name = utils.cleantext(utils.safe_get_attr(link, "title"))
        if not caturl or not name:
            continue
        site.add_dir(name, urllib_parse.urljoin(site.url, caturl), "List", "")
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(
        name, download, direct_regex=r'(?:src:|source src=)\s*"([^"]+)"'
    )
    vp.progress.update(25, "[CR]Loading video page[CR]")

    videohtml = utils.getHtml(url, site.url, ignoreCertificateErrors=True)
    match = re.compile(
        r'iframe scrolling="no" src="([^"]+)"', re.IGNORECASE | re.DOTALL
    ).findall(videohtml)
    embedlink = None
    if match:
        embedlink = match[0]
    else:
        match = re.compile(r"iframe src='([^']+)'", re.IGNORECASE | re.DOTALL).findall(
            videohtml
        )
        if match:
            embedlink = match[0]

    if embedlink:
        embedhtml = utils.getHtml(embedlink, url, ignoreCertificateErrors=True)
        vp.play_from_html(embedhtml)
