"""
Cumination
Copyright (C) 2021 Team Cumination

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
import time
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "watcherotic",
    "[COLOR hotpink]WatchErotic[/COLOR]",
    "https://watcherotic.com/",
    "watcherotic.png",
    "watcherotic",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url + "latest-updates/")


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    html = listhtml.split(">SHOULD WATCH<")[0]
    if "There is no data in this list" in html.split("New Albums")[0]:
        utils.notify(msg="No data found")
        return

    skip = "(Magazine)"

    cm = []
    cm_lookupinfo = utils.addon_sys + "?mode=watcherotic.Lookupinfo&url="
    cm.append(
        ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + cm_lookupinfo + ")")
    )
    cm_related = utils.addon_sys + "?mode=watcherotic.Related&url="
    cm.append(
        ("[COLOR deeppink]Related videos[/COLOR]", "RunPlugin(" + cm_related + ")")
    )

    soup = utils.parse_html(html)
    thumbnails = utils.Thumbnails(site.name) if "watcherotic" in site.url else None

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

    for item in soup.select(".thumb.thumb_rel.item"):
        link = item.find("a", href=True)
        if not link:
            continue
        videopage = urllib_parse.urljoin(site.url, link["href"])
        name = utils.safe_get_attr(link, "title")
        if not name:
            name = utils.safe_get_text(link)
        name = utils.cleantext(name)
        if not name or (skip and skip in name):
            continue
        img_tag = item.find("img")
        img = utils.safe_get_attr(
            img_tag, "data-original", ["data-src", "data-lazy", "src"]
        )
        if img:
            img = urllib_parse.urljoin(site.url, img)
            if thumbnails:
                img = thumbnails.fix_img(img)
        duration = utils.cleantext(
            utils.safe_get_text(item.select_one(".time"))
        )
        quality = utils.cleantext(
            utils.safe_get_text(item.select_one(".quality"))
        )
        site.add_download_link(
            name,
            videopage,
            "watcherotic.Play",
            img or site.image,
            name,
            duration=duration,
            quality=quality,
            contextm=_context_menu(videopage),
        )

    pagination_soup = utils.parse_html(listhtml)
    next_link = pagination_soup.find(
        "a", class_="next", attrs={"data-action": "ajax"}
    )
    if next_link:
        block_id = next_link.get("data-block-id")
        params = next_link.get("data-parameters", "")
        active = pagination_soup.select_one(".pagination .active") or pagination_soup.select_one(
            ".active"
        )
        current = utils.safe_get_text(active).strip() if active else ""
        if block_id and params and current.isdigit():
            npage = int(current) + 1
            params = params.replace(";", "&").replace(":", "=")
            tm = int(time.time() * 1000)
            nurl = (
                url.split("?")[0]
                + "?mode=async&function=get_block&block_id={0}&{1}&_={2}".format(
                    block_id, params, str(tm)
                )
            )
            nurl = nurl.replace("+from_albums", "")
            nurl = re.sub(r"&from([^=]*)=\d+", r"&from\1={}".format(npage), nurl)

            cm_page = (
                utils.addon_sys
                + "?mode=watcherotic.GotoPage"
                + "&url="
                + urllib_parse.quote_plus(nurl)
                + "&np="
                + str(npage)
                + "&list_mode=watcherotic.List"
            )
            cm_page = [("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")]

            site.add_dir(
                "[COLOR hotpink]Next Page...[/COLOR] (" + str(npage) + ")",
                nurl,
                "List",
                site.img_next,
                contextm=cm_page,
            )
    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp=0):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = url.replace("/page/{}".format(np), "/page/{}".format(pg))
        url = url.replace("from={}".format(np), "from={}".format(pg))
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
def Cat(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    tag_cloud = soup.select_one(".wp-block-tag-cloud") or soup
    for link in tag_cloud.select("a[aria-label][href]"):
        name = utils.cleantext(utils.safe_get_attr(link, "aria-label"))
        caturl = utils.safe_get_attr(link, "href")
        if not name or not caturl:
            continue
        site.add_dir(name, caturl, "List", "")
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}/".format(url, keyword.replace(" ", "-"))
        List(url)


@site.register()
def Play(url, name, download=None):
    videohtml = utils.getHtml(url, site.url)

    vp = utils.VideoPlayer(
        name, download=download, regex='"file":"([^"]+)"', direct_regex='file:"([^"]+)"'
    )
    match = re.compile(
        r"""<iframe[^>]+src=['"](h[^'"]+)['"]""", re.DOTALL | re.IGNORECASE
    ).findall(videohtml)
    playerurl = match[0]
    embedhtml = utils.getHtml(playerurl, url)
    match = re.compile(r"video_url:\s*'([^']+)'", re.DOTALL | re.IGNORECASE).findall(
        embedhtml
    )
    if match:
        videolink = match[0] + "|referer=" + site.url
        vp.play_from_direct_link(videolink)


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Tag", r'<a href="{}(tags/[^"]+)">([^<]+)</a>'.format(site.url), ""),
        ("Actor", r'/(models/[^"]+)">.+?</i>([^<]+)</a>', ""),
    ]

    lookupinfo = utils.LookupInfo(
        site.url, url, "{}.List".format(site.module_name), lookup_list
    )
    lookupinfo.getinfo()


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("watcherotic.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")
