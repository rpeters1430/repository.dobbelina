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
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "yrprno",
    "[COLOR hotpink]YrPrno[/COLOR]",
    "https://www.yrprno.com/",
    "yrprno.png",
    "yrprno",
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

    for card in soup.select(".well.well-sm"):
        link = card.select_one(".video-link[href]")
        if not link:
            continue
        videopage = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(
            utils.safe_get_attr(
                link, "title", default=utils.safe_get_text(link, default="")
            )
        )

        if not videopage or "=modelfeed" in videopage:
            continue

        img = utils.safe_get_attr(link.select_one("img"), "data-original", ["src"])
        duration = utils.safe_get_text(card.select_one(".duration"), default="")
        quality = "HD" if card.find(string=re.compile(r"\bHD\b")) else ""

        site.add_download_link(
            name,
            videopage,
            "yrprno.Playvid",
            img,
            name,
            duration=duration,
            quality=quality,
            contextm="yrprno.Related",
        )

    pagination_links = [
        link
        for link in soup.select("a.prevnext[href]")
        if "Next" in utils.safe_get_text(link, default="")
    ]
    pagination = (
        pagination_links[0] if pagination_links else soup.select_one("a.prevnext[href]")
    )
    if pagination:
        next_url = utils.safe_get_attr(pagination, "href", default="")
        page_match = re.search(r"page(\d+)\.html", next_url)
        page_num = page_match.group(1) if page_match else ""

        # Attempt to find last page number
        last_page = ""
        for link in soup.select("a.prevnext[href]"):
            href = utils.safe_get_attr(link, "href", default="")
            match = re.search(r"page(\d+)\.html", href)
            if match:
                last_page = (
                    max(last_page, match.group(1)) if last_page else match.group(1)
                )
        last_page = last_page or page_num

        contextmenu = []
        if page_num and last_page:
            contexturl = (
                utils.addon_sys
                + "?mode=yrprno.GotoPage"
                + "&list_mode=yrprno.List"
                + "&url="
                + urllib_parse.quote_plus(url)
                + "&np="
                + page_num
                + "&lp="
                + last_page
            )
            contextmenu.append(
                ("[COLOR violet]Goto Page[/COLOR]", "RunPlugin(" + contexturl + ")")
            )

        label = "Next Page"
        if page_num and last_page:
            label += f" ({page_num}/{last_page})"
        elif page_num:
            label += f" ({page_num})"
        site.add_dir(
            label, next_url, "yrprno.List", site.img_next, contextm=contextmenu
        )
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
        + str("yrprno.List")
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

    for link in soup.select("a[href][title]"):
        caturl = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(
            utils.safe_get_attr(
                link, "title", default=utils.safe_get_text(link, default="")
            )
        )
        if not caturl or not name:
            continue
        site.add_dir(name, caturl, "List", "")
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(
        name, download, direct_regex=r'source src=["\']([^"\']+)["\']'
    )
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videohtml = utils.getHtml(url, site.url, ignoreCertificateErrors=True)
    
    # Try finding the video source directly in the page first
    source_match = re.search(r'<source\s+[^>]*src=["\']([^"\']+)["\']', videohtml, re.IGNORECASE)
    if source_match:
        vp.play_from_direct_link(source_match.group(1))
        return

    vp.play_from_html(videohtml)
