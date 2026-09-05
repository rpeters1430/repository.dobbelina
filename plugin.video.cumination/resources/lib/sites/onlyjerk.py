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

from __future__ import annotations

import base64
import re
from urllib.parse import quote_plus, urljoin

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "onlyjerk",
    "[COLOR hotpink]OnlyJerk[/COLOR]",
    "https://onlyjerk.net/",
    "onlyjerk.png",
    "onlyjerk",
    category="Amateur & Social",
)
BASE_URL = "https://onlyjerk.net/"


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Latest[/COLOR]", urljoin(BASE_URL, "latest-videos/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Top Weekly[/COLOR]", urljoin(BASE_URL, "popular-recent/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Most Viewed[/COLOR]", urljoin(BASE_URL, "most-viewed/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Trending[/COLOR]", urljoin(BASE_URL, "trending/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]OnlyFans[/COLOR]", urljoin(BASE_URL, "onlyfans/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Camwhores[/COLOR]", urljoin(BASE_URL, "camwhores/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Fansly[/COLOR]", urljoin(BASE_URL, "fansly/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]ManyVids[/COLOR]", urljoin(BASE_URL, "manyvids/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Asian[/COLOR]", urljoin(BASE_URL, "asian/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Porn[/COLOR]", urljoin(BASE_URL, "porn/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", urljoin(BASE_URL, "?s="), "Search", site.img_search)
    List(urljoin(BASE_URL, "latest-videos/"))
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    items = soup.select(".td_module_wrap")

    for item in items:
        link = item.select_one("h3.entry-title a, a.td-image-wrap")
        if not link:
            continue

        href = link.get("href")
        if not href:
            continue

        video_url = urljoin(BASE_URL, href)
        title = link.get("title") or link.get_text(strip=True) or "Video"

        # Thumbnail extraction (CSS background-image or img src)
        thumb = ""
        thumb_span = item.select_one(".entry-thumb")
        if thumb_span:
            style = thumb_span.get("style", "")
            m = re.search(r'url\([\'"]?(.*?)[\'"]?\)', style)
            if m:
                thumb = m.group(1).strip()

        if not thumb:
            img = item.select_one("img")
            if img:
                thumb = img.get("src") or img.get("data-src") or img.get("data-original") or ""

        if thumb and not thumb.startswith("http"):
            thumb = urljoin(BASE_URL, thumb)

        site.add_download_link(
            title,
            video_url,
            "Playvid",
            thumb,
        )

    # Next page navigation
    next_btn = soup.select_one(".page-nav a[aria-label='next-page'], .pagination a[aria-label='next-page']")
    if not next_btn:
        # Fallback: check for page links greater than current page
        current = soup.select_one(".page-nav .current, .pagination .current")
        if current:
            try:
                curr_page = int(current.get_text(strip=True))
                next_page_link = soup.select_one(f".page-nav a[title='{curr_page + 1}']")
                if next_page_link and next_page_link.get("href"):
                    next_btn = next_page_link
            except (ValueError, TypeError):
                pass

    if next_btn and next_btn.get("href"):
        next_url = urljoin(BASE_URL, next_btn["href"])
        site.add_dir("[COLOR dodgerblue]Next Page...[/COLOR]", next_url, "List", site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = urljoin(BASE_URL, f"?s={quote_plus(keyword)}")
        List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    soup = utils.parse_html(html)
    sources = []

    # Check for encoded iframe data-enc
    for ifr in soup.select("iframe[data-enc]"):
        enc = ifr.get("data-enc")
        if not enc:
            continue
        try:
            decoded = base64.b64decode(enc).decode("utf-8", errors="ignore").strip()
            if decoded.startswith("http") and decoded not in sources:
                sources.append(decoded)
        except Exception:
            continue

    # Check for standard iframe sources
    for ifr in soup.select("iframe[src]"):
        src = ifr.get("src", "").strip()
        if src and src.startswith("http") and "about:blank" not in src and src not in sources:
            sources.append(src)

    if sources:
        vp.play_from_link_list(sources)
        return

    vp.play_from_link_to_resolve(url)
