"""
Cumination
Copyright (C) 2017 Whitecream, hdgdl, Team Cumination

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

import json
import os
import re
import sqlite3
import time
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
import xbmcgui
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "stripchat",
    "[COLOR hotpink]stripchat.com[/COLOR]",
    "https://stripchat.com/",
    "stripchat.png",
    "stripchat",
    webcam=True,
    category="Cams & Live",
)

STRIPCHAT_STREAM_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
)
STRIPCHAT_PKEY = "B0p93vi8Uj6AYyZb"
STRIPCHAT_DISABLED = False


def _normalize_model_image_url(url: str | None) -> str:
    if not isinstance(url, str) or not url:
        return ""
    normalized = url.strip()
    if normalized.startswith("//"):
        return "https:" + normalized
    if normalized.startswith("/"):
        return "https://stripchat.com" + normalized
    if normalized.startswith("http"):
        return normalized
    return ""


def _live_preview_url(url: str | None, snapshot_ts: int | str | None = None, cache_bust: int | str | None = None) -> str:
    normalized = _normalize_model_image_url(url)
    if not normalized:
        return ""
    if "strpst.com/previews/" in normalized and "-thumb-small" in normalized:
        normalized = normalized.replace("-thumb-small", "-thumb-big")
    if "strpst.com/previews/" in normalized and snapshot_ts:
        sep = "&" if "?" in normalized else "?"
        normalized = f"{normalized}{sep}t={snapshot_ts}"
    if "strpst.com/previews/" in normalized and cache_bust:
        sep = "&" if "?" in normalized else "?"
        normalized = f"{normalized}{sep}cb={cache_bust}"
    return normalized


def _model_screenshot(model: dict, cache_bust: int | str | None = None) -> str:
    if not isinstance(model, dict):
        return ""
    model_id = model.get("id")
    snapshot_ts = model.get("snapshotTimestamp") or model.get("popularSnapshotTimestamp")
    if snapshot_ts and model_id:
        return f"https://img.doppiocdn.com/thumbs/{snapshot_ts}/{model_id}_webp"

    image_fields = (
        "previewUrlThumbSmall",
        "previewUrlThumbBig",
        "previewUrlThumbLarge",
        "preview",
        "previewUrl",
        "snapshotUrl",
        "avatarUrl",
        "thumbnailUrl",
        "thumbUrl",
        "imageUrl",
        "posterUrl",
    )
    for field in image_fields:
        value = model.get(field)
        if isinstance(value, dict):
            for nested_key in ("url", "src", "https", "absolute"):
                img = _live_preview_url(value.get(nested_key), snapshot_ts, cache_bust=cache_bust)
                if img:
                    return img
            continue
        img = _live_preview_url(value, snapshot_ts, cache_bust=cache_bust)
        if img:
            return img

    return ""


def _format_direct_hls_url(stream_url: str) -> str:
    """Format Stripchat HLS stream URL for native Kodi inputstream.adaptive playback.

    Stripchat's CDN natively supports standard HLS playback when using the native
    fallback key pkey=B0p93vi8Uj6AYyZb and excluding playlistType=lowLatency.
    This produces ordinary MPEG-TS/MP4 segments rather than Mouflon LL-HLS parts.
    """
    parsed = urlparse(stream_url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query.pop("playlistType", None)
    query["pkey"] = [STRIPCHAT_PKEY]

    clean_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        urlencode(query, doseq=True),
        "",
    ))

    header_string = (
        "User-Agent={0}&Referer={1}&Origin={2}&manifest_headers=1"
    ).format(
        urllib_parse.quote(STRIPCHAT_STREAM_UA, safe=""),
        urllib_parse.quote("https://stripchat.com/", safe=""),
        urllib_parse.quote("https://stripchat.com", safe=""),
    )
    return f"{clean_url}|{header_string}"


def _load_model_stream(model_identifier: str) -> str | None:
    """Find the live HLS stream URL for a given model username or URL."""
    if not isinstance(model_identifier, str) or not model_identifier.strip():
        return None

    cleaned = model_identifier.strip()
    if cleaned.startswith("http") and ".m3u8" in cleaned:
        return cleaned

    parsed = urlparse(cleaned)
    username = parsed.path.strip("/").split("/")[-1] if parsed.scheme and parsed.netloc else cleaned

    endpoint = f"https://stripchat.com/api/front/models?search={urllib_parse.quote(username)}&primaryTag=girls"
    headers = {
        "User-Agent": STRIPCHAT_STREAM_UA,
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://stripchat.com",
        "Referer": f"https://stripchat.com/{username}",
    }
    try:
        utils.kodilog(f"Stripchat: Resolving stream for model: {username}")
        response, _ = utils.get_html_with_cloudflare_retry(
            endpoint,
            site.url,
            headers=headers,
            retry_on_empty=True,
        )
        if response:
            payload = json.loads(response)
            models = payload.get("models") if isinstance(payload, dict) else []
            for model in models:
                if model.get("username", "").lower() == username.lower():
                    stream_url = model.get("hlsPlaylist") or (model.get("stream") or {}).get("url")
                    if stream_url:
                        return stream_url
    except Exception as e:
        utils.kodilog(f"Stripchat: Stream search lookup error: {e}")

    profile_endpoint = f"https://stripchat.com/api/front/models/username/{urllib_parse.quote(username)}"
    try:
        response, _ = utils.get_html_with_cloudflare_retry(
            profile_endpoint,
            site.url,
            headers=headers,
            retry_on_empty=True,
        )
        if response:
            payload = json.loads(response)
            if isinstance(payload, dict):
                model = payload.get("model", payload)
                stream_url = model.get("hlsPlaylist") or (model.get("stream") or {}).get("url")
                if stream_url:
                    return stream_url
    except Exception as e:
        utils.kodilog(f"Stripchat: Username profile endpoint error: {e}")

    return None


def _add_model_download_link(model: dict, cache_bust: int | str | None = None, skip_offline: bool = False) -> bool:
    raw_name = model.get("username")
    if not raw_name:
        return False
    is_live = model.get("isLive")
    if skip_offline and is_live is False:
        return False

    name = utils.cleanhtml(raw_name)
    if is_live is False:
        name += " [COLOR yellow][Offline][/COLOR]"
    videourl = model.get("hlsPlaylist") or (model.get("stream") or {}).get("url") or raw_name
    img = _model_screenshot(model, cache_bust=cache_bust)
    fanart = img
    subject = ""
    if model.get("groupShowTopic"):
        subject += model.get("groupShowTopic") + "[CR]"
    if model.get("country"):
        subject += f"[COLOR deeppink]Location: [/COLOR]{utils.get_country(model.get('country'))}[CR]"
    if model.get("languages"):
        langs = [utils.get_language(x) for x in model.get("languages")]
        subject += f"[COLOR deeppink]Languages: [/COLOR]{', '.join(langs)}[CR]"
    if model.get("broadcastGender"):
        subject += f"[COLOR deeppink]Gender: [/COLOR]{model.get('broadcastGender')}[CR]"
    if model.get("viewersCount"):
        subject += f"[COLOR deeppink]Watching: [/COLOR]{model.get('viewersCount')}[CR][CR]"
    if model.get("tags"):
        tags = [t for t in model.get("tags") if "tag" not in t.lower()]
        subject += "[COLOR deeppink]# [/COLOR]" + "[COLOR deeppink] #[/COLOR]".join(tags)

    site.add_download_link(
        name, videourl, "Playvid", img, subject, noDownload=True, fanart=fanart
    )
    return True


@site.register(default_mode=True)
def Main():
    if STRIPCHAT_DISABLED:
        utils.notify("Stripchat", "Temporarily disabled")
        utils.eod()
        return

    female = utils.addon.getSetting("chatfemale") != "false"
    male = utils.addon.getSetting("chatmale") == "true"
    couple = utils.addon.getSetting("chatcouple") == "true"
    trans = utils.addon.getSetting("chattrans") == "true"

    site.add_dir("[COLOR red]Refresh Stripchat images[/COLOR]", "", "clean_database", "", Folder=False)
    site.add_dir("[COLOR red]Top Models[/COLOR]", "", "TopModels", "", Folder=False)
    site.add_dir("[COLOR red]Search[/COLOR]", "", "Search", site.img_search)

    base_api = "https://stripchat.com/api/front/models?limit=80&parentTag=autoTagNew&sortBy=trending&offset=0&primaryTag="
    if female:
        site.add_dir("[COLOR hotpink]Female HD[/COLOR]", f"{base_api}girls&broadcastHD=true", "List", "")
        site.add_dir("[COLOR hotpink]Female[/COLOR]", f"{base_api}girls", "List", "")
    if couple:
        site.add_dir("[COLOR hotpink]Couples HD[/COLOR]", f"{base_api}couples&broadcastHD=true", "List", "")
        site.add_dir("[COLOR hotpink]Couples[/COLOR]", f"{base_api}couples", "List", "")
    if male:
        site.add_dir("[COLOR hotpink]Male HD[/COLOR]", f"{base_api}men&broadcastHD=true", "List", "")
        site.add_dir("[COLOR hotpink]Male[/COLOR]", f"{base_api}men", "List", "")
    if trans:
        site.add_dir("[COLOR hotpink]Transsexual HD[/COLOR]", f"{base_api}trans&broadcastHD=true", "List", "")
        site.add_dir("[COLOR hotpink]Transsexual[/COLOR]", f"{base_api}trans", "List", "")

    utils.eod()


_TOP_MODELS_GENDERS = [
    ("Girls", "female"),
    ("Couples", "couple"),
    ("Guys", "male"),
    ("Trans", "tranny"),
]
_TOP_MODELS_ZONES = [
    ("Worldwide", ""),
    ("Europe", "eu"),
    ("North America", "na"),
    ("South America", "sa"),
    ("Asia & Pacific", "as"),
    ("Africa", "af"),
]


@site.register()
def TopModels():
    if STRIPCHAT_DISABLED:
        utils.notify("Stripchat", "Temporarily disabled")
        return

    gender_names = [name for name, _ in _TOP_MODELS_GENDERS]
    selection = xbmcgui.Dialog().select("Select Gender", gender_names)
    if selection == -1:
        return
    gender = _TOP_MODELS_GENDERS[selection][1]

    zone = ""
    if gender == "female":
        zone_names = [name for name, _ in _TOP_MODELS_ZONES]
        selection = xbmcgui.Dialog().select("Select Region", zone_names)
        if selection == -1:
            return
        zone = _TOP_MODELS_ZONES[selection][1]

    url = (
        "https://stripchat.com/api/front/v5/models/top"
        f"?gender={gender}&period=current&offset=0&limit=100&continent={zone}"
    )

    online_only = utils.addon.getSetting("online_only") == "true"
    if online_only:
        site.add_download_link("[COLOR red][B]Show all models[/B][/COLOR]", url, "online", "", "", noDownload=True)
    else:
        site.add_download_link("[COLOR red][B]Show only models online[/B][/COLOR]", url, "online", "", "", noDownload=True)

    List(url)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        prompt = "Enter model username or search keyword"
        site.search_dir(url, prompt)
        return

    search_url = (
        f"https://stripchat.com/api/front/models?search={urllib_parse.quote(keyword)}&limit=80&offset=0"
    )
    List(search_url)


@site.register()
def List(url: str, page: int = 1):
    if STRIPCHAT_DISABLED:
        utils.notify("Stripchat", "Temporarily disabled")
        utils.eod()
        return

    if utils.addon.getSetting("chaturbate") == "true":
        clean_database(False)

    try:
        utils.kodilog("Stripchat: Fetching model list from API")
        response, _ = utils.get_html_with_cloudflare_retry(
            url,
            referer=site.url,
            headers={"User-Agent": STRIPCHAT_STREAM_UA},
            retry_on_empty=True,
        )
        if not response:
            utils.kodilog("Stripchat: Empty response from API")
            utils.notify("Error", "Could not load Stripchat models")
            utils.eod()
            return

        data = json.loads(response)
        if "models" in data:
            model_list = data["models"]
        elif "tops" in data:
            model_list = [
                winner["model"]
                for top in data.get("tops", [])
                for winner in top.get("winners", [])
                if winner.get("model")
            ]
        else:
            model_list = []
        utils.kodilog(f"Stripchat: Successfully loaded {len(model_list)} models")
    except Exception as e:
        utils.kodilog(f"Stripchat: Error loading model list: {e}")
        utils.notify("Error", "Could not load Stripchat models")
        utils.eod()
        return

    online_only = utils.addon.getSetting("online_only") == "true"
    cache_bust = int(time.time())
    for model in model_list:
        _add_model_download_link(model, cache_bust, skip_offline=online_only)

    total_items = data.get("filteredCount", 0)
    nextp = (page * 80) < total_items
    if nextp:
        next_offset = (page * 80)
        lastpg = -1 * (-total_items // 80)
        page += 1
        nurl = re.sub(r"offset=\d+", f"offset={next_offset}", url)
        if "offset=" not in nurl:
            sep = "&" if "?" in nurl else "?"
            nurl = f"{nurl}{sep}offset={next_offset}"
        site.add_dir(
            f"Next Page.. (Currently in Page {page - 1} of {lastpg})",
            nurl,
            "List",
            site.img_next,
            page,
        )

    utils.eod()


@site.register(clean_mode=True)
def clean_database(showdialog: bool = True):
    try:
        conn = sqlite3.connect(utils.TRANSLATEPATH("special://database/Textures13.db"))
        with conn:
            for domain_fragment in (
                ".strpst.com",
                ".doppiocdn.com",
                ".doppiocdn.net",
                ".doppiocdn.media",
                ".doppiocdn.org",
                ".doppiocdn.live",
            ):
                pattern = f"%{domain_fragment}%"
                rows = conn.execute(
                    "SELECT id, cachedurl FROM texture WHERE url LIKE ?;",
                    (pattern,),
                ).fetchall()
                for row in rows:
                    conn.execute("DELETE FROM sizes WHERE idtexture = ?;", (row[0],))
                    try:
                        os.remove(utils.TRANSLATEPATH("special://thumbnails/" + row[1]))
                    except Exception as e:
                        utils.kodilog(f"Stripchat image cleanup error: {e}")
                conn.execute("DELETE FROM texture WHERE url LIKE ?;", (pattern,))
        if showdialog:
            utils.notify("Finished", "Stripchat images cleared")
    except Exception as e:
        utils.kodilog(f"Stripchat: Texture database clean error: {e}")


@site.register()
def online(url: str):
    if STRIPCHAT_DISABLED:
        utils.notify("Stripchat", "Temporarily disabled")
        return
    if utils.addon.getSetting("online_only") == "true":
        utils.addon.setSetting("online_only", "false")
    else:
        utils.addon.setSetting("online_only", "true")
    utils.refresh()


@site.register()
def Playvid(url: str, name: str):
    if STRIPCHAT_DISABLED:
        utils.notify("Stripchat", "Temporarily disabled")
        return
    if "[Offline]" in name:
        clean_name = name.split(" [COLOR")[0]
        utils.notify(f"{clean_name} is currently offline")
        return
    _play_stripchat_model(url, name)


def _play_stripchat_model(url: str, name: str):
    """Core Stripchat playback handler, usable directly and via LemonCams."""
    raw_stream_url = url
    if not raw_stream_url or not raw_stream_url.startswith("http") or ".m3u8" not in raw_stream_url:
        resolved = _load_model_stream(raw_stream_url or name)
        if resolved:
            raw_stream_url = resolved

    if not raw_stream_url or not raw_stream_url.startswith("http") or ".m3u8" not in raw_stream_url:
        utils.notify("Stripchat", "Model is offline")
        return

    vp = utils.VideoPlayer(name, IA_check="IA")
    vp.progress.update(80, "[CR]Starting Playback[CR]")
    direct_hls_url = _format_direct_hls_url(raw_stream_url)
    vp.play_from_direct_link(direct_hls_url)
    vp.progress.close()
