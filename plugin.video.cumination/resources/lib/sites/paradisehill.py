"""
Cumination site plugin
Copyright (C) 2015 Whitecream

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
import json

import xbmc
import xbmcgui
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "paradisehill",
    "[COLOR hotpink]ParadiseHill[/COLOR]",
    "https://en.paradisehill.cc/",
    "paradisehill.png",
    "paradisehill",
)

dialog = utils.dialog


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        "{0}categories/".format(site.url),
        "Cat",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Actors[/COLOR]",
        "{0}actors/?sort=name".format(site.url),
        "Cat",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Studios[/COLOR]",
        "{0}studios/?sort=title".format(site.url),
        "Cat",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search Films[/COLOR]",
        "{0}search/?pattern=&what=1".format(site.url),
        "Search",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Search Actors[/COLOR]",
        "{0}search/?pattern=&what=2".format(site.url),
        "Search",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Search Studios[/COLOR]",
        "{0}search/?pattern=&what=3".format(site.url),
        "Search",
        site.img_search,
    )
    List("{0}all/?sort=created_at".format(site.url))
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)
    for item in soup.select(".item"):
        link = item.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href", default="")
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"])
        name = utils.cleantext(
            utils.safe_get_text(item.select_one(".name"), default="")
        )
        if not videopage or not name:
            continue
        img = site.url[:-1] + img if img and img.startswith("/") else img
        videopage = (
            site.url[:-1] + videopage if videopage.startswith("/") else videopage
        )
        site.add_download_link(name, videopage, "Playvid", img, name)
    pagination = soup.select_one("ul.pagination")
    if pagination:
        npage = pagination.select_one("li.next a[href]")
        if npage:
            nurl = site.url[:-1] + utils.cleantext(
                utils.safe_get_attr(npage, "href", default="")
            )
            lastpg = ""
            last = pagination.select_one("li.last a[data-page]")
            if last:
                lastpg = utils.safe_get_attr(last, "data-page", default="")
            pgtxt = "Next Page (Currently in Page {} of {})".format(
                utils.safe_get_attr(npage, "data-page", default=""),
                int(lastpg) + 1 if lastpg else "",
            )
            site.add_dir(pgtxt, nurl, "List", site.img_next)
    utils.eod()


@site.register()
def Cat(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    for item in soup.select(".item"):
        link = item.select_one("a[href]")
        caturl = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(utils.safe_get_text(item.select_one("span"), default=""))
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"])
        if not caturl or not name:
            continue
        img = site.url[:-1] + img if img and img.startswith("/") else img
        catpage = site.url[:-1] + caturl if caturl.startswith("/") else caturl
        site.add_dir(utils.cleantext(name), catpage, "List", img)
    npage = soup.select_one("li.next a[href]")
    if npage:
        nurl = site.url[:-1] + utils.safe_get_attr(npage, "href", default="").replace(
            "&amp;", "&"
        )
        lp = ""
        last = soup.select_one("li.last a[data-page]")
        if last:
            lp = utils.safe_get_attr(last, "data-page", default="")
        site.add_dir(
            "Next Page (Currently in Page {} of {})".format(
                utils.safe_get_attr(npage, "data-page", default=""),
                int(lp) + 1 if lp else "",
            ),
            nurl,
            "Cat",
            site.img_next,
        )
    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "+")
        searchUrl = searchUrl.replace("&what=", title + "&what=")
        if "&what=1" in searchUrl:
            List(searchUrl)
        else:
            Cat(searchUrl)


@site.register()
def Playvid(url, name, download=None):
    playall = utils.addon.getSetting("paradisehill") == "true"
    videopage = utils.getHtml(url, site.url)
    videojson = re.compile("videoList = ([^;]+)", re.IGNORECASE | re.DOTALL).findall(
        videopage
    )[0]
    videodict = json.loads(videojson)

    videos = []
    for i, j in enumerate(videodict):
        videourl = videodict[i]["sources"][0]["src"]
        part = "Part {}/{}".format(i + 1, len(videodict))
        videos.append((videourl, part))

    # if len(videos) < 1:
    #    videos = re.compile(r'<source[^\n]+src="([^"]+)">([^<]+)', re.DOTALL | re.IGNORECASE).findall(videopage)

    if not playall:
        if len(videos) > 1:
            videolist = []
            for _, pname in videos:
                videolist.append(pname)
            videopart = dialog.select("Multiple videos found", videolist)
            if videopart == -1:
                return
            videourl = videos[videopart][0]
            if videourl.startswith("//"):
                videourl = "https:" + videourl
            name = "{0} - {1}".format(name, videos[videopart][1])
        else:
            videourl = videos[0][0]
        if videourl.startswith("//"):
            videourl = "https:" + videourl
        videourl = videourl + "|Referer={}".format(url)

    if download == 1 and not playall:
        if videourl.startswith("//"):
            videourl = "https:" + videourl
        utils.downloadVideo(videourl, name)
    else:
        iconimage = xbmc.getInfoImage("ListItem.Thumb")

        if playall:
            pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            pl.clear()
            for videourl, pname in videos:
                newname = name + " " + pname
                listitem = xbmcgui.ListItem(newname)
                listitem.setArt(
                    {
                        "thumb": iconimage,
                        "icon": "DefaultVideo.png",
                        "poster": iconimage,
                    }
                )
                if utils.KODIVER > 19.8:
                    vtag = listitem.getVideoInfoTag()
                    vtag.setTitle(newname)
                    vtag.setGenres(["Porn"])
                else:
                    listitem.setInfo("video", {"Title": newname, "Genre": "Porn"})
                listitem.setProperty("IsPlayable", "true")
                if videourl.startswith("//"):
                    videourl = "https:" + videourl
                videourl = "{0}|Referer={1}".format(videourl, url)
                pl.add(videourl, listitem)
                listitem = ""
            xbmc.Player().play(pl)
        else:
            if videourl.startswith("//"):
                videourl = "https:" + videourl
            vp = utils.VideoPlayer(name)
            vp.play_from_direct_link(videourl)
