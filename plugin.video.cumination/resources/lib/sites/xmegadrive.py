"""
Cumination site scraper - xMegaDrive
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
from resources.lib.decrypters.kvsplayer import kvs_decode


site = AdultSite(
    "xmegadrive",
    "[COLOR hotpink]xMegaDrive[/COLOR]",
    "https://www.xmegadrive.com/",
    "xmegadrive.png",
    "xmegadrive",
)
REFERER_HEADER = site.url
ORIGIN_HEADER = site.url.rstrip("/")
UA_HEADER = urllib_parse.quote(utils.USER_AGENT, safe="")
IMG_HEADER_SUFFIX = "|Referer={0}&User-Agent={1}".format(REFERER_HEADER, UA_HEADER)
VIDEO_HEADER_SUFFIX = "|Referer={0}&Origin={1}&User-Agent={2}".format(
    REFERER_HEADER, ORIGIN_HEADER, UA_HEADER
)


def _clean_media_url(media_url):
    if not media_url:
        return None
    cleaned = media_url.replace("\\/", "/").replace("&amp;", "&").strip()
    if "/&" in cleaned:
        cleaned = cleaned.replace("/&", "?", 1)
    cleaned = cleaned.rstrip("/")
    if not cleaned.startswith("http"):
        cleaned = urllib_parse.urljoin(site.url, cleaned)
    return cleaned


def _parse_flashvars(html):
    block = re.search(
        r"var\s+flashvars\s*=\s*\{([^}]+)\}", html, re.IGNORECASE | re.DOTALL
    )
    if not block:
        block = re.search(
            r"flashvars\s*=\s*\{([^}]+)\}", html, re.IGNORECASE | re.DOTALL
        )
    if not block:
        return {}

    vars_block = block.group(1)
    pairs = re.findall(r"([a-z0-9_]+):\s*'([^']*)'", vars_block, re.IGNORECASE)
    if not pairs:
        pairs = re.findall(r'([a-z0-9_]+):\s*"([^"]*)"', vars_block, re.IGNORECASE)
    return {key.lower(): value for key, value in pairs}


def _extract_video_url(html):
    flashvars = _parse_flashvars(html)
    video_url = flashvars.get("video_url") if flashvars else None
    license_code = flashvars.get("license_code") if flashvars else None

    if not video_url:
        flashvars_match = re.search(
            r"['\"]video_url['\"]:\s*['\"]([^'\"]+)['\"]", html, re.IGNORECASE
        )
        if flashvars_match:
            video_url = flashvars_match.group(1)

    if video_url:
        if video_url.startswith("function/") and license_code:
            try:
                video_url = kvs_decode(video_url, license_code)
            except Exception:
                video_url = re.sub(r"^function/\d+/", "", video_url)
        else:
            video_url = re.sub(r"^function/\d+/", "", video_url)

    if not video_url:
        mp4_match = re.search(r'(https?://[^"\'<>\s]+\.mp4/?)', html, re.IGNORECASE)
        if mp4_match:
            video_url = mp4_match.group(1)

    return _clean_media_url(video_url)


def _extract_list_items(html):
    items = []
    soup = utils.parse_html(html)

    for link in soup.select('div.list-videos div.item a[href*="/videos/"]'):
        videourl = utils.safe_get_attr(link, "href")
        if not videourl:
            continue

        title_tag = link.select_one("strong.title")
        title = utils.safe_get_text(title_tag, "") or utils.safe_get_attr(link, "title")
        if not title:
            continue

        img_tag = link.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-original", ["src"])

        duration_tag = link.select_one("div.duration")
        duration = utils.safe_get_text(duration_tag, "")

        items.append((videourl, utils.cleantext(title), img, duration))

    return items


def _find_next_page(html, current_url):
    soup = utils.parse_html(html)

    next_link = soup.select_one('a[rel="next"]')
    if next_link:
        url = utils.safe_get_attr(next_link, "href")
        if url:
            return url

    next_link = soup.select_one('link[rel="next"]')
    if next_link:
        url = utils.safe_get_attr(next_link, "href")
        if url:
            return url

    li_next = soup.select_one('li.next a, li[class*="next"] a')
    if li_next:
        url = utils.safe_get_attr(li_next, "href")
        if url:
            return url

    load_more = soup.select_one("div.load-more a[href]")
    if load_more:
        url = utils.safe_get_attr(load_more, "href")
        if url:
            return url

    page_match = re.search(r"/(\d+)/?$", current_url)
    if page_match:
        current_page = int(page_match.group(1))
        next_page = current_page + 1
        next_url = re.sub(r"/\d+/?$", "/{}/".format(next_page), current_url)
        if "/{}/".format(next_page) in html or "page={}".format(next_page) in html:
            return next_url

    return None


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url + "latest-updates/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    items = _extract_list_items(listhtml)

    for videourl, title, img, duration in items:
        if videourl.startswith("/"):
            videourl = urllib_parse.urljoin(site.url, videourl)
        if img:
            img = urllib_parse.urljoin(site.url, img) if img.startswith("/") else img
            if "|" not in img:
                img += IMG_HEADER_SUFFIX

        display_name = title
        if duration:
            display_name = "{} [COLOR yellow]{}[/COLOR]".format(display_name, duration)
        site.add_download_link(
            display_name, videourl, "Playvid", img, title, duration=duration
        )

    nurl = _find_next_page(listhtml, url)
    if nurl:
        if nurl.startswith("/"):
            nurl = urllib_parse.urljoin(site.url, nurl)
        site.add_dir("[COLOR hotpink]Next Page...[/COLOR]", nurl, "List", site.img_next)

    utils.eod()


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)

    for item in soup.select("div.list-categories a.item"):
        caturl = utils.safe_get_attr(item, "href")
        if not caturl:
            continue

        name = utils.safe_get_attr(item, "title")
        if not name:
            title_tag = item.select_one("strong.title")
            name = utils.safe_get_text(title_tag, "")
        if not name:
            continue

        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-original", ["src"])

        count_tag = item.select_one("div.videos")
        count = utils.safe_get_text(count_tag, "").strip()

        display_name = utils.cleantext(name)
        if count:
            display_name = "{} [COLOR deeppink]{}[/COLOR]".format(display_name, count)

        if img:
            img = urllib_parse.urljoin(site.url, img) if img.startswith("/") else img
            if "|" not in img:
                img += IMG_HEADER_SUFFIX

        site.add_dir(display_name, caturl, "List", img)

    nurl = _find_next_page(cathtml, url)
    if nurl:
        if nurl.startswith("/"):
            nurl = urllib_parse.urljoin(site.url, nurl)
        site.add_dir(
            "[COLOR hotpink]Next Page...[/COLOR]", nurl, "Categories", site.img_next
        )

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        slug = urllib_parse.quote(keyword.replace(" ", "-"))
        search_url = urllib_parse.urljoin(site.url, "search/{}/".format(slug))
        List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    try:
        html = utils.getHtml(url, site.url)
    except Exception:
        utils.notify("Error", "Could not load video page")
        return

    video_url = _extract_video_url(html)
    if video_url:
        play_url = video_url if "|" in video_url else video_url + VIDEO_HEADER_SUFFIX
        vp.progress.update(75, "[CR]Playing video[CR]")
        vp.play_from_direct_link(play_url)
        return

    utils.notify("Error", "Could not extract video URL")
    vp.progress.close()
