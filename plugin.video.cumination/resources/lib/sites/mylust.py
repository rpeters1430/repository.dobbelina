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

site = AdultSite(
    "mylust",
    "[COLOR hotpink]MyLust[/COLOR]",
    "https://mylust.com/",
    "mylust.png",
    "mylust",
    category="Video Tubes",
)
BASE_URL = "https://mylust.com/"


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", urljoin(BASE_URL, "categories/"), "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Best Videos[/COLOR]", urljoin(BASE_URL, "best/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]New Videos[/COLOR]", urljoin(BASE_URL, "latest-updates/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Most Viewed[/COLOR]", urljoin(BASE_URL, "most-popular/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Top Rated[/COLOR]", urljoin(BASE_URL, "top-rated/"), "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", urljoin(BASE_URL, "search/"), "Search", site.img_search)
    List(urljoin(BASE_URL, "videos/"))


@site.register()
def List(url: str):
    html_content = utils.getHtml(url, referer=site.url)
    if not html_content:
        utils.eod()
        return

    soup = utils.parse_html(html_content)
    if not soup:
        utils.eod()
        return

    items = soup.find_all("div", attrs={"data-video-id": True})
    if not items:
        items = [div for div in soup.find_all("div", class_="item") if div.find("a", href=lambda h: h and "/videos/" in h)]

    for item in items:
        link = item.find("a", href=True)
        if not link:
            continue
        href = link["href"]
        if not href.startswith("http"):
            href = urljoin(BASE_URL, href)

        img = item.find("img")
        title = ""
        thumb = ""
        if img:
            title = utils.safe_get_attr(img, "alt", ["title"], default="")
            thumb = utils.safe_get_attr(img, "data-jpg", ["src", "data-src"], default="")
        if not title:
            title = utils.safe_get_attr(link, "title", default="").strip()
        if not title:
            continue
        if thumb and not thumb.startswith("http"):
            thumb = urljoin(BASE_URL, thumb)

        duration_tag = item.find(class_="duration")
        duration = utils.safe_get_text(duration_tag, default="")

        site.add_download_link(
            utils.cleantext(title),
            href,
            "Playvid",
            thumb or site.image,
            duration=duration,
        )

    next_el = soup.find("li", class_="next")
    if next_el:
        next_link = next_el.find("a", href=True)
        if next_link:
            next_url = next_link["href"]
            if not next_url.startswith("http"):
                next_url = urljoin(BASE_URL, next_url)
            site.add_dir("Next Page", next_url, "List", site.img_next)

    utils.eod()


@site.register()
def Categories(url: str):
    html_content = utils.getHtml(url, referer=site.url)
    if not html_content:
        utils.eod()
        return

    soup = utils.parse_html(html_content)
    if not soup:
        utils.eod()
        return

    items = soup.find_all("div", class_="item")
    for item in items:
        link = item.find("a", href=True)
        if not link or "/categories/" not in link["href"]:
            continue
        href = link["href"]
        if not href.startswith("http"):
            href = urljoin(BASE_URL, href)

        title = utils.safe_get_attr(link, "title", default="").strip()
        img = item.find("img")
        thumb = utils.safe_get_attr(img, "src", ["data-src"], default="") if img else ""
        if thumb and not thumb.startswith("http"):
            thumb = urljoin(BASE_URL, thumb)

        count_tag = item.find(class_="video_count")
        count_str = utils.safe_get_text(count_tag, default="").strip()
        display_name = f"{utils.cleantext(title)} [COLOR hotpink]({count_str})[/COLOR]" if count_str else utils.cleantext(title)

        if title:
            site.add_dir(display_name, href, "List", thumb or site.img_cat)

    utils.eod()


@site.register()
def Search(url: str, keyword: str | None = None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = urljoin(BASE_URL, f"search/?q={quote_plus(keyword.strip())}")
        List(search_url)


@site.register()
def Playvid(url: str, name: str, download: bool | None = None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    html_content = utils.getHtml(url, referer=site.url)
    if not html_content:
        vp.progress.close()
        utils.notify("Error", "Failed to load video page")
        return

    videolink = None

    soup = utils.parse_html(html_content)
    if soup:
        sources = soup.find_all("source", src=True)
        for s in sources:
            if s.get("title") == "1080p":
                videolink = s["src"]
                break
        if not videolink:
            for s in sources:
                if s.get("title") == "720p":
                    videolink = s["src"]
                    break
        if not videolink and sources:
            videolink = sources[0]["src"]

    if not videolink:
        match = re.search(r'"contentUrl"\s*:\s*"([^"]+)"', html_content)
        if match:
            videolink = match.group(1)

    if not videolink:
        match = re.search(r'(https://mylust\.com/get_file/[^"\'\s>]+)', html_content)
        if match:
            videolink = match.group(1)

    if videolink:
        videolink = videolink.replace("&amp;", "&")
        vp.progress.update(75, "[CR]Playing video[CR]")
        vp.play_from_direct_link(f"{videolink}|verifypeer=false")
    else:
        utils.notify("Video not found", "Could not extract video source")

    vp.progress.close()
