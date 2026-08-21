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
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "3movs",
    "[COLOR hotpink]3Movs[/COLOR]",
    "https://www.3movs.com/",
    "3movs.png",
    "3movs",
    category="Video Tubes",
)

movs_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.3movs.com/",
}


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search_videos/?q=",
        "Search",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Most Viewed[/COLOR]",
        site.url + "most-viewed/all-time/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Top Rated[/COLOR]",
        site.url + "top-rated/all-time/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Longest[/COLOR]",
        site.url + "longest/",
        "List",
        site.img_cat,
    )
    List(site.url + "videos/")
    utils.eod()


@site.register()
def List(url, page=1):
    if page is None:
        page = 1
    else:
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1

    current_url = url
    if page > 1:
        if "/search_videos/" in url and "?" in url:
            base, query_str = url.split("?", 1)
            current_url = "{}/{}/?{}".format(base.rstrip("/"), page, query_str)
        else:
            current_url = "{}/{}/".format(url.rstrip("/"), page)

    html = utils.getHtml(current_url, site.url, headers=movs_headers)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)

    for item in soup.select(".item.thumb, .th, .thumb"):
        link = item.select_one("a.title[href], a.wrap_image[href], a[href*='/videos/']")
        if not link:
            continue
        v_url = utils.safe_get_attr(link, "href")
        if not v_url or v_url in ("https://www.3movs.com/videos/", "/videos/", site.url):
            continue
        v_url = urllib_parse.urljoin(site.url, v_url)

        title_tag = item.select_one("a.title, .title")
        v_title = utils.safe_get_text(title_tag) or utils.safe_get_attr(link, "title") or "Video"
        v_title = utils.cleantext(v_title)

        img_tag = item.select_one("img.img, img[data-src], img[src]")
        v_thumb = utils.safe_get_attr(img_tag, "data-src", ["data-webp", "src"]) or site.img_cat

        time_tag = item.select_one(".time, [class*='time']")
        duration = utils.safe_get_text(time_tag) or ""

        site.add_download_link(v_title, v_url, "Playvid", v_thumb, v_title, duration=duration)

    next_page_link = soup.select_one(".pagination a.next, a.icon-arrow-right, a[rel='next']")
    if next_page_link or ("Next" in html or "icon-arrow-right" in html):
        site.add_dir(
            "[COLOR hotpink]Next Page >>[/COLOR]",
            url,
            "List",
            site.img_next,
            page=page + 1,
        )

    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url, headers=movs_headers)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    for item in soup.select(".thumb_cat, .item.thumb_cat, .item"):
        link = item.select_one("a[href*='/categories/']")
        if not link:
            continue
        c_url = utils.safe_get_attr(link, "href")
        if not c_url or c_url in ("https://www.3movs.com/categories/", "/categories/", site.url):
            continue
        c_url = urllib_parse.urljoin(site.url, c_url)

        title_tag = item.select_one(".title, a.title")
        c_title = utils.safe_get_text(title_tag) or utils.safe_get_attr(link, "title") or "Category"
        c_title = utils.cleantext(c_title)

        count_tag = item.select_one("span, .count")
        count = utils.safe_get_text(count_tag)
        display_title = "[COLOR hotpink]{}[/COLOR]".format(c_title)
        if count:
            display_title += " [COLOR yellow]({})[/COLOR]".format(count)

        img_tag = item.select_one("img[data-src], img[src]")
        c_thumb = utils.safe_get_attr(img_tag, "data-src", ["src"]) or site.img_cat

        site.add_dir(display_title, c_url, "List", c_thumb)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = site.url + "search_videos/?q=" + urllib_parse.quote_plus(keyword)
        List(search_url, 1)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    page_html = utils.getHtml(url, site.url, headers=movs_headers)
    if not page_html:
        vp.progress.close()
        utils.notify("Error", "Failed to load video page")
        return

    player_config = re.search(r"var\s+flashvars\s*=\s*({.*?});", page_html, re.DOTALL)
    stream_url = None

    if player_config:
        config_json = player_config.group(1)
        hq_match = re.search(r"video_url:\s*['\"](.*?)['\"]", config_json)
        lq_match = re.search(r"video_alt_url:\s*['\"](.*?)['\"]", config_json)

        hq_url = hq_match.group(1) if hq_match else None
        lq_url = lq_match.group(1) if lq_match else None
        stream_url = hq_url or lq_url

    if stream_url:
        stream_url += "|User-Agent={0}&Referer={1}".format(
            urllib_parse.quote(movs_headers["User-Agent"], safe=""),
            site.url,
        )
        vp.play_from_direct_link(stream_url)
        vp.progress.close()
    else:
        vp.progress.close()
        utils.notify("Error", "Could not extract video URL")
