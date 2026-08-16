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
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "pornslash",
    "[COLOR hotpink]PornSlash[/COLOR]",
    "https://www.pornslash.com/",
    "pornslash.png",
    "pornslash",
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
        "[COLOR hotpink](Porn)Stars[/COLOR]",
        site.url + "pornstars?p=1",
        "Stars",
        utils.cum_image("cum-models.png"),
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/",
        "Search",
        site.img_search,
    )
    List(site.url + "videos/new?p=1")


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.notify("PornSlash", "No video found!")
        return

    soup = utils.parse_html(listhtml)
    items = soup.select(".video-item, div.video-item")
    if not items:
        utils.notify("PornSlash", "No video found!")
        return

    found = False
    for item in items:
        a_tag = item.select_one("a[href]")
        if not a_tag:
            continue
        href = utils.safe_get_attr(a_tag, "href")
        if not href:
            continue
        videopage = site.url.rstrip("/") + href if href.startswith("/") else href

        name = item.get("data-title") or utils.safe_get_attr(a_tag, "title") or utils.safe_get_text(a_tag)
        name = utils.cleantext(name)

        resolution = utils.safe_get_text(item.select_one(".quality"))
        duration = utils.safe_get_text(item.select_one(".duration"))
        img_tag = item.select_one("img")
        img = utils.get_thumbnail(img_tag) if img_tag else ""

        title = f"{name} [COLOR yellow]{resolution}[/COLOR]" if resolution else name
        site.add_download_link(title, videopage, "Playvid", img, name, duration=duration)
        found = True

    if not found:
        utils.notify("PornSlash", "No video found!")
        return

    next_page = soup.select_one("a.next, .pagination a.next, a:has(span.nav-btn)")
    if next_page:
        np_href = utils.safe_get_attr(next_page, "href")
        m = re.search(r"[\?\&]p=(\d+)", np_href)
        if m:
            nextpage = m.group(1)
            np_url = site.url.rstrip("/") + np_href if np_href.startswith("/") else np_href
            site.add_dir(f"Next Page... ({nextpage})", np_url, "List", site.img_next)

    utils.eod()


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    items = soup.select(".cat-item, a[class*='cat-item']")
    if not items:
        raise ValueError("No Categories found!")

    for item in items:
        href = utils.safe_get_attr(item, "href")
        name = utils.safe_get_text(item.select_one(".cat-name")) or utils.safe_get_text(item)
        img_tag = item.select_one("img")
        img = utils.get_thumbnail(img_tag) if img_tag else ""
        if not href or not name:
            continue
        cat_url = site.url.rstrip("/") + href + "?p=1" if not href.startswith("http") else href
        site.add_dir(name, cat_url, "List", img)
    utils.eod()


@site.register()
def Stars(url):
    starshtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(starshtml)
    items = soup.select("a.poster-wrapper, .star-item")
    if not items:
        raise ValueError("No Stars found!")

    for item in items:
        href = utils.safe_get_attr(item, "href")
        img_tag = item.select_one("img")
        name = utils.safe_get_attr(img_tag, "alt") or utils.safe_get_text(item)
        img = utils.get_thumbnail(img_tag) if img_tag else ""
        if not href or not name:
            continue
        star_url = site.url.rstrip("/") + href if not href.startswith("http") else href
        site.add_dir(name, star_url, "List", img)

    next_page = soup.select_one("a.next, .pagination a.next, a:has(span.nav-btn)")
    if next_page:
        np_href = utils.safe_get_attr(next_page, "href")
        m = re.search(r"[\?\&]p=(\d+)", np_href)
        if m:
            nextpage = m.group(1)
            np_url = site.url.rstrip("/") + np_href if np_href.startswith("/") else np_href
            site.add_dir(f"Next Page... ({nextpage})", np_url, "Stars", site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        query_url = site.url + f"search/{keyword.replace(' ', '+')}?p=1"
        List(query_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]{}[CR]".format(utils.i18n("loading_video")))

    embed = utils.getHtml(url, site.url)
    if not embed:
        utils.notify(name, "No page found!")
        return

    master_match = re.search(r'fetch\("(https?://[^"]+/master/[^"]+)"\)', embed)
    if not master_match:
        soup = utils.parse_html(embed)
        video_tag = soup.select_one("video source, video")
        if video_tag and video_tag.get("src"):
            vp.play_from_direct_link(video_tag["src"])
            return
        raise ValueError("No video stream found!")

    master_url = master_match.group(1)
    try:
        m3u = utils.getHtml(master_url, url)
    except Exception:
        vp.play_from_direct_link(master_url)
        return

    variants = re.findall(
        r"#EXT-X-STREAM-INF:.*?RESOLUTION=(\d+x\d+).*?\n(https?://[^\s]+)",
        m3u,
    )
    if not variants:
        vp.play_from_direct_link(master_url)
        return

    sources = {res: stream_url for res, stream_url in variants}
    videourl = utils.selector(
        utils.i18n("select_quality"),
        sources,
        setting_valid="qualityask",
        sort_by=lambda x: int(x.split("x")[1]) if "x" in x else 0,
        reverse=True,
    )
    if not videourl:
        return

    vp.progress.update(75, "[CR]{}[CR]".format(utils.i18n("stream_found")))
    play_url = (
        videourl
        + "|User-Agent="
        + urllib_parse.quote(utils.USER_AGENT)
        + "&Referer="
        + urllib_parse.quote(site.url)
    )
    vp.play_from_direct_link(play_url)
