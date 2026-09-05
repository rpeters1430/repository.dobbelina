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

import re
from urllib.parse import quote_plus, urljoin

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.decrypters.kvsplayer import kvs_decode

site = AdultSite(
    "porno24",
    "[COLOR hotpink]Porno24[/COLOR]",
    "https://porno24.to/",
    "porno24.png",
    "porno24",
    category="Video Tubes",
)
BASE_URL = "https://porno24.to/"


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", urljoin(BASE_URL, "categories/"), "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Top Rated[/COLOR]", urljoin(BASE_URL, "top-rated/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Most Popular[/COLOR]", urljoin(BASE_URL, "most-popular/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", urljoin(BASE_URL, "search/"), "Search", site.img_search)
    List(urljoin(BASE_URL, "latest-updates/"))
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    items = soup.select(".thumb.item, .list-videos .item")

    for item in items:
        link = item.select_one("a[href]")
        if not link:
            continue

        href = link.get("href")
        if not href or "/video/" not in href:
            continue

        video_url = urljoin(BASE_URL, href)
        title_el = item.select_one(".title")
        title = link.get("title") or (title_el.get_text(strip=True) if title_el else "Video")

        duration_el = item.select_one(".time")
        duration = duration_el.get_text(strip=True) if duration_el else ""

        quality_el = item.select_one(".qualtiy, .quality")
        quality = quality_el.get_text(strip=True) if quality_el else ""

        img = item.select_one("img")
        thumb = ""
        if img:
            thumb = img.get("src") or img.get("data-webp") or img.get("data-original") or ""
            if thumb and not thumb.startswith("http"):
                thumb = urljoin(BASE_URL, thumb)

        display_name = title
        if quality:
            display_name += f" [COLOR red]{quality}[/COLOR]"
        if duration:
            display_name += f" [COLOR yellow]({duration})[/COLOR]"

        site.add_download_link(
            display_name,
            video_url,
            "Playvid",
            thumb,
            duration=duration,
        )

    # Next page handling
    next_btn = soup.select_one(".pagination a.next")
    if next_btn:
        params = next_btn.get("data-parameters", "")
        m = re.search(r"from(?:_videos(?:\+from_albums)?)?:(\d+)", params)
        if m:
            next_page = m.group(1)
            if "search" in url:
                clean_base = re.sub(r"\?.*$", "", url)
                next_url = f"{clean_base}?from_videos={next_page}"
            else:
                clean_base = re.sub(r"/\d+/?$", "/", url)
                if not clean_base.endswith("/"):
                    clean_base += "/"
                next_url = f"{clean_base}{next_page}/"
            site.add_dir("[COLOR dodgerblue]Next Page...[/COLOR]", next_url, "List", site.img_next)

    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    items = soup.select(".thumb.item, .list-categories .item")

    for item in items:
        link = item.select_one("a[href]")
        if not link:
            continue

        href = link.get("href")
        if not href or "/categories/" not in href or href.endswith("/categories/"):
            continue

        cat_url = urljoin(BASE_URL, href)
        title_el = item.select_one(".title")
        title = link.get("title") or (title_el.get_text(strip=True) if title_el else "")
        if not title:
            continue

        count_el = item.select_one(".thumb-item")
        count = count_el.get_text(strip=True) if count_el else ""

        img = item.select_one("img")
        thumb = ""
        if img:
            thumb = img.get("src") or img.get("data-webp") or img.get("data-original") or ""
            if thumb and not thumb.startswith("http"):
                thumb = urljoin(BASE_URL, thumb)

        name = title
        if count:
            name += f" [COLOR yellow]({count})[/COLOR]"

        site.add_dir(name, cat_url, "List", thumb)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = urljoin(BASE_URL, f"search/{quote_plus(keyword)}/")
        List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    license_match = re.search(r"license_code:\s*'([^']+)'", html, re.IGNORECASE)
    license_code = license_match.group(1) if license_match else ""

    sources = {}
    for url_key, label_key, default_label in (
        ("video_url", "video_url_text", "720p"),
        ("video_alt_url", "video_alt_url_text", "1080p"),
        ("video_alt_url2", "video_alt_url2_text", "480p"),
        ("video_alt_url3", "video_alt_url3_text", "360p"),
        ("video_alt_url4", "video_alt_url4_text", "2160p"),
    ):
        url_match = re.search(r"{}:\s*'([^']+)'".format(url_key), html, re.IGNORECASE)
        if not url_match:
            continue
        stream_url = url_match.group(1)
        label_match = re.search(r"{}:\s*'([^']+)'".format(label_key), html, re.IGNORECASE)
        label = label_match.group(1) if label_match else default_label

        if stream_url.startswith("function/"):
            if license_code:
                try:
                    stream_url = kvs_decode(stream_url, license_code)
                except Exception:
                    stream_url = re.sub(r"^function/\d+/", "", stream_url)
            else:
                stream_url = re.sub(r"^function/\d+/", "", stream_url)

        if stream_url and stream_url.startswith("http"):
            sources[label] = stream_url

    if sources:
        stream_url = (
            utils.selector(
                "Select quality",
                sources,
                sort_by=lambda x: int(re.sub(r"\D", "", x) or 0),
                reverse=True,
            )
            if len(sources) > 1
            else next(iter(sources.values()))
        )
        if stream_url:
            ua = quote_plus(utils.USER_AGENT)
            headers_suffix = f"|Referer={url}&User-Agent={ua}"
            vp.play_from_direct_link(stream_url + headers_suffix)
            return

    vp.play_from_link_to_resolve(url)
