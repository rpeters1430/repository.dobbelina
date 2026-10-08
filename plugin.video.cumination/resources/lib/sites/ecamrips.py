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

import base64
import os
import re
import time
from urllib.parse import quote, urljoin

from resources.lib import basics, utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "ecamrips",
    "[COLOR hotpink]eCamRips[/COLOR]",
    "https://www.ecamrips.com/",
    "ecamrips.png",
    "ecamrips",
    category="Cams & Live",
    requires_flaresolverr=True,
)

THUMB_DIR = os.path.join(basics.profileDir, "thumbs", "ecamrips")
THUMB_MAX_AGE = 2 * 24 * 60 * 60
IMAGE_TYPES = ((b"RIFF", ".webp"), (b"\x89PNG", ".png"), (b"\xff\xd8", ".jpg"))


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search Models[/COLOR]",
        site.url + "model/en/{0}/",
        "Search",
        site.img_search,
    )
    List(site.url + "en/")
    utils.eod()


def _prune_thumbs():
    try:
        cutoff = time.time() - THUMB_MAX_AGE
        for name in os.listdir(THUMB_DIR):
            path = os.path.join(THUMB_DIR, name)
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
    except OSError:
        pass


def _save_thumb(video_id, data_uri):
    """Thumbnails are inlined as base64 data URIs, which Kodi cannot display,
    so write each one to the profile and hand Kodi the file path instead."""
    if not video_id or not data_uri.startswith("data:image"):
        return ""
    try:
        raw = base64.b64decode(data_uri.split(",", 1)[1].strip())
    except (IndexError, ValueError):
        return ""
    # The declared mime type is wrong (WebP served as image/png): sniff it.
    ext = next((e for magic, e in IMAGE_TYPES if raw.startswith(magic)), None)
    if not ext:
        return ""
    path = os.path.join(THUMB_DIR, video_id + ext)
    try:
        if not os.path.exists(path):
            if not os.path.isdir(THUMB_DIR):
                os.makedirs(THUMB_DIR)
            with open(path, "wb") as fh:
                fh.write(raw)
    except OSError:
        return ""
    return path


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    _prune_thumbs()
    for item in soup.select("li[id^='li']"):
        link = item.select_one("a.moiclick1[href]")
        if not link:
            continue
        img = link.select_one("img")
        name = utils.safe_get_attr(link, "title") or utils.safe_get_attr(img, "alt")
        name = utils.cleantext(name)
        if not name:
            continue
        thumb = _save_thumb(
            utils.safe_get_attr(link, "data-id"),
            utils.safe_get_attr(img, "data-tn", ["src"]),
        )
        site.add_download_link(
            name,
            urljoin(site.url, link["href"]),
            "Playvid",
            thumb,
            duration=utils.safe_get_text(item.select_one(".dur")),
        )

    next_link = soup.select_one("a.current + a[href]")
    if next_link:
        site.add_dir(
            "Next Page", urljoin(url, next_link["href"]), "List", site.img_next
        )
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    # The page embeds loading_video.php?idd=<id>, a click-through to play.php
    # which holds the <video>. play.php only needs the id from the page URL,
    # but answers with an empty body unless a same-site Referer is sent (and
    # so does the media host).
    video_id = re.search(r"/show-cam-sex-movies/(\d+)-", url)
    if video_id:
        play_url = "{}play.php?idd={}".format(site.url, video_id.group(1))
    else:
        soup = utils.parse_html(utils.getHtml(url, site.url))
        iframe = soup.find("iframe", src=re.compile(r"loading_video\.php", re.I))
        play_url = (
            urljoin(url, iframe["src"]).replace("loading_video.php", "play.php")
            if iframe
            else None
        )

    video_url = None
    if play_url:
        vp.progress.update(50, "[CR]Resolving embed[CR]")
        source = utils.parse_html(utils.getHtml(play_url, url)).select_one(
            "video[src], video source[src]"
        )
        if source:
            video_url = urljoin(play_url, source["src"])

    if video_url:
        vp.progress.update(80, "[CR]Playing video[CR]")
        vp.play_from_direct_link("{}|Referer={}".format(video_url, site.url))
    else:
        vp.progress.close()
        utils.notify("No playable stream found", "eCamRips")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        # The site's search box only looks up model names.
        List(url.format(quote(keyword.strip().replace(" ", "_"))))
