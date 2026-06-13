"""
Cumination
Copyright (C) 2023 Team Cumination

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
import base64
import json
import six
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "hotleak",
    "[COLOR hotpink]Hotleak[/COLOR]",
    "https://hotleak.vip/",
    "hotleak.png",
    "hotleak",
    category="Amateur & Social",
)


def _is_text(value):
    return isinstance(value, six.string_types)


def _log_non_text_response(context, value):
    utils.kodilog(
        "hotleak: Expected HTML string while {}, got {}".format(
            context, type(value).__name__
        )
    )


def _headers_suffix():
    return "|User-Agent={0}&Referer={1}".format(
        urllib_parse.quote(utils.USER_AGENT),
        urllib_parse.quote(site.url),
    )


def _with_headers(url):
    if not url or "|" in url:
        return url
    return url + _headers_suffix()


def _absolute_url(url):
    return urllib_parse.urljoin(site.url, url or "")


def _fallback_title_from_url(url):
    parts = [part for part in urllib_parse.urlsplit(url or "").path.split("/") if part]
    if len(parts) >= 3 and parts[-2] == "video":
        return "Hotleak Video {}".format(parts[-1])
    return "Hotleak Video"


def _clean_title(title, url=""):
    title = utils.cleantext(title or "").strip()
    title = re.sub(r"\s+\d{5,}\s*$", "", title).strip()
    return title or _fallback_title_from_url(url)


def _extract_video_data(data_video):
    if not data_video:
        return None
    try:
        return json.loads(data_video)
    except (TypeError, ValueError) as e:
        utils.kodilog("hotleak: Failed to parse video data: {}".format(e))
        return None


def _iter_encrypted_sources(video_json):
    if not isinstance(video_json, dict):
        return
    sources = video_json.get("source") or []
    if isinstance(sources, dict):
        sources = [sources]
    for source in sources:
        if not isinstance(source, dict):
            continue
        encrypted_url = source.get("src") or source.get("file") or source.get("url")
        if encrypted_url:
            yield encrypted_url


@site.register(default_mode=True)
def Main(url):
    site.add_dir("[COLOR hotpink]Videos[/COLOR]", site.url + "videos", "List", "")
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search", "Search", site.img_search
    )
    utils.eod()


@site.register()
def List(url, page=1):
    listhtml = utils.getHtml(url, site.url)
    if not _is_text(listhtml):
        _log_non_text_response("loading listing", listhtml)
        listhtml = ""
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    items = soup.select("article.movie-item, .movie-item")
    seen_urls = set()

    for item in items:
        link = item.select_one("a.thumbnail-container")
        if not link:
            link = item.select_one("a")
        
        videopage = utils.safe_get_attr(link, "href")
        if not videopage or "tantaly.com" in videopage: # Skip ads
            continue
        videopage = _absolute_url(videopage)
        
        # Skip photos
        if "/photo/" in videopage:
            continue
        if "/video/" not in videopage or videopage in seen_urls:
            continue
        seen_urls.add(videopage)

        img_tag = item.select_one("img.post-thumbnail, img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
        if img:
            img = _with_headers(_absolute_url(img.strip()))

        name = utils.safe_get_text(item.select_one(".movie-name h3, .movie-name, .post-title, .title"))
        if not name:
            name = utils.safe_get_attr(img_tag, "alt")
        name = _clean_title(name, videopage)
        
        date = utils.safe_get_text(item.select_one(".date"))
        views = utils.safe_get_text(item.select_one(".view"))
        meta = []
        if date:
            meta.append(date)
        if views:
            meta.append(views)
        description = " | ".join(meta)

        site.add_download_link(
            name, videopage, "Playvid", img, desc=description
        )

    # Next Page
    next_el = soup.select_one("a.page-link[rel='next'], a.next, li.next a")
    if next_el:
        np_url = utils.safe_get_attr(next_el, "href")
        if np_url:
            np_url = _absolute_url(np_url)
            page_match = re.search(r"page=(\d+)", np_url)
            np = page_match.group(1) if page_match else str(int(page) + 1)
            site.add_dir("Next Page ({})".format(np), np_url, "List", site.img_next, page=np)

    utils.eod()


def _decrypt_video_url(encrypted_url):
    if not encrypted_url or not _is_text(encrypted_url) or len(encrypted_url) <= 32:
        return None
    try:
        # Remove first 16 chars
        decrypted = encrypted_url[16:]
        # Remove last 16 chars
        decrypted = decrypted[:-16]
        # Reverse the string
        decrypted = decrypted[::-1]
        # Base64 decode
        decrypted = base64.b64decode(decrypted).decode("utf-8")
        if decrypted.startswith("http"):
            return decrypted
        utils.kodilog("hotleak: Decrypted URL did not look playable")
        return None
    except Exception as e:
        utils.kodilog("hotleak: URL decryption failed: {}".format(e))
        return None


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    vp.IA_check = "skip"

    # Get HTML page
    html = utils.getHtml(url)
    if not _is_text(html):
        _log_non_text_response("loading video page", html)
        html = ""
    if not html:
        vp.progress.close()
        utils.notify("Error", "Could not load video page")
        return
    soup = utils.parse_html(html)

    # Look for video data in data-video attributes
    video_items = soup.select('[data-video]')

    for item in video_items:
        data_video = utils.safe_get_attr(item, 'data-video')
        video_json = _extract_video_data(data_video)
        for encrypted_url in _iter_encrypted_sources(video_json):
            # Decrypt the URL
            vp.progress.update(50, "[CR]Decrypting video URL[CR]")
            video_url = _decrypt_video_url(encrypted_url)

            if video_url:
                utils.kodilog("hotleak: Decrypted URL: {}".format(video_url))
                # Play directly with headers to avoid session/token issues
                vp.play_from_direct_link(_with_headers(video_url))
                return

    # If we get here, we couldn't find/decrypt the video URL
    utils.kodilog("hotleak: Could not extract video URL from page")
    vp.progress.close()
    utils.notify("Error", "Could not find video URL")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = site.url + "search?search=" + urllib_parse.quote_plus(keyword)
        List(search_url)
