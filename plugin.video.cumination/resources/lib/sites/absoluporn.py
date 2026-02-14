"""
Cumination
Copyright (C) 2016 Whitecream

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
import hashlib
import xbmcplugin
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "absoluporn",
    "[COLOR hotpink]AbsoluPorn[/COLOR]",
    "http://www.absoluporn.com/en",
    "absoluporn.png",
    "absoluporn",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Top Rated[/COLOR]",
        "{0}/wall-note-1.html".format(site.url),
        "List",
        "",
        "",
    )
    site.add_dir(
        "[COLOR hotpink]Most Viewed[/COLOR]",
        "{0}/wall-main-1.html".format(site.url),
        "List",
        "",
        "",
    )
    site.add_dir(
        "[COLOR hotpink]Longest[/COLOR]",
        "{0}/wall-time-1.html".format(site.url),
        "List",
        "",
        "",
    )
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url, "Cat", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        "{0}/search-".format(site.url),
        "Search",
        site.img_search,
    )
    List("{0}/wall-date-1.html".format(site.url))


@site.register()
def List(url):
    listhtml = utils.getHtml(url, "")
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return

    for item in soup.select(".thumb-main-titre"):
        link = item.select_one("a[href][title]")
        if not link:
            continue

        videourl = utils.safe_get_attr(link, "href", default="")
        if videourl.startswith(".."):
            videourl = videourl[2:]
        videopage = urllib_parse.urljoin(site.url[:-3], videourl)
        videopage = videopage.replace(" ", "%20")

        name = utils.cleantext(utils.safe_get_attr(link, "title", default=""))
        if not name:
            continue

        img_tag = link.select_one("img")
        img = utils.get_thumbnail(img_tag)

        info = item.select_one(".thumb-info")
        info_text = utils.safe_get_text(info, default="").lower()
        if "hd" in info_text:
            hd = "FULLHD" if "full" in info_text else "HD"
        else:
            hd = ""

        duration_elem = item.select_one(".time")
        duration = utils.safe_get_text(duration_elem, default="")

        site.add_download_link(
            name, videopage, "Playvid", img, name, duration=duration, quality=hd
        )

    next_link = soup.select_one("span.text16 + a[href]")
    if next_link:
        nextp = utils.safe_get_attr(next_link, "href", default="")
        if nextp.startswith(".."):
            nextp = nextp[2:]
        if nextp:
            nextp = nextp.replace(" ", "%20")
            site.add_dir("Next Page", site.url[:-3] + nextp, "List", site.img_next)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, "")
    r = re.compile(r'<source\s*src="([^"]+)', re.DOTALL | re.IGNORECASE).search(
        videopage
    )
    if r:
        videourl = r.group(1)
    else:
        servervideo = re.compile(
            "servervideo = '([^']+)'", re.DOTALL | re.IGNORECASE
        ).findall(videopage)[0]
        vpath = re.compile("path = '([^']+)'", re.DOTALL | re.IGNORECASE).findall(
            videopage
        )[0]
        coda, repp = re.compile(
            r"repp = (codage\()*'([^']+)'", re.DOTALL | re.IGNORECASE
        ).findall(videopage)[0]
        filee = re.compile("filee = '([^']+)'", re.DOTALL | re.IGNORECASE).findall(
            videopage
        )[0]
        if coda:
            repp = hashlib.md5(repp).hexdigest()
        videourl = servervideo + vpath + repp + filee
    vp.play_from_direct_link(videourl)


@site.register()
def Cat(url):
    cathtml = utils.getHtml(url, "")
    soup = utils.parse_html(cathtml)
    if not soup:
        utils.eod()
        return

    catsec = soup.select_one(".categorie")
    if not catsec:
        utils.eod()
        return

    for link in catsec.select("a[href]"):
        caturl = utils.safe_get_attr(link, "href", default="")
        if caturl.startswith(".."):
            caturl = caturl[2:]
        catpage = site.url[:-3] + caturl

        name = utils.cleantext(utils.safe_get_text(link, default=""))
        if not name:
            continue

        items = ""
        li = link.find_parent("li")
        if li:
            count_elem = li.find("span")
            items = utils.safe_get_text(count_elem, default="")

        label = name + " [COLOR deeppink]" + items + "[/COLOR]" if items else name
        site.add_dir(label, catpage, "List", "")
    xbmcplugin.addSortMethod(utils.addon_handle, xbmcplugin.SORT_METHOD_TITLE)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "%20")
        searchUrl = searchUrl + title + "-1.html"
        List(searchUrl)
