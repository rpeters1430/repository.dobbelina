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

import os
import sqlite3
import json
import re
import time
import sys
import subprocess
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from resources.lib import utils
from six.moves import urllib_parse
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "stripchat",
    "[COLOR hotpink]stripchat.com[/COLOR]",
    "https://stripchat.com/",
    "stripchat.png",
    "stripchat",
    True,
)


def _normalize_model_image_url(url):
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


def _live_preview_url(url, snapshot_ts=None, cache_bust=None):
    normalized = _normalize_model_image_url(url)
    if not normalized:
        return ""
    if "strpst.com/previews/" in normalized and "-thumb-small" in normalized:
        # Stripchat API currently exposes only thumb-small in many responses.
        # The corresponding thumb-big endpoint exists and gives a clearer live frame.
        normalized = normalized.replace("-thumb-small", "-thumb-big")
    # Attach snapshot/cache-bust params so Kodi does not hold stale thumbnails.
    if "strpst.com/previews/" in normalized and snapshot_ts:
        sep = "&" if "?" in normalized else "?"
        normalized = "{}{}t={}".format(normalized, sep, snapshot_ts)
    if "strpst.com/previews/" in normalized and cache_bust:
        sep = "&" if "?" in normalized else "?"
        normalized = "{}{}cb={}".format(normalized, sep, cache_bust)
    return normalized


def _model_screenshot(model, cache_bust=None):
    if not isinstance(model, dict):
        return ""
    model_id = model.get("id")
    snapshot_ts = model.get("snapshotTimestamp") or model.get(
        "popularSnapshotTimestamp"
    )
    if snapshot_ts and model_id:
        return "https://img.doppiocdn.com/thumbs/{0}/{1}_webp".format(
            snapshot_ts, model_id
        )
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
                img = _live_preview_url(
                    value.get(nested_key), snapshot_ts, cache_bust=cache_bust
                )
                if img:
                    return img
            continue
        img = _live_preview_url(value, snapshot_ts, cache_bust=cache_bust)
        if img:
            return img

    return ""


def _rewrite_mouflon_manifest_for_kodi(manifest_text):
    if not isinstance(manifest_text, str) or "#EXTM3U" not in manifest_text:
        return ""

    lines = manifest_text.splitlines()
    rewritten = []
    mouflon_uri = ""
    replaced = False
    segment_from_parts = False
    skip_next_media_placeholder = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#EXT-X-MOUFLON:URI:"):
            mouflon_uri = stripped.split(":URI:", 1)[1].strip()
            continue

        if stripped.startswith("#EXT-X-PART:"):
            duration_match = re.search(r"DURATION=([0-9.]+)", stripped)
            if mouflon_uri and duration_match:
                rewritten.append("#EXTINF:{0},".format(duration_match.group(1)))
                rewritten.append(mouflon_uri)
                replaced = True
                segment_from_parts = True
                mouflon_uri = ""
            continue

        if stripped.startswith("#EXTINF:") and segment_from_parts:
            skip_next_media_placeholder = True
            segment_from_parts = False
            continue

        if stripped and not stripped.startswith("#"):
            if skip_next_media_placeholder:
                skip_next_media_placeholder = False
                mouflon_uri = ""
                continue
            if mouflon_uri and (
                stripped.startswith("../") or stripped.endswith("/media.mp4")
            ):
                rewritten.append(mouflon_uri)
                replaced = True
                mouflon_uri = ""
                continue
            mouflon_uri = ""

        rewritten.append(line)

    if not replaced:
        return ""
    return "\n".join(rewritten) + "\n"


def _normalize_stream_cdn_url(url):
    if not isinstance(url, str) or not url:
        return url
    normalized = url
    normalized = normalized.replace("edge-hls.doppiocdn.com", "edge-hls.doppiocdn.net")
    normalized = normalized.replace("media-hls.doppiocdn.com", "media-hls.doppiocdn.net")
    normalized = normalized.replace("edge-hls.saawsedge.com", "edge-hls.saawsedge.net")
    normalized = normalized.replace("media-hls.saawsedge.com", "media-hls.saawsedge.net")
    return normalized


