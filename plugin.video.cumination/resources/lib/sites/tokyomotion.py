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
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "tokyomotion",
    "[COLOR hotpink]TokyoMotion[/COLOR]",
    "https://www.tokyomotion.net/",
    "tokyomotion.png",
    "tokyomotion",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search?search_query={}&search_type=videos",
        "Search",
        site.img_search,
    )
    List(site.url + "videos?type=public&o=mr&page=1")
    utils.eod()


@site.register()
def List(url, page=1):
    listhtml = utils.getHtml(url, site.url)
    if "No Videos Found" in listhtml:
        utils.notify(msg="Nothing found")
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    cards = soup.select("div.well.well-sm") if soup else []
    if not cards:
        # Fallback to regex parsing if the layout is not as expected
        match = re.compile(
            r'well well-sm[^"]*?">\s*<a href="/([^"]+)".*?src="([^"]+)"\s*title="([^"]+)"(.*?)duration">([^<]+)<',
            re.DOTALL | re.IGNORECASE,
        ).findall(listhtml)
        for videopage, img, name, hd, duration in match:
            videopage = urllib_parse.urljoin(site.url, videopage)
            img = (img + "|Referer=" + site.url) if img else None
            hd = "HD" if "HD" in hd else ""
            site.add_download_link(
                utils.cleantext(name),
                videopage,
                "Playvid",
                img,
                name,
                duration=utils.cleantext(duration),
                quality=hd,
            )
    else:
        for card in cards:
            link = card.find("a", href=True)
            if not link:
                continue
            videopage = urllib_parse.urljoin(site.url, link["href"])

            img_tag = card.find("img")
            img = utils.safe_get_attr(img_tag, "data-src", ["src"])
            if img and img.startswith("//"):
                img = "https:" + img
            if img:
                img = img + "|Referer=" + site.url

            name = utils.safe_get_attr(link, "title") or utils.safe_get_text(link)
            name = utils.cleantext(name) if name else "Video"

            duration_tag = card.find(class_=lambda c: c and "duration" in c)
            duration = utils.cleantext(utils.safe_get_text(duration_tag))

            hd = ""
            text = card.get_text(" ", strip=True).upper()
            if "HD" in text:
                hd = "HD"

            site.add_download_link(
                name, videopage, "Playvid", img, name, duration=duration, quality=hd
            )

    next_link = soup.find("a", class_=lambda c: c and "prevnext" in c) if soup else None
    if next_link:
        next_href = utils.safe_get_attr(next_link, "href")
        if next_href:
            nurl = urllib_parse.urljoin(site.url, next_href.replace("&amp;", "&"))
            npage_nr = re.search(r"page=(\d+)", nurl)
            npage_label = "({})".format(npage_nr.group(1)) if npage_nr else ""
            site.add_dir(
                "Next Page {}".format(npage_label), nurl, "List", site.img_next
            )
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    videohtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(videohtml)
    sources = soup.find_all("source") if soup else []
    src = utils.safe_get_attr(sources[-1], "src") if sources else ""
    if not src:
        match = re.search(r'source src="([^"]+)"', videohtml, re.DOTALL | re.IGNORECASE)
        if match:
            src = match.group(1)
    if src:
        vp.play_from_direct_link(src + "|Referer={}".format(site.url))


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        List(url.format(keyword.replace(" ", "+")))


@site.register()
def Categories(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)
    items = soup.select("div.col-sm-6 a[href]") if soup else []
    for anchor in items:
        catpage = utils.safe_get_attr(anchor, "href")
        if not catpage:
            continue
        catpage = urllib_parse.urljoin(site.url, catpage)
        if "type=" not in catpage:
            sep = "&" if "?" in catpage else "?"
            catpage = catpage + "{}type=public&o=mr".format(sep)

        img_tag = anchor.find("img")
        img = utils.safe_get_attr(img_tag, "src")
        name = utils.safe_get_attr(anchor, "title") or utils.safe_get_text(anchor)
        if not name:
            continue
        site.add_dir(utils.cleantext(name), catpage, "List", img)
    utils.eod()
