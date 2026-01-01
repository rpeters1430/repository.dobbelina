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

import re
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "freeuseporn",
    "[COLOR hotpink]Freeuse Porn[/COLOR]",
    "https://www.freeuseporn.com/",
    "freeuseporn.png",
    "freeuseporn",
)


@site.register(default_mode=True)
def Main(url):
    site.add_dir(
        "[COLOR hotpink]Tags[/COLOR]", site.url + "tags/", "Tags", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/videos/",
        "Search",
        site.img_search,
    )
    List(site.url + "videos?o=mr&page=1")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, "")
    soup = utils.parse_html(listhtml)
    items = soup.select(".item")
    if not items:
        return
    for item in items:
        link = item.find_parent("a") or item.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage:
            continue
        img_tag = item.select_one("img")
        name = utils.cleantext(
            utils.safe_get_attr(img_tag, "alt", ["title"], default="")
        )
        if not name:
            name = utils.cleantext(
                utils.safe_get_attr(link, "title", default=utils.safe_get_text(link))
            )
        duration = utils.cleantext(
            utils.safe_get_text(item.select_one(".duration"), default="").strip()
        )
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
        videopage = urllib_parse.urljoin(site.url, videopage)

        contexturl = (
            utils.addon_sys
            + "?mode=freeuseporn.Lookupinfo"
            + "&url="
            + urllib_parse.quote_plus(videopage)
        )

        contextmenu = [
            ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + contexturl + ")")
        ]

        site.add_download_link(
            name,
            videopage,
            "Playvid",
            img,
            name,
            duration=duration,
            contextm=contextmenu,
        )

    next_link = soup.select_one(".page-link[href], a.page-link[href], a.next[href]")
    if next_link:
        next_url = utils.safe_get_attr(next_link, "href", default="")
        if next_url:
            site.add_dir("Next Page...", next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.play_from_site_link(url, url)


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(searchUrl, "Search")
    else:
        title = keyword.replace(" ", "-")
        searchUrl = searchUrl + title + "?o=mr&page=1"
        List(searchUrl)


@site.register()
def Tags(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)
    tags = []
    for link in soup.select('a[href*="/search/videos/"]'):
        tag = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(utils.safe_get_text(link, default=""))
        if not tag or not name:
            continue
        tag = tag.split("/search/videos/")[-1].strip("/")
        tags.append((tag, name))
    for tag, name in sorted(tags):
        site.add_dir(name, site.url + "search/videos/", "Search", "", keyword=tag)
    utils.eod()


@site.register()
def Lookupinfo(url):
    lookup_list = [
        (
            "Tag",
            r'href="/([^"]+)"><i\s*class="fas\s*fa-(?:th-list|tag)"></i>([^<]+)<',
            "",
        )
    ]

    lookupinfo = utils.LookupInfo(site.url, url, "freeuseporn.List", lookup_list)
    lookupinfo.getinfo()
