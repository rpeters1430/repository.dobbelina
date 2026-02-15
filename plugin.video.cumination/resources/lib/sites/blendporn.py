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
    "blendporn",
    "[COLOR hotpink]Blendporn[/COLOR]",
    "https://www.blendporn.com/",
    "blendporn.png",
    "blendporn",
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
    for item in soup.select(".well.well-sm, .video-item, .item"):
        link = item.select_one("a.video-link, a[href]")
        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage or "=modelfeed" in videopage:
            continue
        name = utils.cleantext(
            utils.safe_get_attr(link, "title", default=utils.safe_get_text(link))
        )
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
        duration = utils.safe_get_text(item.select_one(".duration"), default="")
        quality = (
            "HD" if item.select_one(".quality, .hd") or "HD" in item.get_text() else ""
        )
        site.add_download_link(
            name,
            videopage,
            "blendporn.Playvid",
            img,
            name,
            duration=duration,
            quality=quality,
            contextm="blendporn.Related",
        )

    next_link = soup.select_one("a.prevnext[href]")
    if next_link and "next" in utils.safe_get_text(next_link, "").lower():
        next_url = utils.safe_get_attr(next_link, "href", default="")
        if next_url:
            site.add_dir("Next Page", next_url, "blendporn.List", site.img_next)
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
        + str("blendporn.List")
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
    for item in soup.select(".col-sm-6, .category-item"):
        link = item.select_one("a[href]")
        caturl = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(utils.safe_get_attr(link, "title", default=""))
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
        if not caturl or not name:
            continue
        site.add_dir(name, caturl, "List", img)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(
        name, download, direct_regex=r'(?:src:|source src=)\s*["\']([^"\']+)["\']'
    )
    vp.progress.update(25, "[CR]Loading video page[CR]")

    # Try Playwright sniffer first
    try:
        from tests.utils.playwright_helper import fetch_with_playwright_and_network
        vp.progress.update(40, "[CR]Sniffing with Playwright...[CR]")
        _, requests = fetch_with_playwright_and_network(url, wait_for="load")
        for req in requests:
            if any(ext in req["url"].lower() for ext in [".mp4", ".m3u8"]):
                if not any(x in req["url"].lower() for x in ["/thumbs/", "/images/"]):
                    vp.play_from_direct_link(req["url"])
                    return
    except (ImportError, Exception):
        pass

    videohtml = utils.getHtml(url, site.url)
    
    # Try finding the video source directly in the main page first
    match = re.search(r'<source\s+[^>]*src=["\']([^"\']+)["\']', videohtml, re.IGNORECASE)
    if match:
        vp.play_from_direct_link(match.group(1))
        return

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
        embedhtml = utils.getHtml(embedlink, url)
        vp.play_from_html(embedhtml)
