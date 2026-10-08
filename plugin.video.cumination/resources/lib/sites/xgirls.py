"""
Cumination
Copyright (C) 2026 Team Cumination

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
from urllib.parse import quote_plus, urljoin

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "xgirls",
    "[COLOR hotpink]xGirls[/COLOR]",
    "https://xgirls.webcam/",
    "xgirls.png",
    "xgirls",
    category="Cams & Live",
)

# Only the main grid: the page also carries "Latest"/"Top Rated" teaser cards
# (div.card-col) that repeat videos and label every thumbnail "image".
VIDEO_LIST_SPEC = {
    "items": "div.list-videos div.item",
    "url": {"selector": "a[href*='/video/']", "attr": "href"},
    "title": {
        "selector": "a[title]",
        "attr": "title",
        "fallback_selectors": ["img[alt]"],
        "fallback_attrs": ["alt"],
    },
    "thumbnail": {
        "selector": "img",
        "attr": "data-original",
        "fallback_attrs": ["data-webp", "src"],
    },
    "duration": {"selector": ".duration", "text": True},
    "quality": {"selector": ".is-hd", "text": True},
}


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Top Rated[/COLOR]",
        site.url + "top-rated/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Most Popular[/COLOR]",
        site.url + "most-popular/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/{0}/",
        "Search",
        site.img_search,
    )
    List(site.url + "latest-updates/")
    utils.eod()


def _next_page(soup, current_url):
    link = soup.select_one("li.next a")
    if not link:
        return None
    href = utils.safe_get_attr(link, "href")
    if href and not href.startswith("#"):
        return urljoin(current_url, href)

    # Search results paginate through the KVS async block only.
    block_id = utils.safe_get_attr(link, "data-block-id")
    params = utils.safe_get_attr(link, "data-parameters")
    if not block_id or not params:
        return None
    query = ["mode=async", "function=get_block", "block_id=" + block_id]
    for pair in params.split(";"):
        keys, _, value = pair.partition(":")
        if not value:
            continue
        for key in re.split(r"[+ ]", keys):
            query.append("{}={}".format(key, quote_plus(value)))
    return current_url.split("?")[0] + "?" + "&".join(query)


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    utils.soup_videos_list(site, soup, VIDEO_LIST_SPEC)

    next_url = _next_page(soup, url)
    if next_url:
        site.add_dir("Next Page", next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)

    for link in soup.select("a.item[href*='/categories/']"):
        title = utils.safe_get_attr(link, "title") or utils.safe_get_text(
            link.select_one(".title")
        )
        if not title:
            continue
        thumb = utils.safe_get_attr(
            link.select_one("img"), "data-original", ["data-webp", "src"]
        )
        if thumb.startswith("data:"):
            thumb = ""
        count = utils.safe_get_text(link.select_one(".videos"))
        if count:
            title = "{} [COLOR hotpink]({})[/COLOR]".format(title, count)
        site.add_dir(
            title,
            urljoin(site.url, link["href"]),
            "List",
            urljoin(site.url, thumb) if thumb else site.img_cat,
        )

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    vpage = utils.getHtml(url, site.url)
    if re.search(r"video_url\s*:", vpage):
        vp.progress.update(60, "[CR]kt_player detected[CR]")
        vp.play_from_kt_player(vpage, url)
        return

    soup = utils.parse_html(vpage)
    source = soup.find("source", src=True) or soup.find("video", src=True)
    if source and source.get("src"):
        vp.play_from_direct_link(
            "{}|Referer={}".format(urljoin(url, source["src"]), site.url)
        )
    else:
        vp.progress.close()
        utils.notify("No playable stream found", "xGirls")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = url.format(quote_plus(keyword))
        List(search_url)
