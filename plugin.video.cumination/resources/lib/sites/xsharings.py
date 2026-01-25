"""
Cumination
Copyright (C) 2025 Team Cumination

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
import json
from resources.lib import utils
from six.moves import urllib_parse
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "xsharings",
    "[COLOR hotpink]XSharings[/COLOR]",
    "https://xsharings.com/",
    "xsharings.png",
    "xsharings",
)

addon = utils.addon


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Actors[/COLOR]",
        site.url + "actors/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url + "page/1?filter=latest")


@site.register()
def List(url):
    listhtml = utils.getHtml(url)
    listhtml = listhtml.split("Videos being watched")[0]
    if "It looks like nothing was found for this search" in listhtml:
        utils.notify("No results found", "Try a different search term")
        return

    cm = []
    cm_lookupinfo = utils.addon_sys + "?mode=xsharings.Lookupinfo&url="
    cm.append(
        ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + cm_lookupinfo + ")")
    )
    cm_related = utils.addon_sys + "?mode=xsharings.Related&url="
    cm.append(
        ("[COLOR deeppink]Related videos[/COLOR]", "RunPlugin(" + cm_related + ")")
    )

    soup = utils.parse_html(listhtml)
    items = soup.select("[data-post-id]")
    for item in items:
        link = item.find("a", href=True, title=True) or item.find("a", href=True)
        if not link:
            continue
        videopage = utils.safe_get_attr(link, "href")
        if not videopage:
            continue
        videopage = urllib_parse.urljoin(site.url, videopage)
        name = utils.safe_get_attr(link, "title") or utils.safe_get_text(link)
        name = utils.cleantext(name)
        if not name:
            continue
        img_tag = item.find("img")
        img = utils.safe_get_attr(
            img_tag, "data-src", ["src", "data-original", "data-lazy"]
        )
        if img:
            img = urllib_parse.urljoin(site.url, img)
        duration = ""
        clock = item.select_one(".fa-clock-o")
        if clock:
            duration = utils.cleantext(utils.safe_get_text(clock.parent))
        site.add_download_link(
            name,
            videopage,
            "xsharings.Play",
            img or site.image,
            name,
            contextm=cm,
            duration=duration,
        )

    next_link = None
    active = soup.select_one('a[aria-current="page"]')
    if active:
        next_li = active.find_parent("li")
        if next_li:
            next_li = next_li.find_next_sibling("li")
            if next_li:
                next_link = next_li.find("a", href=True)
    if next_link:
        href = utils.safe_get_attr(next_link, "href")
        if href:
            next_url = urllib_parse.urljoin(site.url, href)
            npnr = utils.safe_get_text(next_link)
            npnr = npnr if npnr.isdigit() else ""
            lpnr = ""
            page_numbers = []
            for anchor in soup.select("ul.pagination a"):
                text = utils.safe_get_text(anchor)
                if text.isdigit():
                    page_numbers.append(int(text))
            if page_numbers:
                lpnr = str(max(page_numbers))
            label = "Next Page"
            if npnr:
                label = "Next Page ({})".format(npnr)
                if lpnr:
                    label = "Next Page ({}/{})".format(npnr, lpnr)
            cm_page = (
                utils.addon_sys
                + "?mode="
                + "xsharings.GotoPage"
                + "&list_mode="
                + "xsharings.List"
                + "&url="
                + urllib_parse.quote_plus(next_url)
                + "&np="
                + str(npnr)
                + "&lp="
                + str(lpnr or 0)
            )
            cm = [("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")]
            site.add_dir(label, next_url, "List", site.img_next, contextm=cm)
    utils.eod()


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    for article in soup.select('article[id^="post"]'):
        link = article.find("a", href=True)
        if not link:
            continue
        name = utils.safe_get_attr(link, "title") or utils.safe_get_text(link)
        name = utils.cleantext(name)
        if not name:
            continue
        img_tag = article.find("img")
        img = utils.safe_get_attr(
            img_tag, "data-src", ["src", "data-original", "data-lazy"]
        )
        if img:
            img = urllib_parse.urljoin(site.url, img)
        site.add_dir(name, urllib_parse.urljoin(site.url, link["href"]), "List", img)
    next_link = None
    active = soup.select_one('a[aria-current="page"]')
    if active:
        next_li = active.find_parent("li")
        if next_li:
            next_li = next_li.find_next_sibling("li")
            if next_li:
                next_link = next_li.find("a", href=True)
    if next_link:
        href = utils.safe_get_attr(next_link, "href")
        if href:
            site.add_dir(
                "Next Page",
                urllib_parse.urljoin(site.url, href),
                "Categories",
                site.img_next,
            )
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
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url += keyword.replace(" ", "+")
        List(url)


@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url)
    iframematch = re.compile(
        r'<iframe src="([^"]+)"', re.DOTALL | re.IGNORECASE
    ).findall(html)
    if iframematch:
        sources = {i.split("/")[2]: i for i in iframematch}
        iframe = utils.selector("Select video host:", sources)
        if iframe:
            if vp.resolveurl.HostedMediaFile(iframe).valid_url():
                vp.play_from_link_to_resolve(iframe)
            else:
                iframehtml = utils.getHtml(iframe, url)
                packed = utils.get_packed_data(iframehtml)
                packed = "{" + packed.split("}")[0].split("{")[-1] + "}"
                packed = json.loads(packed)
                video_url = packed.get("hls2")
                if video_url:
                    vp.play_from_direct_link(video_url)
    else:
        utils.notify("Oh oh", "No video found")


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys + "?mode=xsharings.List&url=" + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Lookupinfo(url):
    lookup_list = [
        (
            "Actors",
            r'<a href="(https://xsharings.com/actor/[^"]+)" title="([^"]+)">',
            "",
        ),
        (
            "Categories",
            r'<a href="(https://xsharings.com/category/[^/]+/)" class="label" title="([^"]+)">',
            "",
        ),
    ]
    lookupinfo = utils.LookupInfo("", url, "xsharings.List", lookup_list)
    lookupinfo.getinfo()
