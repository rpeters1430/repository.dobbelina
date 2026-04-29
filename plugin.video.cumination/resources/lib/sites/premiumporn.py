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

from __future__ import annotations

import base64
import json
import re

from six.moves import urllib_parse

import xbmc
import xbmcgui
from resources.lib import utils
from resources.lib.adultsite import AdultSite

try:
    from Cryptodome.Cipher import AES
except Exception as error:
    utils.kodilog("Import Error Cryptodome: {}".format(error))

site = AdultSite(
    "premiumporn",
    "[COLOR hotpink]PremiumPorn[/COLOR]",
    "https://premiumporn.org/",
    "premiumporn.png",
    "premiumporn",
    category="Video Tubes",
)

addon = utils.addon


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Actors[/COLOR]",
        site.url + "actors/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Studios[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url + "video/page/1/?rawx_per_page=24")


@site.register()
def List(url):
    listhtml = utils.getHtml(url, error=True)
    if not listhtml or "It looks like nothing was found for this search" in listhtml:
        utils.notify("No results found", "Try a different search term")
        return

    soup = utils.parse_html(listhtml)

    cm = []
    cm_lookupinfo = utils.addon_sys + "?mode=premiumporn.Lookupinfo&url="
    cm.append(
        ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + cm_lookupinfo + ")")
    )

    for item in soup.select("[data-post-id], article, .post"):
        link = item.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage:
            continue

        name = utils.cleantext(
            utils.safe_get_text(item.select_one(".vc-title, .title"), default="")
        )
        if not name:
            name = utils.cleantext(utils.safe_get_text(link, default=""))

        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
        duration = utils.safe_get_text(
            item.select_one(".vc-dur, .duration"), default=""
        ).strip()

        site.add_download_link(
            name,
            videopage,
            "premiumporn.Play",
            img,
            name,
            duration=duration,
            contextm=cm,
        )

    # Fixed next page selector
    next_link = soup.select_one(".page-numbers.current + a, a.next.page-numbers, a.next.page-link[href]")
    if next_link:
        next_url = utils.safe_get_attr(next_link, "href", default="")
        if next_url:
            site.add_dir(
                "Next Page",
                next_url,
                "premiumporn.List",
                site.img_next,
                contextm="premiumporn.GotoPage",
            )
    utils.eod()


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    if not cathtml:
        utils.eod()
        return

    soup = utils.parse_html(cathtml)
    for item in soup.select("a.thumb, a.video-block, .list-categories a"):
        siteurl = utils.safe_get_attr(item, "href", default="")
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"])
        name = utils.safe_get_attr(img_tag, "alt", default=utils.safe_get_text(item))
        
        videos = ""
        count_tag = item.select_one(".video-datas, .count")
        if count_tag:
            videos = utils.safe_get_text(count_tag, default="").strip()
        else:
            text = utils.safe_get_text(item)
            match = re.search(r"(\d+)\s+VIDEOS", text, re.IGNORECASE)
            if match:
                videos = match.group(1)

        if not siteurl or not name:
            continue
            
        if videos:
            name = utils.cleantext(name) + "[COLOR hotpink] (" + videos + " videos)[/COLOR]"
        else:
            name = utils.cleantext(name)

        site.add_dir(name, siteurl, "List", img)

    next_link = soup.select_one(".page-numbers.current + a, a.next.page-numbers")
    if next_link:
        site.add_dir(
            "Next Page",
            utils.safe_get_attr(next_link, "href", default=""),
            "Categories",
            site.img_next,
        )
    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = url.replace("/page/{}/".format(np), "/page/{}/".format(pg))
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        contexturl = (
            utils.addon_sys
            + "?mode="
            + str(list_mode)
            + "&url="
            + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url += keyword.replace(" ", "+")
        List(url)


def base64_url_decode(data):
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    data = data.replace("-", "+").replace("_", "/")
    return base64.b64decode(data)


def decrypt_aes_gcm(payload, key, iv):
    try:
        cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
        plaintext = cipher.decrypt_and_verify(payload[:-16], payload[-16:])
        return plaintext.decode("utf-8")
    except Exception as e:
        return "Decryption failed: {}".format(str(e))


@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    match = re.compile(
        r'data-src="([^"]+)"\s+data-label="([^"]+)"', re.DOTALL | re.IGNORECASE
    ).findall(html)
    if match:
        src = {m[1]: m[0] for m in match}
        embed_url = utils.selector("Select host", src)
        if embed_url:
            if "vidara" in embed_url:
                id_match = re.search(r"/e/([^\"/]+)", embed_url)
                if id_match:
                    video_id = id_match.group(1)
                    vid_url = "https://vidara.so/api/stream"
                    data = {"filecode": video_id, "device": "web"}
                    response = utils.postHtml(
                        vid_url,
                        json_data=data,
                        headers={"Content-Type": "application/json"},
                    )
                    if response:
                        try:
                            response_json = json.loads(response)
                            video_url = response_json.get("streaming_url", "")
                            if video_url:
                                vp.play_from_direct_link(video_url)
                                return
                        except:
                            pass
                utils.notify("Oh oh", "Unable to retrieve video URL from Vidara")
                return
            else:
                parsed_embed = urllib_parse.urlparse(embed_url)
                embed_host = (parsed_embed.hostname or "").lower()
                is_bysewihe_host = embed_host == "bysewihe.com" or embed_host.endswith(".bysewihe.com")
                is_g9r6_host = embed_host == "g9r6.com" or embed_host.endswith(".g9r6.com")
                if is_bysewihe_host or is_g9r6_host:
                    id_match = re.search(r"/e/([^/]+)", embed_url)
                    if id_match:
                        video_id = id_match.group(1)
                        details_url = "https://bysewihe.com/api/videos/{}/embed/details".format(
                            video_id
                        )
                    hdr = utils.base_hdrs.copy()
                    hdr["X-Embed-Origin"] = "premiumporn.org"
                    hdr["X-Embed-Parent"] = embed_url
                    hdr["X-Embed-Referer"] = site.url
                    details_data = utils.getHtml(details_url, embed_url, headers=hdr)
                    if details_data:
                        details_json = json.loads(details_data)
                        embed = details_json.get("embed_frame_url", "")
                        api_url = "https://g9r6.com/api/videos/{}/embed/playback".format(
                            video_id
                        )
                        api_data = utils.getHtml(api_url, embed, headers=hdr)
                        if api_data:
                            encrypted_data = json.loads(api_data)
                            playback = encrypted_data["playback"]

                            iv = base64_url_decode(playback["iv"])
                            payload = base64_url_decode(playback["payload"])

                            key_part1 = base64_url_decode(playback["key_parts"][0])
                            key_part2 = base64_url_decode(playback["key_parts"][1])
                            combined_key = key_part1 + key_part2

                            result = decrypt_aes_gcm(payload, combined_key, iv)
                            try:
                                src_api = {}
                                for source in json.loads(result).get("sources", []):
                                    v_url = source.get("url", "").replace("\\u0026", "&")
                                    label = source.get("label", "")
                                    src_api[label] = v_url

                                video_url = utils.prefquality(
                                    src_api,
                                    sort_by=lambda x: 2160 if x == "4k" else int(x[:-1]),
                                    reverse=True,
                                )
                                if video_url:
                                    vp.play_from_direct_link(video_url)
                                    return
                            except:
                                pass
                vp.play_from_link_to_resolve(embed_url)
                return

    iframematch = re.compile(
        r'<iframe[^>]+src="([^"]+)"', re.DOTALL | re.IGNORECASE
    ).findall(html)
    if iframematch:
        iframe = iframematch[0]
        if iframe.startswith("//"):
            iframe = "https:" + iframe
        vp.play_from_link_to_resolve(iframe)
        return

    utils.notify("Oh oh", "No video found")


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("premiumporn.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Lookupinfo(url):
    lookup_list = [
        (
            "Actors",
            r'<a href="(https://premiumporn.org/actor/[^/]+/)" class="si-actor-card">.+?class="si-actor-name">([^<]+)</span>',
            "",
        ),
        (
            "Tags",
            r'<a href="(https://premiumporn.org/tag/[^"]+)" class="v-tag">([^<]+)<',
            "",
        ),
    ]
    lookupinfo = utils.LookupInfo("", url, "premiumporn.List", lookup_list)
    lookupinfo.getinfo()
