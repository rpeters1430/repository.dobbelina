"""
Cumination
Copyright (C) 2025 Cumination

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
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse
import xbmc
import xbmcgui


site = AdultSite(
    "xxdbx", "[COLOR hotpink]xxdbx[/COLOR]", "https://xxdbx.com/", "xxdbx.png", "xxdbx"
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url)
    if "&ndash; 0 videos &ndash;" in listhtml:
        utils.notify(msg="No videos found!")
        return

    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return

    cm = []
    cm_lookupinfo = utils.addon_sys + "?mode=" + str("xxdbx.Lookupinfo") + "&url="
    cm.append(
        ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + cm_lookupinfo + ")")
    )
    cm_related = utils.addon_sys + "?mode=" + str("xxdbx.Related") + "&url="
    cm.append(
        ("[COLOR deeppink]Related videos[/COLOR]", "RunPlugin(" + cm_related + ")")
    )

    for v_div in soup.select(".v"):
        link = v_div.select_one("a[href]")
        if not link:
            continue

        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage:
            continue

        title_elem = v_div.select_one(".v_title")
        name = utils.cleantext(utils.safe_get_text(title_elem, default=""))

        img_tag = v_div.select_one("img[src]")
        img = utils.safe_get_attr(img_tag, "src", default="")
        if img and img.startswith("//"):
            img = "https:" + img

        duration_elem = v_div.select_one(".v_dur")
        duration = utils.safe_get_text(duration_elem, default="")

        if name and videopage:
            site.add_download_link(
                name,
                videopage,
                "xxdbx.Playvid",
                img,
                name,
                duration=duration,
                contextm=cm,
            )

    # Pagination
    next_link = None
    for link in soup.select('a[href][class=""]'):
        if "Next" in utils.safe_get_text(link, default=""):
            next_link = link
            break

    if next_link:
        next_url = utils.safe_get_attr(next_link, "href", default="")
        if next_url:
            # Extract page number from URL
            np_match = re.search(r"\?page=(\d+)", next_url)
            np = np_match.group(1) if np_match else ""

            contextmenu = []
            if np:
                contexturl = (
                    utils.addon_sys
                    + "?mode=xxdbx.GotoPage"
                    + "&url="
                    + urllib_parse.quote_plus(next_url)
                    + "&np="
                    + np
                    + "&lp=0"
                )
                contextmenu.append(
                    ("[COLOR violet]Goto Page[/COLOR]", "RunPlugin(" + contexturl + ")")
                )

            label = "Next Page"
            if np:
                label += f" ({np})"
            site.add_dir(
                label, next_url, "xxdbx.List", site.img_next, contextm=contextmenu
            )

    utils.eod()


@site.register()
def GotoPage(url, np, lp=0):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        url = url.replace("?page={}".format(np), "?page={}".format(pg))
        contexturl = (
            utils.addon_sys
            + "?mode="
            + "xxdbx.List&url="
            + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        List(url + keyword.replace(" ", "%20"))


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, site.url)
    soup = utils.parse_html(videopage)

    sources = {}
    if soup:
        for source_tag in soup.select("source[src][title]"):
            videourl = utils.safe_get_attr(source_tag, "src", default="")
            qual = utils.safe_get_attr(source_tag, "title", default="")
            if videourl and qual:
                if videourl.startswith("//"):
                    videourl = "https:" + videourl
                sources[qual] = videourl

    if sources:
        videourl = utils.prefquality(
            sources, sort_by=lambda x: 2160 if x == "4k" else int(x[:-1]), reverse=True
        )
        if videourl:
            vp.progress.update(75, "[CR]Video found[CR]")
            vp.play_from_direct_link(videourl)
    else:
        utils.notify("Oh Oh", "No Videos found")


@site.register()
def Lookupinfo(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    if not soup:
        return

    lookup_items = []

    # Find the tags div
    tags_div = soup.select_one(".tags")
    if tags_div:
        # Find dates
        for link in tags_div.select('a[href*="/dates/"]'):
            date_url = utils.safe_get_attr(link, "href", default="")
            date_name = utils.cleantext(utils.safe_get_text(link, default=""))
            if date_url and date_name:
                if date_url.startswith("/"):
                    date_url = site.url.rstrip("/") + date_url
                lookup_items.append(("Dates", date_name, date_url))

        # Find channels
        for link in tags_div.select('a[href*="/channels/"]'):
            channel_url = utils.safe_get_attr(link, "href", default="")
            channel_name = utils.cleantext(utils.safe_get_text(link, default=""))
            if channel_url and channel_name:
                if channel_url.startswith("/"):
                    channel_url = site.url.rstrip("/") + channel_url
                lookup_items.append(("Channels", channel_name, channel_url))

        # Find stars
        for link in tags_div.select('a[href*="/stars/"]'):
            star_url = utils.safe_get_attr(link, "href", default="")
            star_name = utils.cleantext(utils.safe_get_text(link, default=""))
            if star_url and star_name:
                if star_url.startswith("/"):
                    star_url = site.url.rstrip("/") + star_url
                lookup_items.append(("Stars", star_name, star_url))

        # Find search tags
        for link in tags_div.select('a[href*="/search/"]'):
            search_url = utils.safe_get_attr(link, "href", default="")
            search_name = utils.cleantext(utils.safe_get_text(link, default=""))
            if search_url and search_name:
                if search_url.startswith("/"):
                    search_url = site.url.rstrip("/") + search_url
                lookup_items.append(("Search", search_name, search_url))

    if not lookup_items:
        utils.notify("Lookup", "No tags found")
        return

    utils.kodiDB(lookup_items, "xxdbx.List")


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("xxdbx.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")
