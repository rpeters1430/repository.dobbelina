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
    "6xtube",
    "[COLOR hotpink]6XTube[/COLOR]",
    "http://www.6xtube.com/",
    "6xtube.png",
    "6xtube",
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
    if not soup:
        utils.eod()
        return

    for item in soup.select("div.well.well-sm"):
        link = item.select_one("a.video-link[href]")
        if not link:
            continue

        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage or "=modelfeed" in videopage:
            continue
        videopage = urllib_parse.urljoin(site.url, videopage)

        name = utils.cleantext(utils.safe_get_attr(link, "title", default=""))
        if not name:
            continue

        img_tag = item.select_one("img[src]")
        img = utils.safe_get_attr(img_tag, "src", default="")
        if img:
            if img.startswith("//"):
                img = "https:" + img
            elif img.startswith("/"):
                img = urllib_parse.urljoin(site.url, img)

        duration_elem = item.select_one(".duration")
        duration = utils.safe_get_text(duration_elem, default="")

        quality = ""
        quality_elem = item.select_one(".hd, .quality, .label-hd")
        if quality_elem:
            if "HD" in utils.safe_get_text(quality_elem, default="").upper():
                quality = "HD"
        elif "HD" in utils.safe_get_text(item, default="").upper():
            quality = "HD"

        site.add_download_link(
            name,
            videopage,
            "6xtube.Playvid",
            img,
            name,
            duration=duration,
            quality=quality,
            contextm="6xtube.Related",
        )

    next_link = None
    for link in soup.select("a.prevnext[href]"):
        if "Next" in utils.safe_get_text(link, default=""):
            next_link = link
            break

    if next_link:
        next_url = utils.safe_get_attr(next_link, "href", default="")
        if next_url:
            next_url = utils.fix_url(next_url, site.url, baseurl=url.split("page")[0])
            npnr = 0
            np_match = re.search(r"page(\d+)\.html", next_url)
            if np_match:
                npnr = int(np_match.group(1))

            lpnr = 0
            for page_link in soup.select("a[href]"):
                href = utils.safe_get_attr(page_link, "href", default="")
                page_match = re.search(r"page(\d+)\.html", href)
                if page_match:
                    lpnr = max(lpnr, int(page_match.group(1)))

            label = "Next Page"
            if npnr:
                label = "Next Page ({})".format(npnr)
                if lpnr:
                    label = "Next Page ({}/{})".format(npnr, lpnr)

            cm = None
            if npnr:
                cm_page = (
                    utils.addon_sys
                    + "?mode=6xtube.GotoPage"
                    + "&list_mode=6xtube.List"
                    + "&url="
                    + urllib_parse.quote_plus(next_url)
                    + "&np="
                    + str(npnr)
                    + "&lp="
                    + str(lpnr)
                )
                cm = [("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")]

            site.add_dir(label, next_url, "6xtube.List", site.img_next, contextm=cm)
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
        + str("6xtube.List")
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
    if not soup:
        utils.eod()
        return

    for item in soup.select(".col-sm-6"):
        link = item.select_one("a[href][title]")
        if not link:
            continue

        caturl = utils.safe_get_attr(link, "href", default="")
        if caturl:
            caturl = urllib_parse.urljoin(site.url, caturl)

        name = utils.cleantext(utils.safe_get_attr(link, "title", default=""))

        img_tag = link.select_one("img[src]")
        img = utils.safe_get_attr(img_tag, "src", default="")
        if img:
            if img.startswith("//"):
                img = "https:" + img
            elif img.startswith("/"):
                img = urllib_parse.urljoin(site.url, img)

        if caturl and name:
            site.add_dir(name, caturl, "List", img)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(
        name, download, direct_regex=r'(?:src:|source src=)\s*"([^"]+)"'
    )
    vp.progress.update(25, "[CR]Loading video page[CR]")

    videohtml = utils.getHtml(url, site.url, ignoreCertificateErrors=True)
    match = re.compile(
        r'iframe scrolling="no"\s*src="([^"]+)"', re.IGNORECASE | re.DOTALL
    ).findall(videohtml)
    if match:
        embedlink = match[0]
        embedhtml = utils.getHtml(embedlink, url, ignoreCertificateErrors=True)
        vp.play_from_html(embedhtml)
