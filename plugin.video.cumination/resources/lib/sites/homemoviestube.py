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
    category="Amateur & Social",
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
    for item in soup.select(".vidItem, .video, .video-item, .media-card.video-card"):
        link = item.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage:
            continue
        videopage = urllib_parse.urljoin(site.url, videopage)
        img_tag = item.select_one("img")
        name = utils.cleantext(
            utils.safe_get_attr(link, "title", default="")
            or utils.safe_get_attr(img_tag, "title", ["alt"], default="")
            or utils.safe_get_text(link, default="")
        )
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])
        if img:
            img = urllib_parse.urljoin(site.url, img.replace(" ", "%20"))
        duration = utils.safe_get_text(
            item.select_one(".time, .duration-badge"), default=""
        )
        site.add_download_link(name, videopage, "Playvid", img, name, duration=duration)

    next_link = soup.select_one(
        "a[rel='next'], a[aria-label='Next'], .prev-next-item a[href], .next a[href]"
    )
    if next_link:
        np = urllib_parse.urljoin(
            url, utils.safe_get_attr(next_link, "href", default="")
        )
        curr_pg = utils.safe_get_text(soup.select_one(".current, .active"), default="")
        last_pg = ""
        for link in soup.select(".pagination a, a.page-link"):
            text = utils.safe_get_text(link, default="")
            if text.isdigit() and (not last_pg or int(text) > int(last_pg)):
                last_pg = text
        pg_info = (
            " (Currently in Page {0} of {1})".format(curr_pg, last_pg)
            if curr_pg and last_pg
            else ""
        )
        site.add_dir(
            "[COLOR hotpink]Next Page[/COLOR]{}".format(pg_info),
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
    for item in soup.select(".category-item, .channel-card"):
        link = item if item.name == "a" else item.select_one("a[href]")
        caturl = utils.safe_get_attr(link, "href", default="")
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"])
        name_tag = item.select_one(".channel-name") or link or item
        name = utils.cleantext(utils.safe_get_text(name_tag, default=""))
        badge = utils.safe_get_text(
            item.select_one(".channel-count-badge, .badge"), default=""
        )
        if badge:
            name += " [COLOR deeppink][{}][/COLOR]".format(badge)
        if not caturl or not name:
            continue
        entries.append((img, caturl, name))
    entries = list({e[1]: e for e in entries}.values())
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
        media_url = urllib_parse.quote(source.group(1), safe="/:?&=%")
        media_url = urllib_parse.urljoin(site.url, media_url)
        vp.play_from_direct_link(media_url + "|verifypeer=false")
    else:
        vp.progress.close()
        utils.notify("Oh Oh", "No Videos found")
        return
