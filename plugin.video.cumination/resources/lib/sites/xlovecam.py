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

import json
import re
import time
from urllib.parse import quote, unquote

import requests

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "xlovecam",
    "[COLOR hotpink]xLoveCam[/COLOR]",
    "https://www.xlovecam.com/en/",
    "xlovecam.png",
    "xlovecam",
    webcam=True,
    category="Cams & Live",
)

ONLINE_LIST_URL = "https://www.xlovecam.com/en/performerAction/onlineList/"
STREAM_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
# Matches both the legacy `var csrfProtectionToken = "..."` form and the
# current page's JSON-embedded `"csrfProtectionToken":"..."` form -- the
# site changed shape since upstream's original regex (which only matched
# the `=` form) stopped finding a token at all.
CSRF_RE = re.compile(r'csrfProtectionToken"?\s*[:=]\s*"([^"]+)"')


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Models[/COLOR]", site.url, "List", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url, "Search", site.img_search
    )
    utils.eod()


def _online_list(next_query=None, nickname=""):
    session = requests.Session()
    init = session.get(site.url, headers={"User-Agent": STREAM_UA}, timeout=15)
    token_match = CSRF_RE.search(init.text)
    token = token_match.group(1) if token_match else ""

    cookies = session.cookies.get_dict()
    cookies.setdefault("x-windowId", "mt9rzsd4.2tp4l")

    headers = {
        "User-Agent": STREAM_UA,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": site.url,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    offset_from = next_query.get("from", 0) if next_query else 0
    data_time = next_query.get("time") if next_query else int(time.time())
    data_off = (next_query.get("off") if next_query else None) or ""

    data = {
        "config[nickname]": nickname,
        "config[favorite]": "0",
        "config[recent]": "0",
        "config[vip]": "0",
        "config[sort][id]": "35",
        "offset[from]": str(offset_from),
        "offset[length]": "35",
        "origin": "fetch-stat-on-load",
        "stat": "1",
        "data[from]": str(offset_from),
        "data[time]": str(data_time),
        "data[off]": data_off,
        "featureSupported[sessionStorageLarge]": "true",
        "featureSupported[localStorage]": "true",
        "csrfProtectionToken": token,
    }

    resp = session.post(
        ONLINE_LIST_URL, headers=headers, cookies=cookies, data=data, timeout=15
    )
    return resp.json()


@site.register()
def List(url):
    next_query = None
    if url.startswith("{") or url.startswith("%7B"):
        next_query = json.loads(unquote(url))

    try:
        response = _online_list(next_query=next_query)
    except Exception as e:
        utils.kodilog("xLoveCam: error loading list: {}".format(str(e)))
        utils.notify("xLoveCam", "Could not load models")
        utils.eod()
        return

    content = response.get("content", {})
    items = content.get("performerList") or []
    if not items:
        utils.notify("xLoveCam", "No live models found")

    for item in items:
        if item.get("showType") != 1:
            continue
        name = item.get("nickname")
        videourl = item.get("hlsPlaylist")
        if not name or not videourl:
            continue
        img = "https:" + item["profileImg"] if item.get("profileImg", "").startswith("//") else item.get("profileImg", "")
        plot_parts = []
        if item.get("rating"):
            plot_parts.append("[COLOR deeppink]Rating:[/COLOR] {}".format(item["rating"]))
        if item.get("love"):
            plot_parts.append("[COLOR deeppink]Loves:[/COLOR] {}".format(item["love"]))
        plot = "[CR]".join(plot_parts)

        site.add_download_link(name, videourl, "Playvid", img, plot, noDownload=True)

    if content.get("moreItemAvailable") and content.get("nextQuery"):
        np = quote(json.dumps(content["nextQuery"]))
        site.add_dir(
            "[COLOR hotpink]Next Page...[/COLOR]", np, "List", site.img_next
        )

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
        return

    try:
        response = _online_list(nickname=keyword)
    except Exception as e:
        utils.kodilog("xLoveCam: error searching: {}".format(str(e)))
        utils.notify("xLoveCam", "Search failed")
        utils.eod()
        return

    items = response.get("content", {}).get("performerList") or []
    if not items:
        utils.notify("xLoveCam", "No models found for '{}'".format(keyword))

    for item in items:
        if item.get("showType") != 1:
            continue
        name = item.get("nickname")
        videourl = item.get("hlsPlaylist")
        if not name or not videourl:
            continue
        img = "https:" + item["profileImg"] if item.get("profileImg", "").startswith("//") else item.get("profileImg", "")
        site.add_download_link(name, videourl, "Playvid", img, noDownload=True)

    utils.eod()


@site.register()
def Playvid(url, name):
    header_string = "User-Agent={0}&Referer={1}".format(
        quote(STREAM_UA, safe=""), quote(site.url, safe=""),
    )
    vp = utils.VideoPlayer(name, IA_check="IA")
    vp.play_from_direct_link("{}|{}".format(url, header_string))
