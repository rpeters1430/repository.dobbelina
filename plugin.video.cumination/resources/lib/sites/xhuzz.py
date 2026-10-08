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

from urllib.parse import quote_plus, urljoin

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "xhuzz",
    "[COLOR hotpink]xHuzz[/COLOR]",
    "https://xhuzz.com/",
    "xhuzz.png",
    "xhuzz",
    category="Video Tubes",
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
        site.url + "search?q={0}",
        "Search",
        site.img_search,
    )
    List(site.url + "videos")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    spec = {
        "items": "div:has(> a[href*='/video/']), div.snap-start",
        "url": {"selector": "a[href*='/video/']", "attr": "href"},
        "title": {
            "selector": "img[alt]",
            "attr": "alt",
            "fallback_selectors": ["a[aria-label]", "h3", "span"],
        },
        "thumbnail": {
            "selector": "img",
            "attr": "src",
            "fallback_attrs": ["data-src"],
        },
        "pagination": {
            "selector": "a[href*='page='], .pagination a",
            "attr": "href",
        },
    }

    utils.soup_videos_list(site, soup, spec)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)

    for link in soup.select("a[href*='/category/'], a[href*='/tag/']"):
        href = urljoin(site.url, link.get("href", ""))
        img = link.find("img")
        thumb = img.get("src") if img else site.img_cat
        title = link.get_text(strip=True) or (img.get("alt") if img else "")
        if title:
            site.add_dir(title, href, "List", thumb)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    vpage = utils.getHtml(url, site.url)
    soup = utils.parse_html(vpage)

    # 1. Check for source buttons with resolver URLs
    btns = soup.select(".source-btn[data-src]")
    sources = [b["data-src"] for b in btns if b.get("data-src")]

    # 2. Check for iframes or videos
    if not sources:
        iframe = soup.find("iframe", id="video-player") or soup.find("iframe", src=True)
        if iframe and iframe.get("src"):
            sources.append(iframe["src"])

    if sources:
        vp.progress.update(60, "[CR]Resolving stream[CR]")
        for src in sources:
            src = urljoin(url, src)
            if vp.play_from_link(src):
                return

    utils.notify("No playable stream found", "xHuzz")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = url.format(quote_plus(keyword))
        List(search_url)
