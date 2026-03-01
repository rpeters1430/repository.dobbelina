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

import xbmc
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "tabootube",
    "[COLOR hotpink]TabooTube[/COLOR]",
    "https://www.tabootube.xxx/",
    "tabootube.png",
    "tabootube",
)


@site.register(default_mode=True)
def Main(url):
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Tags[/COLOR]", site.url + "tags/", "Tags", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(
        site.url
        + "?mode=async&function=get_block&block_id=list_videos_most_recent_videos&sort_by=post_date&from=1",
        1,
    )
    utils.eod()


@site.register()
def List(url, page=1):
    try:
        listhtml = utils.getHtml(url, "")
        if not listhtml:
            utils.kodilog(
                f"TabooTube: Got empty response for list page {page} at {url}",
                xbmc.LOGWARNING,
            )
            utils.eod()
            return
    except Exception as exc:
        utils.kodilog(
            f"TabooTube: Failed to fetch list page {page}: {exc}", xbmc.LOGERROR
        )
        raise

    soup = utils.parse_html(listhtml)
    items = soup.select(".item")
    for item in items:
        link = item.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage:
            continue

        videopage = urllib_parse.urljoin(site.url, videopage)
        name = utils.cleantext(
            utils.safe_get_attr(link, "title", default=utils.safe_get_text(link))
        )
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-original", ["data-src", "src"])
        if img:
            img = urllib_parse.urljoin(site.url, img)
        duration = utils.safe_get_text(item.select_one(".duration"), default="")

        contextmenu = []
        contexturl = (
            utils.addon_sys
            + "?mode="
            + str("tabootube.Lookupinfo")
            + "&url="
            + urllib_parse.quote_plus(videopage)
        )
        contextmenu.append(
            ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + contexturl + ")")
        )

        site.add_download_link(
            name,
            videopage,
            "Playvid",
            img,
            name,
            contextm=contextmenu,
            duration=duration,
        )

    np = None
    next_el = soup.select_one(".next[data-page], .pagination .next a, a.next")
    if next_el:
        next_val = utils.safe_get_attr(next_el, "data-page", ["href"])
        if next_val:
            match = re.search(r"from=(\d+)", next_val)
            if match:
                np = match.group(1)
            elif next_val.isdigit():
                np = next_val

    if not np:
        match = re.search(
            r'class="next">.*?post_date;from:(\d+)"',
            listhtml,
            re.DOTALL | re.IGNORECASE,
        )
        if match:
            np = match.group(1)

    if np:
        if "from=" in url:
            nextp = re.sub(r"from=\d+", "from={}".format(np), url)
        else:
            nextp = url
        site.add_dir("Next Page ({})".format(np), nextp, "List", site.img_next, page=np)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    vpage = utils.getHtml(url, site.url)
    if "kt_player('kt_player'" in vpage:
        vp.progress.update(60, "[CR]{0}[CR]".format("kt_player detected"))
        vp.play_from_kt_player(vpage, url)


@site.register()
def Categories(url):
    try:
        cathtml = utils.getHtml(url, "")
        if not cathtml:
            utils.kodilog(
                f"TabooTube: Got empty response for categories at {url}",
                xbmc.LOGWARNING,
            )
            utils.eod()
            return
    except Exception as exc:
        utils.kodilog(f"TabooTube: Failed to fetch categories: {exc}", xbmc.LOGERROR)
        raise
    soup = utils.parse_html(cathtml)
    for link in soup.select("a.item[href][title]"):
        catpage = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(utils.safe_get_attr(link, "title", default=""))
        if not catpage or not name:
            continue
        catpage = urllib_parse.urljoin(site.url, catpage)
        catpage = (
            catpage
            + "?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=1"
        )
        site.add_dir(name, catpage, "List", "", page=1)
    utils.eod()


@site.register()
def Tags(url):
    try:
        taghtml = utils.getHtml(url, "")
        if not taghtml:
            utils.kodilog(
                f"TabooTube: Got empty response for tags at {url}", xbmc.LOGWARNING
            )
            utils.eod()
            return
    except Exception as exc:
        utils.kodilog(f"TabooTube: Failed to fetch tags: {exc}", xbmc.LOGERROR)
        raise
    soup = utils.parse_html(taghtml)
    for link in soup.select('a[href*="/tags/"], a[href*="tags/"]'):
        tagpage = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(utils.safe_get_text(link, default=""))
        if not tagpage or not name:
            continue
        tagpage = urllib_parse.urljoin(site.url, tagpage)
        tagpage = (
            tagpage
            + "?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=1"
        )
        site.add_dir(name, tagpage, "List", "", page=1)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "-")
        searchUrl = (
            searchUrl
            + title
            + "?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=1"
        )
        List(searchUrl, 1)


@site.register()
def Lookupinfo(url):
    class TabootubeLookup(utils.LookupInfo):
        def url_constructor(self, url):
            ajaxpart = "?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=1"
            if "categories/" in url:
                return url + ajaxpart
            if any(x in url for x in ["models/", "tags/"]):
                return site.url + url + ajaxpart

    lookup_list = [
        ("Cat", r'Categories:\s*?<a href="([^"]+)">([^<]+)<', ""),
        ("Tag", '/(tags/[^"]+)">([^<]+)<', ""),
        ("Actor", '/(models/[^"]+)">([^<]+)<', ""),
        # ("Studio", r'/(studios[^"]+)">([^<]+)</a>', ''),
    ]

    lookupinfo = TabootubeLookup(site.url, url, "tabootube.List", lookup_list)
    lookupinfo.getinfo()
