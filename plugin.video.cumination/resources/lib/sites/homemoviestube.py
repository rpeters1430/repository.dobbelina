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
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "homemoviestube",
    "[COLOR hotpink]HomeMovies Tube[/COLOR]",
    "https://www.homemoviestube.com/",
    "homemoviestube.png",
    "homemoviestube",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "channels/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url + "most-recent/")
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)

    soup = utils.parse_html(html)
    for item in soup.select(".vidItem, .video, .video-item"):
        link = item.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage:
            continue
        videopage = urllib_parse.urljoin(site.url, videopage)
        name = utils.cleantext(utils.safe_get_text(link, default=""))
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])
        if img:
            img = urllib_parse.urljoin(site.url, img.replace(" ", "%20"))
        duration = utils.safe_get_text(item.select_one(".time"), default="")
        site.add_download_link(name, videopage, "Playvid", img, name, duration=duration)

    next_link = soup.select_one(".next a[href]")
    if next_link:
        np = urllib_parse.urljoin(url, utils.safe_get_attr(next_link, "href", default=""))
        curr_pg = utils.safe_get_text(soup.select_one(".current"), default="")
        last_pg = ""
        for link in soup.select(".pagination a"):
            text = utils.safe_get_text(link, default="")
            if text.isdigit():
                last_pg = text
        site.add_dir(
            "[COLOR hotpink]Next Page[/COLOR] (Currently in Page {0} of {1})".format(
                curr_pg, last_pg
            ),
            np,
            "List",
            site.img_next,
        )
    utils.eod()


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    entries = []
    for item in soup.select(".category-item"):
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])
        caturl = utils.safe_get_attr(item, "href", default="")
        name = utils.cleantext(utils.safe_get_text(item, default=""))
        if not caturl or not name:
            continue
        entries.append((img, caturl, name))
    entries = list({(img, caturl, name) for img, caturl, name in entries})
    entries.sort(key=lambda x: x[2])
    for img, caturl, name in entries:
        caturl = urllib_parse.urljoin(site.url, caturl)
        if img:
            img = urllib_parse.urljoin(site.url, img)
        site.add_dir(name, caturl, "List", img)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = url + keyword.replace(" ", "-") + "/page1.html"
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    video_page = utils.getHtml(url, site.url)

    source = re.compile(r'<source.+?src="([^"]+)', re.DOTALL | re.IGNORECASE).search(
        video_page
    )
    if source:
        vp.play_from_direct_link(source.group(1) + "|verifypeer=false")
    else:
        vp.progress.close()
        utils.notify("Oh Oh", "No Videos found")
        return
