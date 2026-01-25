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

import xbmc
import xbmcgui
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "justfullporn",
    "[COLOR hotpink]Just Full Porn[/COLOR]",
    "https://justfullporn.net/",
    "justfullporn.png",
    "justfullporn",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Actors[/COLOR]", site.url + "tags/", "Tags", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, "")
    soup = utils.parse_html(listhtml)

    contexturl = utils.addon_sys + "?mode=justfullporn.Lookupinfo&url="
    contextmenu = [
        ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + contexturl + ")")
    ]

    def _context_menu(videopage):
        return [
            (
                label,
                action.replace(
                    "&url=", "&url=" + urllib_parse.quote_plus(videopage)
                ),
            )
            for label, action in contextmenu
        ]

    for item in soup.select("[data-post-id]"):
        link = item.find("a", href=True)
        if not link:
            continue
        videopage = urllib_parse.urljoin(site.url, link["href"])
        img_tag = item.find("img")
        name = utils.safe_get_attr(img_tag, "alt")
        if not name:
            name = utils.safe_get_attr(link, "title") or utils.safe_get_text(link)
        name = utils.cleantext(name)
        if not name:
            continue
        img = utils.safe_get_attr(
            img_tag, "data-src", ["src", "data-original", "data-lazy"]
        )
        if img:
            img = urllib_parse.urljoin(site.url, img)
        site.add_download_link(
            name,
            videopage,
            "justfullporn.Playvid",
            img or site.image,
            name,
            contextm=_context_menu(videopage),
        )

    current = soup.select_one("a.page-link.current")
    next_link = soup.select_one("a.next.page-link") or soup.select_one(
        "a.page-link.next"
    )
    if next_link:
        next_url = urllib_parse.urljoin(site.url, next_link.get("href", ""))
        npnr = utils.safe_get_text(next_link).strip()
        if not npnr.isdigit():
            current_nr = utils.safe_get_text(current).strip() if current else ""
            if current_nr.isdigit():
                npnr = str(int(current_nr) + 1)
            else:
                npnr = ""
        page_numbers = []
        for anchor in soup.select("a.page-link"):
            text = utils.safe_get_text(anchor).strip()
            if text.isdigit():
                page_numbers.append(int(text))
        lpnr = str(max(page_numbers)) if page_numbers else ""
        label = "Next Page"
        if npnr:
            label = "Next Page ({})".format(npnr)
            if lpnr:
                label = "Next Page ({}/{})".format(npnr, lpnr)
        cm_page = (
            utils.addon_sys
            + "?mode=justfullporn.GotoPage"
            + "&url="
            + urllib_parse.quote_plus(next_url)
            + "&np="
            + str(npnr)
            + "&lp="
            + str(lpnr or 0)
        )
        cm = [("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")]
        site.add_dir(label, next_url, "List", contextm=cm)
    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = url.replace("/page/{}/".format(np), "/page/{}/".format(pg))
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
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.play_from_site_link(url, url)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        searchUrl = url + keyword.replace(" ", "+")
        List(searchUrl)


@site.register()
def Categories(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    for block in soup.select(".video-block-cat"):
        link = block.find("a", href=True)
        if not link:
            continue
        name = utils.safe_get_attr(link, "title") or utils.safe_get_text(link)
        name = utils.cleantext(name)
        if not name:
            continue
        img_tag = block.find("img")
        img = utils.safe_get_attr(
            img_tag, "poster", ["src", "data-src", "data-original"]
        )
        videos = utils.cleantext(utils.safe_get_text(block.select_one(".video-datas")))
        if videos:
            name += " [COLOR blue]{}[/COLOR]".format(videos)
        catpage = urllib_parse.urljoin(site.url, link["href"])
        site.add_dir(name, catpage, "List", img or "")

    next_link = soup.select_one("a.next.page-link") or soup.select_one(
        "a.page-link.next"
    )
    if next_link and next_link.get("href"):
        page_number = next_link.get("href", "").rstrip("/").split("/")[-1]
        site.add_dir(
            "Next Page (" + page_number + ")",
            next_link.get("href"),
            "Categories",
            site.img_next,
        )

    utils.eod()


@site.register()
def Tags(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    for link in soup.select(".tag-item a[href]"):
        name = utils.cleantext(utils.safe_get_text(link))
        tagpage = utils.safe_get_attr(link, "href")
        if name and tagpage:
            site.add_dir(name, tagpage, "List", "")

    utils.eod()


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Cat", r'(category/[^"]+)"\s*?class="label"\s*?title="([^"]+)"', ""),
        ("Model", r'(tag/[^"]+)"\s*?class="label"\s*?title="([^"]+)"', ""),
    ]

    lookupinfo = utils.LookupInfo(site.url, url, "justfullporn.List", lookup_list)
    lookupinfo.getinfo()
