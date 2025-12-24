"""
Cumination
Copyright (C) 2024 Team Cumination

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
    "sexyporn",
    "[COLOR hotpink]SexyPorn[/COLOR]",
    "https://www.sexyporn.xxx/",
    "sexyporn.png",
    "sexyporn",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        urllib_parse.urljoin(site.url, "categories"),
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        urllib_parse.urljoin(site.url, "search"),
        "Search",
        site.img_search,
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    if not soup:
        utils.eod()
        return

    for item in soup.select(".video-item"):
        link = item.select_one("a.video-link[href]") or item.select_one("a[href]")
        if not link:
            continue

        videourl = urllib_parse.urljoin(
            site.url, utils.safe_get_attr(link, "href", default="")
        )
        name = utils.cleantext(
            utils.safe_get_attr(
                link, "title", default=utils.safe_get_text(link, default="")
            )
        )
        if not videourl or not name:
            continue

        thumb = utils.safe_get_attr(item.select_one("img"), "data-src", ["src"])
        duration = utils.safe_get_text(item.select_one(".duration"), default="")
        quality = "HD" if item.find(string=re.compile(r"\bHD\b", re.IGNORECASE)) else ""

        site.add_download_link(
            name, videourl, "Playvid", thumb, name, duration=duration, quality=quality
        )

    pagination = soup.select_one('a[rel="next"]') or soup.select_one("a.next[href]")
    if pagination:
        next_url = urllib_parse.urljoin(
            url, utils.safe_get_attr(pagination, "href", default="")
        )
        page_match = re.search(r"(\d+)(?!.*\d)", next_url)
        page_num = page_match.group(1) if page_match else ""
        label = f"Next Page ({page_num})" if page_num else "Next Page"
        site.add_dir(label, next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    if not soup:
        utils.eod()
        return

    for link in soup.select(".category-list a[href], a.category[href]"):
        caturl = urllib_parse.urljoin(
            site.url, utils.safe_get_attr(link, "href", default="")
        )
        name = utils.cleantext(utils.safe_get_text(link, default=""))
        if not caturl or not name:
            continue
        site.add_dir(name, caturl, "List", "")
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        query = keyword.replace(" ", "+")
        search_url = urllib_parse.urljoin(site.url, f"search/?s={query}")
        List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videohtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(videohtml)

    if soup:
        source = soup.select_one("video source[src]")
        if source:
            videourl = utils.safe_get_attr(source, "src", default="")
            if videourl:
                vp.play_from_direct_link(f"{videourl}|referer={site.url}")
                return

        iframe = soup.select_one("iframe[src]")
        if iframe:
            iframe_url = utils.safe_get_attr(iframe, "src", default="")
            if iframe_url:
                vp.play_from_link_to_resolve(iframe_url)
                return

    # Fallback to regex if soup parsing fails
    match = re.search(r'source src="([^"]+)"', videohtml)
    if match:
        vp.play_from_direct_link(match.group(1) + "|referer=" + site.url)
        return

    utils.notify("Oh oh", "Couldn't find a playable link")
