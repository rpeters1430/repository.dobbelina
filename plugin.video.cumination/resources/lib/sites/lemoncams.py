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

import json
import time
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "lemoncams",
    "[COLOR hotpink]LemonCams[/COLOR]",
    "https://www.lemoncams.com/",
    "lemoncams.png",
    "lemoncams",
    True,
    category="Cams & Live",
)

API_URL = "https://api-v2-prod.lemoncams.com/main"
DEFAULT_PROVIDER = "stripchat"
DEFAULT_PAGE = 1
TOP_CAMS_KEY = "__top__"

SUPPORTED_PROVIDERS = {
    "stripchat": "Stripchat",
    "camsoda": "CamSoda",
    "myfreecams": "MyFreeCams",
}


def _is_supported_provider(provider):
    if not provider:
        return False
    return provider.strip().lower() in SUPPORTED_PROVIDERS


def _api_get(params):
    params_with_tsp = dict(params)
    if "tsp" not in params_with_tsp:
        params_with_tsp["tsp"] = str(int(time.time() * 1000))
    if "project" not in params_with_tsp:
        params_with_tsp["project"] = "lemoncams"
    if "function" not in params_with_tsp:
        params_with_tsp["function"] = "cams"

    query = urllib_parse.urlencode(params_with_tsp)
    url = "{}?{}".format(API_URL, query)
    payload = utils._getHtml(url, referer=site.url)
    if not payload:
        return {}
    try:
        return json.loads(payload)
    except Exception as e:
        utils.kodilog("LemonCams API error: {} - Payload: {}".format(str(e), payload[:200]))
        return {}


def _build_model_page_url(provider, username, stream_url=None):
    base = urllib_parse.urljoin(site.url, "{}/{}".format(provider, username))
    if stream_url:
        return "{}|{}".format(base, stream_url)
    return base


def _parse_model_identifier(value, default_provider=DEFAULT_PROVIDER):
    stream_url = None
    if "|" in value:
        value, stream_url = value.split("|", 1)

    value = (value or "").strip()
    if not value:
        return None, None, None

    parsed = urllib_parse.urlparse(value)
    if parsed.scheme and parsed.netloc:
        path_parts = [part for part in parsed.path.split("/") if part]
        if len(path_parts) >= 2:
            return path_parts[0].lower(), path_parts[1], stream_url
        if len(path_parts) == 1:
            return default_provider, path_parts[0], stream_url
        return None, None, stream_url

    if ":" in value:
        provider, username = value.split(":", 1)
        return provider.strip().lower(), username.strip(), stream_url

    return default_provider, value, stream_url


def _extract_playable_url(cam):
    embed_url = cam.get("embedUrl") or ""
    if any(token in embed_url.lower() for token in [".m3u8", ".mp4", "manifest"]):
        return embed_url

    for preview_url in cam.get("previewUrls", []):
        if any(token in preview_url.lower() for token in [".m3u8", ".mp4", "manifest"]):
            return preview_url

    return ""


def _format_plot(cam):
    meta = [
        "[COLOR deeppink]Provider:[/COLOR] {}".format(cam.get("provider", "").title()),
        "[COLOR deeppink]Viewers:[/COLOR] {:,}".format(cam.get("numberOfUsers", 0)),
    ]
    gender = cam.get("gender")
    if gender:
        meta.append("[COLOR deeppink]Gender:[/COLOR] {}".format(gender.title()))
    if cam.get("country"):
        meta.append("[COLOR deeppink]Country:[/COLOR] {}".format(cam["country"].upper()))
    title = cam.get("title")
    if title:
        meta.append("[COLOR deeppink]Status:[/COLOR] {}".format(utils.cleantext(title)))
    return "[CR]".join(meta)


def _image_url(cam):
    image = cam.get("imageUrl") or cam.get("imageUrlSfw") or ""
    if not image:
        return site.img_cat
    return "{}|User-Agent={}&Referer={}".format(
        image,
        urllib_parse.quote(utils.USER_AGENT, safe=""),
        urllib_parse.quote(site.url, safe=""),
    )


def _fetch_provider_payload(target, page=1):
    params = {
        "page": str(page),
        "function": "cams",
        "project": "lemoncams",
    }
    if target and target != TOP_CAMS_KEY:
        if target.startswith("gender="):
            params["gender"] = target.split("=", 1)[1]
        elif target.startswith("category="):
            params["category"] = target.split("=", 1)[1]
        else:
            params["provider"] = target
    return _api_get(params)


