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
import json

site = AdultSite(
    "familypornhd",
    "[COLOR hotpink]Familypornhd[/COLOR]",
    "https://familypornhd.com/",
    "familypornhd.png",
    "familypornhd",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Channels[/COLOR]",
        site.url + "channels/",
        "Channels",
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
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url)
    if "You have requested a page or file which doesn't exist" in html:
        utils.notify(msg="Nothing found")
        utils.eod()
        return

    html = html.split(">Trending Porn<")[0]
    soup = utils.parse_html(html)

    for item in soup.select("article, .entry-tpl-grid, .video-item"):
        link = item.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage:
            continue
        name = utils.cleantext(
            utils.safe_get_attr(link, "title", default=utils.safe_get_text(link))
        )
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
        site.add_download_link(
            name,
            videopage,
            "familypornhd.Playvid",
            img,
            name,
            contextm="familypornhd.Related",
        )

    next_link = soup.select_one('a[rel="next"], a.next, .pagination a.next')
    if next_link:
        next_url = utils.safe_get_attr(next_link, "href", default="")
        if next_url:
            site.add_dir(
                "Next Page",
                next_url,
                "familypornhd.List",
                site.img_next,
                contextm="familypornhd.GotoPage",
            )
    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = url.replace("/page/{}".format(np), "/page/{}".format(pg))
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
        + str("familypornhd.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Channels(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    for item in soup.select("li"):
        link = item.select_one("a[href]")
        caturl = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(utils.safe_get_text(item.select_one("h4"), default=""))
        count = utils.safe_get_text(item.select_one("strong"), default="").strip()
        style = utils.safe_get_attr(link, "style", default="")
        img = ""
        if "background-image" in style:
            match = re.search(r"url\(([^)]+)\)", style)
            if match:
                img = match.group(1)
        if not caturl or not name:
            continue
        if count:
            name = name + "[COLOR hotpink] ({})[/COLOR]".format(count)
        site.add_dir(name, caturl, "List", img)
    utils.eod()


@site.register()
def Pornstars(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    for item in soup.select(".wp-caption"):
        link = item.select_one("a[href]")
        caturl = utils.safe_get_attr(link, "href", default="")
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"])
        name = utils.safe_get_text(item.select_one(".wp-caption-text"), default="")
        if not caturl or not name:
            continue
        site.add_dir(name, caturl, "List", img)
    utils.eod()


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    for link in soup.select("a[href]"):
        name = utils.safe_get_text(link, default="").strip()
        if not name:
            continue
        caturl = utils.safe_get_attr(link, "href", default="")
        if not caturl:
            continue
        if "categories" not in caturl:
            continue
        site.add_dir(name.title(), caturl, "List", "")
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}".format(url, keyword.replace(" ", "%20"))
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download, regex='<a href="([^"]+)" target="_blank"')
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videohtml = utils.getHtml(url, site.url)

    match = re.compile(
        'class="embed-container"><iframe.*?src="([^"]+)"', re.IGNORECASE | re.DOTALL
    ).findall(videohtml)
    if match:
        iframeurl = match[0]
        hash = iframeurl.split("/")[-1]
        if "bestwish.lol" in iframeurl:
            url1 = "https://bestwish.lol/ajax/stream?filecode={}".format(hash)
            html = utils.getHtml(url1, "https://bestwish.lol/")
            jsondata = json.loads(html)
            videourl = jsondata["streaming_url"]
            videourl += "|Referer=https://bestwish.lol/&Origin=https://bestwish.lol"
            vp.play_from_direct_link(videourl)
        elif "video-mart.com" in iframeurl or "videostreamingworld.com" in iframeurl:
            host = iframeurl.rsplit("/", 2)[0]
            url1 = "{}/player/index.php?data={}&do=getVideo".format(host, hash)
            hdr = dict(utils.base_hdrs).copy()
            hdr["Accept"] = "*/*"
            hdr["X-Requested-With"] = "XMLHttpRequest"
            data = {"hash": hash, "r": ""}
            html = utils.getHtml(url1, iframeurl, headers=hdr, data=data)
            jsondata = json.loads(html)
            videourl = jsondata["videoSource"]
            m3u8html = utils.getHtml(videourl, iframeurl, headers=hdr)
            lines = m3u8html.splitlines()
            for i, line in enumerate(lines):
                if line.startswith("/"):
                    lines[i] = host + line
                if 'URI="/' in line:
                    lines[i] = line.replace('URI="/', 'URI="{}/'.format(host))
            m3u8html = "\n".join(lines)
            myplaylist = utils.TRANSLATEPATH("special://temp/myPlaylist.mp4")
            with open(myplaylist, "w", encoding="utf-8") as f:
                f.write(m3u8html)
            vp.play_from_direct_link(myplaylist)
        else:
            host = iframeurl.rsplit("/", 1)[0]
            url1 = host + "/data.php?filecode=" + hash
            html = utils.getHtml(url1, iframeurl)
            jsondata = json.loads(html)
            videourl = jsondata["streaming_url"]
            vp.play_from_direct_link(videourl)
