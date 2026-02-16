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
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "hotleak",
    "[COLOR hotpink]Hotleak[/COLOR]",
    "https://hotleak.vip/",
    "hotleak.png",
    "hotleak",
)

# Use a stable, common user agent for Hotleak to prevent 403s
HOTLEAK_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"


@site.register(default_mode=True)
def Main(url):
    site.add_dir("[COLOR hotpink]Videos[/COLOR]", site.url + "videos", "List", "")
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "videos", "Search", site.img_search)
    utils.eod()


@site.register()
def List(url, page=1):
    listhtml = utils.getHtml(url)

    soup = utils.parse_html(listhtml)
    items = soup.select("article.movie-item")
    for item in items:
        link = item.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href")
        if not videopage or "tantaly.com" in videopage: # Skip ads
            continue
        videopage = urllib_parse.urljoin(site.url, videopage)

        img_tag = item.select_one("img.post-thumbnail")
        img = utils.safe_get_attr(img_tag, "src")
        if img:
            img = urllib_parse.urljoin(site.url, img)
            img = img + "|User-Agent=" + utils.USER_AGENT

        name = utils.safe_get_text(item.select_one(".movie-name h3"))
        if not name:
            name = utils.safe_get_attr(img_tag, "alt", default="Video")

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
    next_el = soup.select_one("a.page-link[rel='next']")
    if next_el:
        np_url = utils.safe_get_attr(next_el, "href")
        if np_url:
            np_url = urllib_parse.urljoin(site.url, np_url)
            page_match = re.search(r"page=(\d+)", np_url)
            np = page_match.group(1) if page_match else str(int(page) + 1)
            site.add_dir("Next Page ({})".format(np), np_url, "List", site.img_next, page=np)

    utils.eod()


def _decrypt_video_url(encrypted_url):
    """
    Decrypt hotleak video URL.

    The site uses client-side encryption that:
    1. Removes first 8 characters
    2. Removes last 16 characters
    3. Reverses the string
    4. Base64 decodes the result

    Args:
        encrypted_url: Encrypted URL from data-video attribute

    Returns:
        Decrypted M3U8 URL
    """
    try:
        # Remove first 8 chars
        decrypted = encrypted_url[8:]
        # Remove last 16 chars
        decrypted = decrypted[:-16]
        # Reverse the string
        decrypted = decrypted[::-1]
        # Base64 decode
        decrypted = base64.b64decode(decrypted).decode('utf-8')
        return decrypted
    except Exception as e:
        utils.kodilog("hotleak: URL decryption failed: {}".format(e))
        return None


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    # Skip inputstream.adaptive - the m3u8 server rejects HEAD requests (403)
    # and rejects Referer headers. Let Kodi's FFMpeg handle the HLS directly.
    vp.IA_check = "skip"

    # Get HTML page
    html = utils.getHtml(url)
    soup = utils.parse_html(html)

    # Look for video data in data-video attributes
    video_items = soup.select('[data-video]')

    for item in video_items:
        data_video = utils.safe_get_attr(item, 'data-video')
        if not data_video:
            continue

        try:
            video_json = json.loads(data_video)

            # Extract encrypted URL from JSON
            if 'source' in video_json and len(video_json['source']) > 0:
                encrypted_url = video_json['source'][0].get('src', '')

                if encrypted_url:
                    # Decrypt the URL
                    vp.progress.update(50, "[CR]Decrypting video URL[CR]")
                    video_url = _decrypt_video_url(encrypted_url)

                    if video_url:
                        utils.kodilog("hotleak: Decrypted URL: {}".format(video_url))
                        # M3U8 requires Origin header; Referer must NOT be sent (causes 403)
                        video_url_with_headers = "{0}|User-Agent={1}&Origin={2}".format(
                            video_url, HOTLEAK_UA, site.url.rstrip('/')
                        )
                        vp.play_from_direct_link(video_url_with_headers)
                        return

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            utils.kodilog("hotleak: Failed to parse video data: {}".format(e))
            continue

    # If we get here, we couldn't find/decrypt the video URL
    utils.kodilog("hotleak: Could not extract video URL from page")
    vp.progress.close()
    utils.notify("Error", "Could not find video URL")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = site.url + "search?search=" + urllib_parse.quote(keyword)
        List(search_url)