@site.register(default_mode=True)
def Main():
    female = utils.addon.getSetting("chatfemale") == "true"
    male = utils.addon.getSetting("chatmale") == "true"
    couple = utils.addon.getSetting("chatcouple") == "true"
    trans = utils.addon.getSetting("chattrans") == "true"
    site.add_dir(
        "[COLOR red]Refresh Stripchat images[/COLOR]",
        "",
        "clean_database",
        "",
        Folder=False,
    )

    bu = "https://stripchat.com/api/front/models?limit=80&parentTag=autoTagNew&sortBy=trending&offset=0&primaryTag="
    if female:
        site.add_dir(
            "[COLOR hotpink]Female HD[/COLOR]",
            "{0}girls&broadcastHD=true".format(bu),
            "List",
            "",
            "",
        )
        site.add_dir(
            "[COLOR hotpink]Female[/COLOR]", "{0}girls".format(bu), "List", "", ""
        )
    if couple:
        site.add_dir(
            "[COLOR hotpink]Couples HD[/COLOR]",
            "{0}couples&broadcastHD=true".format(bu),
            "List",
            "",
            "",
        )
        site.add_dir(
            "[COLOR hotpink]Couples[/COLOR]", "{0}couples".format(bu), "List", "", ""
        )
        site.add_dir(
            "[COLOR hotpink]Couples (Site)[/COLOR]",
            "https://stripchat.com/couples",
            "List2",
            "",
            "",
        )
    if male:
        site.add_dir(
            "[COLOR hotpink]Male HD[/COLOR]",
            "{0}men&broadcastHD=true".format(bu),
            "List",
            "",
            "",
        )
        site.add_dir("[COLOR hotpink]Male[/COLOR]", "{0}men".format(bu), "List", "", "")
    if trans:
        site.add_dir(
            "[COLOR hotpink]Transsexual HD[/COLOR]",
            "{0}trans&broadcastHD=true".format(bu),
            "List",
            "",
            "",
        )
        site.add_dir(
            "[COLOR hotpink]Transsexual[/COLOR]", "{0}trans".format(bu), "List", "", ""
        )
    utils.eod()


