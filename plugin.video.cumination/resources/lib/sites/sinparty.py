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
import math
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "sinparty",
    "[COLOR hotpink]SinParty[/COLOR]",
    "https://sinparty.com/",
    "sinparty.png",
    "sinparty",
    webcam=True,
    category="Cams & Live",
)

API_URL = "https://api.sinparty.com/v2/web/live-cams/web-rtc/{0}?gender%5B%5D={1}&per_page=100&page=1"

GENDERS = {
    "[COLOR hotpink]Female[/COLOR]": ("girls", "f"),
    "[COLOR hotpink]Couples[/COLOR]": ("couples", "c"),
    "[COLOR hotpink]Male[/COLOR]": ("men", "m"),
    "[COLOR hotpink]Transsexual[/COLOR]": ("trans", "t"),
}


@site.register(default_mode=True)
def Main():
    for label, (path, gender) in GENDERS.items():
        site.add_dir(label, API_URL.format(path, gender), "List", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url, "Search", site.img_search
    )
    utils.eod()


def _next_page_url(url, data):
    total = data.get("data", {}).get("total") or 0
    if not total:
        return None, None, None

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    current_page = int((query.get("page") or ["1"])[0])
    per_page = int((query.get("per_page") or ["100"])[0])
    total_pages = math.ceil(total / per_page)
    if current_page >= total_pages:
        return None, current_page, total_pages

    query["page"] = [str(current_page + 1)]
    next_url = urlunparse(parsed._replace(query=urlencode(query, doseq=True)))
    return next_url, current_page + 1, total_pages


@site.register()
def List(url):
    try:
        response = utils._getHtml(url)
        data = json.loads(response)
    except Exception as e:
        utils.kodilog("SinParty: error loading list: {}".format(str(e)))
        utils.notify("SinParty", "Could not load models")
        utils.eod()
        return

    items = data.get("data", {}).get("items") or []
    if not items:
        utils.notify("SinParty", "No live models found")

    for item in items:
        name = item.get("title") or item.get("slug") or "Unknown"
        creator_hash = item.get("creator_user_hash")
        if not creator_hash:
            continue

        plot_parts = []
        if item.get("age"):
            plot_parts.append(
                "[COLOR deeppink]Age:[/COLOR] {}".format(item["age"])
            )
        if item.get("country"):
            plot_parts.append(
                "[COLOR deeppink]Country:[/COLOR] {}".format(item["country"])
            )
        if item.get("viewers") is not None:
            plot_parts.append(
                "[COLOR deeppink]Viewers:[/COLOR] {}".format(item["viewers"])
            )
        if item.get("topic"):
            plot_parts.append(
                "[COLOR deeppink]Topic:[/COLOR] {}".format(utils.cleantext(item["topic"]))
            )
        plot = "[CR]".join(plot_parts)

        api_url = "https://api.sinparty.com/v2/web/live-cams/web-rtc/" + creator_hash
        site.add_download_link(
            name,
            api_url,
            "Playvid",
            item.get("thumbnail_url") or "",
            plot,
            noDownload=True,
        )

    next_url, next_page, total_pages = _next_page_url(url, data)
    if next_url:
        site.add_dir(
            "[COLOR hotpink]Next Page...[/COLOR] ({}/{})".format(next_page, total_pages),
            next_url,
            "List",
            site.img_next,
        )

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
        return
    List(API_URL.format("girls", "f") + "&search=" + keyword.replace(" ", "+"))


@site.register()
def Playvid(url, name):
    vp = utils.VideoPlayer(name, IA_check="IA")
    vp.progress.update(25, "[CR]Loading model stream[CR]")

    try:
        response = utils._getHtml(url)
        data = json.loads(response).get("data", {})
    except Exception as e:
        vp.progress.close()
        utils.kodilog("SinParty: error loading stream for {}: {}".format(name, str(e)))
        utils.notify("SinParty", "Could not load stream")
        return

    if data.get("isLive") is False:
        vp.progress.close()
        utils.notify(name, "Model is offline")
        return
    if data.get("type") == "private":
        vp.progress.close()
        utils.notify(name, "Model is in a private show")
        return

    videourl = data.get("playback_url")
    if not videourl:
        vp.progress.close()
        utils.notify(name, "Stream unavailable")
        return

    vp.progress.update(80, "[CR]Starting Playback[CR]")
    vp.play_from_direct_link(videourl)
    vp.progress.close()
