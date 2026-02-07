"""
Cumination
Copyright (C) 2020 Team Cumination

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

site = AdultSite(
    "xtheatre",
    "[COLOR hotpink]Xtheatre[/COLOR]",
    "https://pornxtheatre.com/",
    "xtheatre.png",
    "xtheatre",
)

addon = utils.addon

sortlistxt = [
    addon.getLocalizedString(30022),
    addon.getLocalizedString(30023),
    addon.getLocalizedString(30024),
    addon.getLocalizedString(30025),
]


@site.register(default_mode=True)
def XTMain():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "XTCat",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "XTSearch", site.img_search
    )
    Sort = (
        "[COLOR hotpink]Current sort:[/COLOR] "
        + sortlistxt[int(addon.getSetting("sortxt"))]
    )
    site.add_dir(Sort, "", "XTSort", "", "")
    XTList(site.url + "?filter=latest", 1)
    utils.eod()


@site.register()
def XTSort():
    addon.openSettings()
    XTMain()


@site.register()
def XTCat(url):
    nextpg = True
    visited = set()
    while nextpg:
        if url in visited:
            break
        visited.add(url)
        cathtml = utils.getHtml(url, "")
        soup = utils.parse_html(cathtml)
        for article in soup.select("article"):
            link = article.select_one("a[href]") or article
            catpage = utils.safe_get_attr(link, "href", default="")
            name = utils.safe_get_attr(link, "title", default="")
            if not name:
                name = utils.safe_get_text(article.select_one(".title"), default="")
            img_tag = article.select_one("img")
            img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
            if not catpage:
                continue
            catpage = (
                catpage + "page/1/" if catpage.endswith("/") else catpage + "/page/1/"
            )
            site.add_dir(name, catpage, "XTList", img, 1)
        np = soup.select_one(".pagination .current a[href]")
        if np:
            url = utils.safe_get_attr(np, "href", default="")
            nextpg = bool(url)
        else:
            nextpg = False
    utils.eod()


@site.register()
def XTSearch(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "XTSearch")
    else:
        title = keyword.replace(" ", "+")
        searchUrl = searchUrl + title
        XTList(searchUrl, 1)


@site.register()
def XTList(url, page=1):
    sort = getXTSortMethod()
    if re.search(r"\?", url, re.DOTALL | re.IGNORECASE):
        url = url + "&filter=" + sort
    else:
        url = url + "?filter=" + sort

    listhtml = utils.getHtml(url, "")
    soup = utils.parse_html(listhtml)
    for article in soup.select("article"):
        link = article.select_one("a[href]") or article
        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage:
            continue
        name = utils.safe_get_attr(link, "title", default="")
        if not name:
            name = utils.safe_get_text(article.select_one(".title"), default="")
        img_tag = article.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
        name = utils.cleantext(name)
        site.add_download_link(name, videopage, "XTVideo", img, name)

    npage = soup.find("a", string=re.compile(r"Next", re.IGNORECASE))
    if npage:
        site.add_dir(
            "Next Page ...",
            utils.safe_get_attr(npage, "href", default=""),
            "XTList",
            site.img_next,
            npage,
        )
    else:
        np = soup.select_one(".pagination .current a[href]")
        if np:
            site.add_dir(
                "Next Page ...",
                utils.safe_get_attr(np, "href", default=""),
                "XTList",
                site.img_next,
            )
    utils.eod()


@site.register()
def XTVideo(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    videohtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(videohtml)
    iframe = soup.select_one(".player iframe[src], iframe[src]")
    embedurl = utils.safe_get_attr(iframe, "src", default="")
    if embedurl:
        if "streamup" in embedurl or "strmup" in embedurl:
            embedhtml = utils.getHtml(embedurl, site.url)
            match = re.search(
                r'streaming_url:"([^"]+)', embedhtml, re.DOTALL | re.IGNORECASE
            )
            if match:
                referer = embedurl.split("/")[2]
                videolink = match.group(
                    1
                ) + "|referer=https://{0}/&origin=https://{0}".format(referer)
                vp.play_from_direct_link(videolink)
                return
    vp.play_from_site_link(url, url)


def getXTSortMethod():
    sortoptions = {0: "date", 1: "title", 2: "views", 3: "likes"}
    sortvalue = addon.getSetting("sortxt")
    return sortoptions[int(sortvalue)]