@site.register()
def List(url, page=1):
    if utils.addon.getSetting("chaturbate") == "true":
        clean_database(False)

    # utils._getHtml will automatically use FlareSolverr if Cloudflare is detected
    try:
        utils.kodilog("Stripchat: Fetching model list from API")
        response, _ = utils.get_html_with_cloudflare_retry(
            url,
            referer=site.url,
            retry_on_empty=True,
        )
        if not response:
            utils.kodilog("Stripchat: Empty response from API")
            utils.notify("Error", "Could not load Stripchat models")
            return None
        data = json.loads(response)
        model_list = data["models"]
        utils.kodilog(
            "Stripchat: Successfully loaded {} models".format(len(model_list))
        )
    except Exception as e:
        utils.kodilog("Stripchat: Error loading model list: {}".format(str(e)))
        utils.notify("Error", "Could not load Stripchat models")
        return None

    cache_bust = int(time.time())
    for model in model_list:
        raw_name = model.get("username")
        if not raw_name:
            continue
        name = utils.cleanhtml(raw_name)
        videourl = model.get("hlsPlaylist") or ""
        img = _model_screenshot(model, cache_bust=cache_bust)
        fanart = img
        subject = ""
        if model.get("groupShowTopic"):
            subject += model.get("groupShowTopic") + "[CR]"
        if model.get("country"):
            subject += "[COLOR deeppink]Location: [/COLOR]{0}[CR]".format(
                utils.get_country(model.get("country"))
            )
        if model.get("languages"):
            langs = [utils.get_language(x) for x in model.get("languages")]
            subject += "[COLOR deeppink]Languages: [/COLOR]{0}[CR]".format(
                ", ".join(langs)
            )
        if model.get("broadcastGender"):
            subject += "[COLOR deeppink]Gender: [/COLOR]{0}[CR]".format(
                model.get("broadcastGender")
            )
        if model.get("viewersCount"):
            subject += "[COLOR deeppink]Watching: [/COLOR]{0}[CR][CR]".format(
                model.get("viewersCount")
            )
        if model.get("tags"):
            subject += "[COLOR deeppink]#[/COLOR]"
            tags = [t for t in model.get("tags") if "tag" not in t.lower()]
            subject += "[COLOR deeppink] #[/COLOR]".join(tags)
        site.add_download_link(
            name, videourl, "Playvid", img, subject, noDownload=True, fanart=fanart
        )

    total_items = data.get("filteredCount", 0)
    nextp = (page * 80) < total_items
    if nextp:
        next = (page * 80) + 1
        lastpg = -1 * (-total_items // 80)
        page += 1
        nurl = re.sub(r"offset=\d+", "offset={0}".format(next), url)
        site.add_dir(
            "Next Page.. (Currently in Page {0} of {1})".format(page - 1, lastpg),
            nurl,
            "List",
            site.img_next,
            page,
        )

    utils.eod()


@site.register(clean_mode=True)
def clean_database(showdialog=True):
    conn = sqlite3.connect(utils.TRANSLATEPATH("special://database/Textures13.db"))
    try:
        with conn:
            for domain_fragment in (".strpst.com", ".doppiocdn.com"):
                pattern = "%" + domain_fragment + "%"
                rows = conn.execute(
                    "SELECT id, cachedurl FROM texture WHERE url LIKE ?;",
                    (pattern,),
                ).fetchall()
                for row in rows:
                    conn.execute("DELETE FROM sizes WHERE idtexture = ?;", (row[0],))
                    try:
                        os.remove(utils.TRANSLATEPATH("special://thumbnails/" + row[1]))
                    except Exception as e:
                        utils.kodilog(
                            "@@@@Cumination: Silent failure in stripchat: " + str(e)
                        )
                conn.execute("DELETE FROM texture WHERE url LIKE ?;", (pattern,))
            if showdialog:
                utils.notify("Finished", "Stripchat images cleared")
    except Exception as e:
        utils.kodilog("@@@@Cumination: Silent failure in stripchat: " + str(e))


@site.register()
def Playvid(url, name):
    vp = utils.VideoPlayer(name, IA_check="IA")
    vp.progress.update(25, "[CR]Loading video page[CR]")

    def _load_model_details(model_name):
        headers = {
            "User-Agent": utils.USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://stripchat.com",
            "Referer": "https://stripchat.com/{0}".format(model_name),
        }
        # The external widget API returns rich stream data (stream.url, stream.urls,
        # snapshotUrl etc.) and supports modelsList lookup by username.
        endpoint = (
            "https://stripchat.com/api/external/v4/widget/?limit=1&modelsList={0}"
        )
        try:
            utils.kodilog(
                "Stripchat: Fetching model details: {}".format(
                    endpoint.format(model_name)
                )
            )
            response, _ = utils.get_html_with_cloudflare_retry(
                endpoint.format(model_name),
                site.url,
                headers=headers,
                retry_on_empty=True,
            )
            if not response:
                utils.kodilog("Stripchat: Empty response from widget endpoint")
                return None
            payload = json.loads(response)
            models = payload.get("models") if isinstance(payload, dict) else None
            if models and len(models) > 0:
                for model in models:
                    if model.get("username", "").lower() == model_name.lower():
                        utils.kodilog(
                            "Stripchat: Successfully loaded model details for {}".format(
                                model_name
                            )
                        )
                        return model
                utils.kodilog(
                    "Stripchat: Widget API returned models but none matched {}".format(
                        model_name
                    )
                )
                if models:
                    utils.kodilog(
                        "Stripchat: First returned model was: {}".format(
                            models[0].get("username")
                        )
                    )
            else:
                utils.kodilog("Stripchat: No models in widget response")
        except json.JSONDecodeError as e:
            utils.kodilog("Stripchat: JSON decode error: {}".format(str(e)))
        except Exception as e:
            utils.kodilog("Stripchat: Error loading model details: {}".format(str(e)))
        return None

    def _pick_stream(model_data, fallback_url):
        candidates = []
        stream_info = model_data.get("stream") if model_data else None
        is_online_flag = None
        manifest_probe_cache = {}
        manifest_probe_errors = {}

        def _mirror_saaws_to_doppi(stream_url):
            if not isinstance(stream_url, str) or "saawsedge.com" not in stream_url:
                return None
            return stream_url.replace(
                "edge-hls.saawsedge.com", "edge-hls.doppiocdn.com"
            )

        # Treat online flags as advisory only; keep stream candidates if present.
        if model_data:
            is_online_values = [
                model_data.get("isOnline"),
                model_data.get("isBroadcasting"),
            ]
            explicit_values = [v for v in is_online_values if isinstance(v, bool)]
            if explicit_values:
                is_online_flag = any(explicit_values)
                if not is_online_flag:
                    utils.kodilog(
                        "Stripchat: Model {} reported offline by API".format(name)
                    )

        if isinstance(stream_info, dict):
            # Explicit urls map (new API structure)
            urls_map = stream_info.get("urls") or stream_info.get("files") or {}
            hls_map = urls_map.get("hls") if isinstance(urls_map, dict) else {}
            if isinstance(hls_map, dict):
                for quality, data in hls_map.items():
                    quality_label = str(quality).lower()
                    if isinstance(data, dict):
                        for key in ("absolute", "https", "url", "src"):
                            stream_url = data.get(key)
                            if isinstance(stream_url, str) and stream_url.startswith(
                                "http"
                            ):
                                utils.kodilog(
                                    "Stripchat: Found stream candidate: {} - {}".format(
                                        quality_label, stream_url[:80]
                                    )
                                )
                                candidates.append((quality_label, stream_url))
                                break
                    elif isinstance(data, str) and data.startswith("http"):
                        utils.kodilog(
                            "Stripchat: Found stream candidate: {} - {}".format(
                                quality_label, data[:80]
                            )
                        )
                        candidates.append((quality_label, data))
            elif isinstance(urls_map, dict):
                # Flat quality dict: stream.urls = {"480p": "url", "240p": "url", ...}
                for quality, data in urls_map.items():
                    quality_label = str(quality).lower()
                    if isinstance(data, str) and data.startswith("http"):
                        utils.kodilog(
                            "Stripchat: Found quality stream: {} - {}".format(
                                quality_label, data[:80]
                            )
                        )
                        candidates.append((quality_label, data))
                    elif isinstance(data, dict):
                        for key in ("absolute", "https", "url", "src"):
                            stream_url = data.get(key)
                            if isinstance(stream_url, str) and stream_url.startswith(
                                "http"
                            ):
                                utils.kodilog(
                                    "Stripchat: Found quality stream: {} - {}".format(
                                        quality_label, stream_url[:80]
                                    )
                                )
                                candidates.append((quality_label, stream_url))
                                break
            # Some responses keep direct URL on stream['url']
            stream_url = stream_info.get("url")
            if isinstance(stream_url, str) and stream_url.startswith("http"):
                utils.kodilog(
                    "Stripchat: Found direct stream URL: {}".format(stream_url[:80])
                )
                candidates.append(("direct", stream_url))
        # Legacy field on model root
        if model_data and isinstance(model_data.get("hlsPlaylist"), str):
            hls_url = model_data["hlsPlaylist"]
            utils.kodilog("Stripchat: Found hlsPlaylist: {}".format(hls_url[:80]))
            candidates.append(("playlist", hls_url))
        if isinstance(fallback_url, str) and fallback_url.startswith("http"):
            utils.kodilog("Stripchat: Using fallback URL: {}".format(fallback_url[:80]))
            candidates.append(("fallback", fallback_url))

        mirrored = []
        for label, candidate_url in list(candidates):
            mirror_url = _mirror_saaws_to_doppi(candidate_url)
            if mirror_url and mirror_url != candidate_url:
                utils.kodilog(
                    "Stripchat: Added mirrored stream candidate: {} - {}".format(
                        label, mirror_url[:80]
                    )
                )
                mirrored.append(("{}-mirror".format(label), mirror_url))
        candidates.extend(mirrored)

        # Some list URLs are pinned to low variants like "<id>_240p.m3u8".
        # Try to promote those to "<id>.m3u8" (often "source"/best stream) when valid.
        def _promote_variant_to_source_url(stream_url):
            if not isinstance(stream_url, str) or ".m3u8" not in stream_url:
                return None
            match = re.search(r"/master/(\d+)_\d{3,4}p\.m3u8($|\?)", stream_url)
            if not match:
                return None

            source_url = stream_url.replace(
                "/master/{}_".format(match.group(1)),
                "/master/{}.".format(match.group(1)),
            )
            source_url = re.sub(
                r"/master/(\d+)\.\d{3,4}p\.m3u8",
                r"/master/\1.m3u8",
                source_url,
            )
            if source_url == stream_url:
                return None

            try:
                probe_headers = {
                    "User-Agent": utils.USER_AGENT,
                    "Origin": "https://stripchat.com",
                    "Referer": "https://stripchat.com/{0}".format(name),
                    "Accept": "application/x-mpegURL,application/vnd.apple.mpegurl,*/*",
                }
                probe_data = utils._getHtml(
                    source_url,
                    "https://stripchat.com/{0}".format(name),
                    headers=probe_headers,
                    error="throw",
                )
                if isinstance(probe_data, str) and "#EXTM3U" in probe_data:
                    utils.kodilog(
                        "Stripchat: Promoted variant stream to source playlist: {}".format(
                            source_url[:80]
                        )
                    )
                    return source_url
            except Exception as e:
                utils.kodilog(
                    "Stripchat: Source playlist probe failed for {}: {}".format(
                        source_url[:80], str(e)
                    )
                )
            return None

        def _fetch_manifest_text(manifest_url):
            if not isinstance(manifest_url, str) or ".m3u8" not in manifest_url:
                return ""
            if manifest_url in manifest_probe_cache:
                return manifest_probe_cache[manifest_url]
            try:
                headers = {
                    "User-Agent": utils.USER_AGENT,
                    "Origin": "https://stripchat.com",
                    "Referer": "https://stripchat.com/{0}".format(name),
                    "Accept": "application/x-mpegURL,application/vnd.apple.mpegurl,*/*",
                }
                text = utils._getHtml(
                    manifest_url,
                    "https://stripchat.com/{0}".format(name),
                    headers=headers,
                    error="throw",
                )
                manifest_probe_errors.pop(manifest_url, None)
            except Exception as e:
                utils.kodilog(
                    "Stripchat: Manifest probe failed for {}: {}".format(
                        manifest_url[:80], str(e)
                    )
                )
                text = ""
                err = str(e).lower()
                if (
                    "name or service not known" in err
                    or "could not resolve host" in err
                ):
                    manifest_probe_errors[manifest_url] = "dns"
            if (not isinstance(text, str) or "#EXTM3U" not in text) and isinstance(
                manifest_url, str
            ):
                # Some CDN paths (notably doppiocdn media manifests) are easier to
                # inspect without custom headers; use requests as a probe fallback.
                try:
                    resp = requests.get(manifest_url, timeout=8)
                    if resp.status_code == 200 and "#EXTM3U" in resp.text:
                        text = resp.text
                        manifest_probe_errors.pop(manifest_url, None)
                except Exception:
                    pass
            manifest_probe_cache[manifest_url] = text if isinstance(text, str) else ""
            return manifest_probe_cache[manifest_url]

        def _is_ad_or_stub_manifest(manifest_text):
            if not isinstance(manifest_text, str) or "#EXTM3U" not in manifest_text:
                return False
            lower = manifest_text.lower()
            if "#ext-x-mouflon-advert" in lower:
                return True
            if "/cpa/v2/" in lower:
                return True
            # Treat short VOD endlists as non-live/ad stubs for cam playback.
            if "#ext-x-playlist-type:vod" in lower and "#ext-x-endlist" in lower:
                return True
            return False

        def _manifest_has_parent_relative_segments(manifest_text):
            if not isinstance(manifest_text, str) or "#EXTM3U" not in manifest_text:
                return False
            for line in manifest_text.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("../"):
                    return True
            return False

        def _candidate_is_ad_path(candidate_url):
            master_text = _fetch_manifest_text(candidate_url)
            if not master_text or "#EXTM3U" not in master_text:
                return False

            # If this manifest itself is an ad/stub, reject immediately.
            if _is_ad_or_stub_manifest(master_text):
                return True

            # If this is a master playlist, inspect child playlists as well.
            child_urls = [
                line.strip()
                for line in master_text.splitlines()
                if line.strip() and not line.startswith("#")
            ]
            for child_url in child_urls[:2]:
                child_text = _fetch_manifest_text(child_url)
                if _is_ad_or_stub_manifest(child_text):
                    return True
            return False

        def _merge_query(url, params):
            parsed = urlparse(url)
            query = parse_qs(parsed.query, keep_blank_values=True)
            for key, value in params.items():
                if key not in query:
                    query[key] = [value]
            new_query = urlencode(query, doseq=True)
            return urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    new_query,
                    parsed.fragment,
                )
            )

        def _derive_signed_media_candidate(master_url):
            master_text = _fetch_manifest_text(master_url)
            if not master_text or "#EXTM3U" not in master_text:
                return None

            mouflon = re.search(r"#EXT-X-MOUFLON:PSCH:(v\d+):([^\r\n]+)", master_text)
            if not mouflon:
                return None

            psch = mouflon.group(1)
            pkey = mouflon.group(2).strip()
            if not pkey:
                return None

            child_urls = [
                line.strip()
                for line in master_text.splitlines()
                if line.strip() and not line.startswith("#")
            ]
            for child_url in child_urls[:2]:
                signed_child_url = _merge_query(
                    child_url,
                    {"psch": psch, "pkey": pkey},
                )
                child_text = _fetch_manifest_text(signed_child_url)
                if not child_text or "#EXTM3U" not in child_text:
                    continue
                if _is_ad_or_stub_manifest(child_text):
                    continue
                if _manifest_has_parent_relative_segments(child_text):
                    utils.kodilog(
                        "Stripchat: Skipping signed media candidate with parent-relative segments: {}".format(
                            signed_child_url[:80]
                        )
                    )
                    continue
                utils.kodilog(
                    "Stripchat: Derived signed media candidate: {}".format(
                        signed_child_url[:80]
                    )
                )
                return signed_child_url
            return None

        promoted = []
        for _, candidate_url in list(candidates):
            source_url = _promote_variant_to_source_url(candidate_url)
            if source_url:
                promoted.append(("source-derived", source_url))
            signed_media_url = _derive_signed_media_candidate(candidate_url)
            if signed_media_url:
                promoted.append(("media-signed", signed_media_url))
        candidates.extend(promoted)

        if not candidates:
            utils.kodilog("Stripchat: No stream candidates found")
            return None, is_online_flag

        def quality_score(label, stream_url):
            if not label:
                label = ""
            score = -1
            label = label.lower()
            if "source" in label:
                score = max(score, 10000)
            match = re.search(r"(\d{3,4})p", label)
            if match:
                try:
                    score = max(score, int(match.group(1)))
                except ValueError:
                    pass

            # Fallback: infer quality from URL pattern when labels are generic.
            if isinstance(stream_url, str):
                if re.search(r"/master/\d+\.m3u8($|\?)", stream_url):
                    score = max(score, 9000)
                url_quality = re.search(r"_(\d{3,4})p\.m3u8($|\?)", stream_url)
                if url_quality:
                    try:
                        score = max(score, int(url_quality.group(1)))
                    except ValueError:
                        pass
            return score

        evaluated = []
        for label, candidate_url in candidates:
            ad_path = _candidate_is_ad_path(candidate_url)
            reachable = manifest_probe_errors.get(candidate_url) != "dns"
            evaluated.append(
                {
                    "label": label,
                    "url": candidate_url,
                    "reachable": reachable,
                    "ad": ad_path,
                    "score": quality_score(label, candidate_url),
                }
            )

        # saawsedge frequently fails DNS in some networks; if we discovered any
        # non-saaws candidate, avoid selecting saaws URLs.
        has_non_saaws = any("saawsedge.com" not in c["url"] for c in evaluated)
        if has_non_saaws:
            filtered = [c for c in evaluated if "saawsedge.com" not in c["url"]]
            if filtered:
                utils.kodilog(
                    "Stripchat: Excluding saawsedge candidates in favor of reachable mirrored CDN"
                )
                evaluated = filtered

        preferred_reachable = [c for c in evaluated if c["reachable"] and not c["ad"]]
        preferred_unreachable = [
            c for c in evaluated if (not c["reachable"]) and (not c["ad"])
        ]
        ad_reachable = [c for c in evaluated if c["reachable"] and c["ad"]]
        if preferred_reachable:
            preferred = preferred_reachable
        elif ad_reachable:
            utils.kodilog(
                "Stripchat: Non-ad streams unresolved and reachable streams are ad-only; skipping playback"
            )
            return None, is_online_flag
        elif preferred_unreachable:
            utils.kodilog(
                "Stripchat: Only unresolved non-ad streams available; trying unresolved fallback"
            )
            preferred = preferred_unreachable
        else:
            utils.kodilog(
                "Stripchat: Only ad stream candidates available; skipping playback"
            )
            return None, is_online_flag

        preferred.sort(
            key=lambda c: (c["score"], 1 if "doppiocdn.com" in c["url"] else 0),
            reverse=True,
        )
        selected_url = preferred[0]["url"]
        selected_label = preferred[0]["label"]
        utils.kodilog(
            "Stripchat: Selected stream: {} - {}".format(
                selected_label, selected_url[:80]
            )
        )

        # Don't try to parse master playlists - just use the selected URL directly
        # The master playlist URL is already the correct stream to use
        # Parsing it and selecting variants often picks the wrong quality or causes auth failures
        utils.kodilog(
            "Stripchat: Using selected stream URL directly without master playlist parsing"
        )

        return selected_url, is_online_flag

    # Load current model details
    utils.kodilog("Stripchat: Loading details for model: {}".format(name))
    model_data = _load_model_details(name)

    if not model_data:
        vp.progress.close()
        utils.kodilog("Stripchat: Failed to load model details")
        utils.notify("Stripchat", "Model not found or offline")
        return

    # Pick best stream URL
    stream_url, is_online_flag = _pick_stream(model_data, url)
    if not stream_url:
        vp.progress.close()
        utils.kodilog("Stripchat: No stream URL available")
        if is_online_flag is False:
            utils.notify("Stripchat", "Model is offline")
        else:
            utils.notify("Stripchat", "Unable to locate stream URL")
        return

    # Validate stream URL
    if not stream_url.startswith("http"):
        vp.progress.close()
        utils.kodilog("Stripchat: Invalid stream URL: {}".format(stream_url))
        utils.notify("Stripchat", "Invalid stream URL")
        return

    utils.kodilog("Stripchat: Final stream URL: {}".format(stream_url[:100]))
    vp.progress.update(85, "[CR]Found Stream[CR]")

    # Verify inputstream.adaptive is available for HLS streams
    # The check_inputstream() call will offer to install if missing
    try:
        from inputstreamhelper import Helper

        is_helper = Helper("hls")
        vp.progress.update(90, "[CR]Checking inputstream.adaptive[CR]")
        if not is_helper.check_inputstream():
            vp.progress.close()
            utils.kodilog(
                "Stripchat: inputstream.adaptive check failed - HLS streams require it"
            )
            utils.notify(
                "Stripchat",
                "inputstream.adaptive is required. Please install it from Kodi settings.",
                duration=8000,
            )
            return
    except Exception as e:
        utils.kodilog("Stripchat: Error checking inputstream: {}".format(str(e)))
        # Continue anyway - let utils.playvid handle it

    # Build headers for HLS stream
    ua = urllib_parse.quote(utils.USER_AGENT, safe="")
    origin_enc = urllib_parse.quote("https://stripchat.com", safe="")
    referer_enc = urllib_parse.quote("https://stripchat.com/{0}".format(name), safe="")
    accept_enc = urllib_parse.quote("application/x-mpegURL", safe="")
    accept_lang = urllib_parse.quote("en-US,en;q=0.9", safe="")
    ia_headers = (
        "User-Agent={0}&Origin={1}&Referer={2}&Accept={3}&Accept-Language={4}".format(
            ua, origin_enc, referer_enc, accept_enc, accept_lang
        )
    )

    def _build_local_mouflon_stream(selected_stream_url):
        proxy_headers = {
            "User-Agent": utils.USER_AGENT,
            "Origin": "https://stripchat.com",
            "Referer": "https://stripchat.com/{0}".format(name),
            "Accept": "application/x-mpegURL,application/vnd.apple.mpegurl,*/*",
        }
        manifest_text = ""
        active_stream_url = selected_stream_url
        candidate_fetch_urls = [_normalize_stream_cdn_url(selected_stream_url)]
        if candidate_fetch_urls[0] != selected_stream_url:
            candidate_fetch_urls.append(selected_stream_url)
        for fetch_url in candidate_fetch_urls:
            try:
                manifest_text = utils._getHtml(
                    fetch_url,
                    "https://stripchat.com/{0}".format(name),
                    headers=proxy_headers,
                    error="throw",
                )
            except Exception:
                manifest_text = ""
            if (
                not isinstance(manifest_text, str) or "#EXTM3U" not in manifest_text
            ) and (isinstance(fetch_url, str) and ".m3u8" in fetch_url):
                try:
                    manifest_text = requests.get(fetch_url, timeout=8).text
                except Exception:
                    manifest_text = ""
            if isinstance(manifest_text, str) and "#EXTM3U" in manifest_text:
                active_stream_url = fetch_url
                break
        rewritten = _rewrite_mouflon_manifest_for_kodi(manifest_text)
        if not rewritten:
            return None

        temp_dir = utils.TRANSLATEPATH("special://temp/stripchat")
        if not os.path.isdir(temp_dir):
            os.makedirs(temp_dir)

        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:64] or "stripchat"
        child_path = os.path.join(temp_dir, "{}_live.m3u8".format(safe_name))
        parent_path = os.path.join(temp_dir, "{}_live.mp4".format(safe_name))

        with open(child_path, "w") as child_file:
            child_file.write(rewritten)
        with open(parent_path, "w") as parent_file:
            parent_file.write(
                "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-STREAM-INF:PROGRAM-ID=1\n{0}\n".format(
                    child_path
                )
            )

        updater_python = None
        executable = getattr(sys, "executable", "") or ""
        if os.path.basename(executable).lower().startswith("python"):
            updater_python = executable
        else:
            updater_python = "python"

        updater_script = (
            "import sys,time,requests\n"
            "url,path=sys.argv[1],sys.argv[2]\n"
            "session=requests.Session()\n"
            "deadline=time.time()+7200\n"
            "last=''\n"
            "while time.time()<deadline:\n"
            "    try:\n"
            "        text=session.get(url, timeout=10).text\n"
            "        if '#EXTM3U' not in text:\n"
            "            time.sleep(1)\n"
            "            continue\n"
            "        out=[]\n"
            "        mou=''\n"
            "        replaced=False\n"
            "        for raw in text.splitlines():\n"
            "            stripped=raw.strip()\n"
            "            if stripped.startswith('#EXT-X-MOUFLON:URI:'):\n"
            "                mou=stripped.split(':URI:', 1)[1].strip()\n"
            "                continue\n"
            "            if stripped and not stripped.startswith('#'):\n"
            "                if mou and (stripped.startswith('../') or stripped.endswith('/media.mp4')):\n"
            "                    out.append(mou)\n"
            "                    replaced=True\n"
            "                    mou=''\n"
            "                    continue\n"
            "                mou=''\n"
            "            out.append(raw)\n"
            "        if replaced:\n"
            "            payload='\\n'.join(out)+'\\n'\n"
            "            if payload!=last:\n"
            "                with open(path, 'w') as fh:\n"
            "                    fh.write(payload)\n"
            "                last=payload\n"
            "    except Exception:\n"
            "        pass\n"
            "    time.sleep(1)\n"
        )

        try:
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            subprocess.Popen(
                [updater_python, "-c", updater_script, active_stream_url, child_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=creationflags,
                close_fds=True,
            )
            utils.kodilog(
                "Stripchat: Started local MOUFLON manifest proxy: {}".format(
                    parent_path
                )
            )
        except Exception as e:
            utils.kodilog(
                "Stripchat: Failed to start manifest proxy updater: {}".format(str(e))
            )

        return parent_path

    proxy_stream = _build_local_mouflon_stream(stream_url)
    if proxy_stream:
        stream_url = proxy_stream
        ia_headers = ""

    utils.kodilog("Stripchat: Starting playback")
    if ia_headers:
        vp.play_from_direct_link(stream_url + "|" + ia_headers)
    else:
        vp.play_from_direct_link(stream_url)


@site.register()
def List2(url):
    site.add_download_link(
        "[COLOR red][B]Refresh[/B][/COLOR]",
        url,
        "utils.refresh",
        "",
        "",
        noDownload=True,
    )
    if utils.addon.getSetting("online_only") == "true":
        url = url + "/?online_only=1"
        site.add_download_link(
            "[COLOR red][B]Show all models[/B][/COLOR]",
            url,
            "online",
            "",
            "",
            noDownload=True,
        )
    else:
        site.add_download_link(
            "[COLOR red][B]Show only models online[/B][/COLOR]",
            url,
            "online",
            "",
            "",
            noDownload=True,
        )

    if utils.addon.getSetting("chaturbate") == "true":
        clean_database(False)

    headers = {"X-Requested-With": "XMLHttpRequest"}
    data = utils._getHtml(url, site.url, headers=headers)

    # BeautifulSoup migration
    soup = utils.parse_html(data)
    if not soup:
        utils.eod()
        return

    # Check for window.LOADABLE_DATA first (modern client-side rendering)
    scripts = soup.find_all("script")
    found_models = False
    for script in scripts:
        script_text = script.string or ""
        if "window.LOADABLE_DATA" in script_text:
            try:
                # Extract JSON from window.LOADABLE_DATA = {...};
                json_match = re.search(
                    r"window\.LOADABLE_DATA\s*=\s*({.*?});", script_text
                )
                if json_match:
                    payload = json.loads(json_match.group(1))
                    model_list = []

                    # Dig through the nested structure
                    # It's usually in payload['categoryTagPage']['models'] or payload['models']
                    if "models" in payload:
                        model_list = payload["models"]
                    elif (
                        "categoryTagPage" in payload
                        and "models" in payload["categoryTagPage"]
                    ):
                        model_list = payload["categoryTagPage"]["models"]

                    if model_list:
                        found_models = True
                        for model in model_list:
                            raw_name = model.get("username")
                            if not raw_name:
                                continue
                            name = utils.cleanhtml(raw_name)
                            videourl = model.get("hlsPlaylist") or ""
                            img = _model_screenshot(model)
                            # Handle offline/profile links
                            if model.get("status") == "off":
                                name = "[COLOR hotpink][Offline][/COLOR] " + name
                                videourl = "  "

                            site.add_download_link(
                                name,
                                videourl,
                                "Playvid",
                                img,
                                "",
                                fanart=img,
                            )
                        break
            except Exception as e:
                utils.kodilog(
                    "Stripchat List2: Error parsing LOADABLE_DATA: {}".format(str(e))
                )

    if not found_models:
        # Fallback to traditional HTML parsing
        # Find the top_ranks or top_others section
        section = soup.find(class_="top_ranks") or soup.find(class_="top_others")
        if section:
            # Find all model entries with top_thumb class
            models = section.find_all(class_="top_thumb")
            for model in models:
                try:
                    link = model.find("a", href=True)
                    if not link:
                        continue
                    model_url = utils.safe_get_attr(link, "href", default="")

                    img_tag = model.find("img")
                    img = utils.safe_get_attr(img_tag, "src", ["data-src"], "")
                    if img and not img.startswith("http"):
                        img = "https:" + img

                    name_tag = model.find(class_="mn_lc")
                    name = utils.safe_get_text(name_tag, default="Unknown")

                    if "profile" in model_url:
                        name = "[COLOR hotpink][Offline][/COLOR] " + name
                        model_url = "  "
                    elif model_url.startswith("/"):
                        model_url = model_url[1:]

                    site.add_download_link(
                        name,
                        model_url,
                        "Playvid",
                        img,
                        "",
                        fanart=img,
                    )
                except Exception as e:
                    utils.kodilog(
                        "Stripchat List2: Error parsing model entry: {}".format(str(e))
                    )
                    continue

    utils.eod()


@site.register()
def List3(url):
    site.add_download_link(
        "[COLOR red][B]Refresh[/B][/COLOR]",
        url,
        "utils.refresh",
        "",
        "",
        noDownload=True,
    )
    if utils.addon.getSetting("online_only") == "true":
        url = url + "/?online_only=1"
        site.add_download_link(
            "[COLOR red][B]Show all models[/B][/COLOR]",
            url,
            "online",
            "",
            "",
            noDownload=True,
        )
    else:
        site.add_download_link(
            "[COLOR red][B]Show only models online[/B][/COLOR]",
            url,
            "online",
            "",
            "",
            noDownload=True,
        )

    if utils.addon.getSetting("chaturbate") == "true":
        clean_database(False)

    headers = {"X-Requested-With": "XMLHttpRequest"}
    data = utils._getHtml(url, site.url, headers=headers)

    # BeautifulSoup migration
    soup = utils.parse_html(data)
    if not soup:
        utils.eod()
        return

    # Check for window.LOADABLE_DATA first (modern client-side rendering)
    scripts = soup.find_all("script")
    found_models = False
    for script in scripts:
        script_text = script.string or ""
        if "window.LOADABLE_DATA" in script_text:
            try:
                # Extract JSON from window.LOADABLE_DATA = {...};
                json_match = re.search(
                    r"window\.LOADABLE_DATA\s*=\s*({.*?});", script_text
                )
                if json_match:
                    payload = json.loads(json_match.group(1))
                    model_list = []

                    if "models" in payload:
                        model_list = payload["models"]
                    elif (
                        "categoryTagPage" in payload
                        and "models" in payload["categoryTagPage"]
                    ):
                        model_list = payload["categoryTagPage"]["models"]

                    if model_list:
                        found_models = True
                        for model in model_list:
                            raw_name = model.get("username")
                            if not raw_name:
                                continue
                            name = utils.cleanhtml(raw_name)
                            videourl = model.get("hlsPlaylist") or ""
                            img = _model_screenshot(model)
                            # Handle offline/profile links
                            if model.get("status") == "off":
                                name = "[COLOR hotpink][Offline][/COLOR] " + name
                                videourl = "  "

                            site.add_download_link(
                                name,
                                videourl,
                                "Playvid",
                                img,
                                "",
                                fanart=img,
                            )
                        break
            except Exception as e:
                utils.kodilog(
                    "Stripchat List3: Error parsing LOADABLE_DATA: {}".format(str(e))
                )

    if not found_models:
        # Fallback to traditional HTML parsing
        # Find the top_ranks section
        section = soup.find(class_="top_ranks")
        if section:
            # Find all model entries with top_thumb class
            models = section.find_all(class_="top_thumb")
            for model in models:
                try:
                    link = model.find("a", href=True)
                    if not link:
                        continue
                    model_url = utils.safe_get_attr(link, "href", default="")

                    img_tag = model.find("img")
                    img = utils.safe_get_attr(img_tag, "src", ["data-src"], "")
                    if img and not img.startswith("http"):
                        img = "https:" + img

                    name_tag = model.find(class_="mn_lc")
                    name = utils.safe_get_text(name_tag, default="Unknown")

                    if "profile" in model_url:
                        name = "[COLOR hotpink][Offline][/COLOR] " + name
                        model_url = "  "
                    elif model_url.startswith("/"):
                        model_url = model_url[1:]

                    site.add_download_link(
                        name,
                        model_url,
                        "Playvid",
                        img,
                        "",
                        fanart=img,
                    )
                except Exception as e:
                    utils.kodilog(
                        "Stripchat List3: Error parsing model entry: {}".format(str(e))
                    )
                    continue

    utils.eod()


@site.register()
def online(url):
    if utils.addon.getSetting("online_only") == "true":
        utils.addon.setSetting("online_only", "false")
    else:
        utils.addon.setSetting("online_only", "true")
    utils.refresh()