def _find_model_stream(provider, username, max_pages=5):
    for page in range(1, max_pages + 1):
        payload = _fetch_provider_payload(provider, page)
        for cam in payload.get("cams", []):
            if cam.get("username", "").lower() == username.lower():
                url = _extract_playable_url(cam)
                if url:
                    return url
    return ""


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Top Cams[/COLOR]",
        TOP_CAMS_KEY,
        "List",
        site.img_cat,
        DEFAULT_PAGE,
    )
    site.add_dir(
        "[COLOR hotpink]Stripchat Cams[/COLOR]",
        "stripchat",
        "List",
        site.img_cat,
        DEFAULT_PAGE,
    )
    site.add_dir(
        "[COLOR hotpink]CamSoda Cams[/COLOR]",
        "camsoda",
        "List",
        site.img_cat,
        DEFAULT_PAGE,
    )
    site.add_dir(
        "[COLOR hotpink]MyFreeCams[/COLOR]",
        "myfreecams",
        "List",
        site.img_cat,
        DEFAULT_PAGE,
    )
    site.add_dir(
        "[COLOR hotpink]Female Cams[/COLOR]",
        "gender=female",
        "List",
        site.img_cat,
        DEFAULT_PAGE,
    )
    site.add_dir(
        "[COLOR hotpink]Male Cams[/COLOR]",
        "gender=male",
        "List",
        site.img_cat,
        DEFAULT_PAGE,
    )
    site.add_dir(
        "[COLOR hotpink]Couples Cams[/COLOR]",
        "gender=couple",
        "List",
        site.img_cat,
        DEFAULT_PAGE,
    )
    site.add_dir(
        "[COLOR hotpink]Search Model[/COLOR]",
        "any",
        "Search",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Open Model URL[/COLOR]",
        "url",
        "Search",
        site.img_search,
    )
    utils.eod()


@site.register()
def List(url=TOP_CAMS_KEY, page=DEFAULT_PAGE):
    if page is None:
        page = DEFAULT_PAGE
    else:
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = DEFAULT_PAGE

    target = (url or TOP_CAMS_KEY).strip()
    payload = _fetch_provider_payload(target, page)
    cams = payload.get("cams") or []

    if not cams:
        label = "Top Cams" if target == TOP_CAMS_KEY else target
        utils.notify("LemonCams", "No cams found for {}".format(label))
        utils.eod()
        return

    for cam in cams:
        cam_username = cam.get("username", "unknown")
        cam_provider = (cam.get("provider") or "stripchat").lower()
        stream_url = _extract_playable_url(cam)

        provider_title = SUPPORTED_PROVIDERS.get(cam_provider, cam_provider.title())
        display_label = "[COLOR hotpink][{}][/COLOR] {}".format(provider_title, cam_username)

        model_url = _build_model_page_url(cam_provider, cam_username, stream_url)
        thumb = _image_url(cam)
        plot = _format_plot(cam)

        site.add_download_link(
            display_label,
            model_url,
            "Playvid",
            thumb,
            plot,
            noDownload=True,
        )

    max_page = int(payload.get("maxPage") or 0)
    if max_page and page < max_page:
        site.add_dir(
            "[COLOR hotpink]Next Page >>[/COLOR] ({}/{})".format(page + 1, max_page),
            target,
            "List",
            site.img_next,
            page=page + 1,
        )

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        prompt = "Paste a LemonCams URL" if url == "url" else "Enter model username (e.g. nicdani_1 or camsoda:desirerodriguez)"
        site.search_dir(url, prompt)
        return

    provider, username, _ = _parse_model_identifier(keyword)
    if not provider or not username:
        utils.notify("LemonCams", "Invalid model or URL")
        utils.eod()
        return

    model_url = _build_model_page_url(provider, username)
    site.add_download_link(
        "[COLOR hotpink][{}][/COLOR] {}".format(provider.title(), username),
        model_url,
        "Playvid",
        site.img_cat,
        "Model: {}".format(username),
        noDownload=True,
    )
    utils.eod()


@site.register()
def Playvid(url, name):
    provider, username, stream_url = _parse_model_identifier(url)
    if not provider or not username:
        utils.notify("LemonCams", "Could not parse model URL")
        return

    if provider == "stripchat":
        # Stripchat serves MOUFLON-extended LL-HLS manifests with placeholder
        # segment URLs that 404 on direct playback; only stripchat.py's
        # manifest rewrite/proxy logic can play them. See its
        # _play_stripchat_model docstring.
        from resources.lib.sites.stripchat import _play_stripchat_model

        _play_stripchat_model(stream_url or username, username)
        return

    vp = utils.VideoPlayer(name, IA_check="IA")
    vp.progress.update(25, "[CR]Loading model stream[CR]")

    playable_url = stream_url

    # If stream_url is not cached in the item URL, resolve it
    if not playable_url:
        vp.progress.update(50, "[CR]Resolving live stream[CR]")
        if provider in ("camsoda", "myfreecams"):
            playable_url = _find_model_stream(provider, username)

    if not playable_url:
        vp.progress.close()
        utils.notify("LemonCams", "Model is offline or stream unavailable")
        return

    vp.progress.update(80, "[CR]Starting Playback[CR]")

    headers = {
        "User-Agent": utils.USER_AGENT,
        "Referer": "https://{}.com/".format(provider),
        "Origin": "https://{}.com".format(provider),
    }
    header_string = (
        "User-Agent={0}&Referer={1}&Origin={2}&manifest_headers=1"
    ).format(
        urllib_parse.quote(headers["User-Agent"], safe=""),
        urllib_parse.quote(headers["Referer"], safe="/"),
        urllib_parse.quote(headers["Origin"], safe="/"),
    )

    vp.play_from_direct_link("{}|{}".format(playable_url, header_string))
    vp.progress.close()
