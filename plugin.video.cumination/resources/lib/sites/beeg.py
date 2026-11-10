"""
Cumination
Copyright (C) 2015 Whitecream
Copyright (C) 2021 Team Cumination

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
import xbmc
import xbmcgui
import random
import base64
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

addon = utils.addon
site = AdultSite(
    "beeg",
    "[COLOR hotpink]Beeg[/COLOR]",
    "https://store.externulls.com/",
    "beeg.png",
    "beeg",
    category="Video Tubes",
)


def _load_json_payload(raw_payload, default):
    if not raw_payload:
        return default
    if isinstance(raw_payload, bytes):
        raw_payload = raw_payload.decode("utf-8", "ignore")
    if not isinstance(raw_payload, str):
        return default
    try:
        payload = json.loads(raw_payload)
    except (TypeError, ValueError) as exc:
        utils.kodilog("beeg: invalid JSON payload - {}".format(exc))
        return default
    return payload


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'tag/recommends?type=other&slug=index', 'Category', site.img_cat)
    site.add_dir('[COLOR hotpink]Channels[/COLOR]', site.url + 'tag/recommends?type=brand&slug=index', 'Category', site.img_cat)
    site.add_dir('[COLOR hotpink]Models[/COLOR]', site.url + 'tag/recommends?type=person&slug=index', 'Category', site.img_cat)
    List('https://store.externulls.com/facts/tag?id=27173&limit=48&offset=0', 1)
    utils.eod()


@site.register()
def List(url, page=1):
    listjson = utils.getHtml(url, site.url)
    jdata = _load_json_payload(listjson, [])
    if not isinstance(jdata, list):
        jdata = []

    for video in jdata:
        tag = ""
        slug = ""
        fc_facts = video["fc_facts"]
        for t in video["tags"]:
            if t["is_owner"]:
                tag = t["tg_name"]
                slug = t["tg_slug"]
        tag = tag if utils.PY3 else tag.encode("utf8")

        story = ""
        for data in video["file"]["data"]:
            if data["cd_column"] == "sf_name":
                name = data["cd_value"]
            if data["cd_column"] == "sf_story":
                story = data["cd_value"]

        name = name if utils.PY3 else name.encode("utf8")
        name = "{} - {}".format(tag, name)
        story = story if utils.PY3 else story.encode("utf8")

        if "fl_duration" in video["file"]:
            m, s = divmod(video["file"]["fl_duration"], 60)
            duration = "{:d}:{:02d}".format(m, s)
        else:
            duration = ""

        h = video["file"].get("fl_height")
        quality = str(h) + "p" if h else ""
        plot = tag + " - " + name + "[CR]" + story

        thumb = str(random.choice(fc_facts[0]["fc_thumbs"]))
        videodump = json.dumps(video)
        videopage = base64.b64encode(videodump.encode())
        img = "https://thumbs.externulls.com/videos/{0}/{1}.webp?size=480x270".format(
            video["file"]["id"], thumb
        )
        parts = ""
        if len(fc_facts) > 1:
            parts = "[COLOR blue] ({} parts)[/COLOR]".format(len(fc_facts))
            for fc_fact in fc_facts:
                if "fc_start" not in fc_fact:
                    parts = ""

        if len(fc_facts) == 1 and "fc_start" in fc_facts[0] and "fc_end" in fc_facts[0]:
            if (
                fc_facts[0]["fc_start"] is not None
                and fc_facts[0]["fc_end"] is not None
            ):
                min_start, sec_start = divmod(fc_facts[0]["fc_start"], 60)
                min_end, sec_end = divmod(fc_facts[0]["fc_end"], 60)
                parts = "[COLOR blue] ({:d}:{:02d} - {:d}:{:02d})[/COLOR]".format(
                    min_start, sec_start, min_end, sec_end
                )

        name += parts

        # Get tag ID for fresh fetching in Playvid
        tag_id = ""
        for t in video["tags"]:
            if t["is_owner"]:
                tag_id = t["id"]
        if not tag_id and video["tags"]:
            tag_id = video["tags"][0]["id"]

        cm_related = (
            utils.addon_sys
            + "?mode="
            + str("beeg.ContextRelated")
            + "&slug="
            + urllib_parse.quote_plus(slug)
        )
        if tag:
            cm = [
                (
                    "[COLOR violet]Tag [COLOR orange][{}][/COLOR]".format(tag),
                    "RunPlugin(" + cm_related + ")",
                )
            ]
        else:
            cm = ""

        # Pass ID and tag_id in the URL for fresh fetching
        video_id = video["file"]["id"]
        if tag_id:
            videopage = "id={}&tag_id={}".format(video_id, tag_id)
        else:
            videopage = "id={}".format(video_id)
        # Store full video data in cache as fallback
        utils.cache.set("beeg_video_{}".format(video_id), json.dumps(video))

        site.add_download_link(
            name,
            videopage,
            "Playvid",
            img,
            plot,
            contextm=cm,
            duration=duration,
            quality=quality,
        )
    if len(jdata) >= 48:
        if not page:
            page = 1
        page = min(page, 100)
        npage = url.split("offset=")[0] + "offset=" + str(page * 48)
        cm_page = (
            utils.addon_sys
            + "?mode=beeg.GotoPage"
            + "&url="
            + urllib_parse.quote_plus(npage)
            + "&np="
            + str(page)
        )
        cm = [("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")]
        site.add_dir(
            "Next Page ({})".format(str(page + 1)),
            npage,
            "List",
            site.img_next,
            page=page + 1,
            contextm=cm,
        )
    utils.eod()


@site.register()
def GotoPage(url, np):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        pg = min(int(pg), 101)
        url = url.replace(
            "offset={}".format(int(np) * 48), "offset={}".format(int(pg) * 48)
        )
        contexturl = (
            utils.addon_sys
            + "?mode="
            + "beeg.List&url="
            + urllib_parse.quote_plus(url)
            + "&page="
            + str(pg)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def ContextRelated(slug):
    url = "https://store.externulls.com/facts/tag?slug={}&get_original=true&limit=48&offset=0".format(
        slug
    )
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("beeg.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    video_id = None
    fc_facts = []

    if "id=" in url:
        try:
            query = url.split("/")[-1] if "/" in url else url
            params = dict(urllib_parse.parse_qsl(query))
            video_id = params.get("id")
            cached = utils.cache.get("beeg_video_{}".format(video_id))
            if cached:
                jdata = json.loads(cached)
                fc_facts = jdata.get("fc_facts", [])
        except Exception as e:
            utils.kodilog("beeg Playvid parse error: {}".format(e))
    else:
        try:
            listjson = base64.b64decode(url)
            try:
                decoded_json = listjson.decode("utf-8")
            except UnicodeDecodeError:
                decoded_json = listjson.decode("latin-1", "ignore")
            jdata = json.loads(decoded_json)
            fc_facts = jdata.get("fc_facts", [])
            video_id = jdata.get("file", {}).get("id")
        except Exception as e:
            utils.kodilog("beeg Playvid decode error: {}".format(e))

    if not video_id:
        vp.progress.close()
        utils.notify("Error", "Unable to determine video ID")
        return

    play_url = "https://store.externulls.com/video/play_url/{}".format(video_id)

    links = {}
    for fc_fact in fc_facts:
        fc_start = fc_fact.get("fc_start")
        fc_end = fc_fact.get("fc_end")
        if fc_start is not None and fc_end is not None:
            links["{}-{}".format(fc_start, fc_end)] = "{}?fc_start={}&fc_end={}".format(play_url, fc_start, fc_end)

    if len(links) > 1:
        play_url = utils.selector("Select part:", links)
        if not play_url:
            vp.progress.close()
            return
    elif len(links) == 1:
        play_url = list(links.values())[0]

    key = utils.getHtml(play_url, site.url)
    if not key:
        vp.progress.close()
        utils.notify("Error", "Failed to retrieve stream key")
        return

    videourl = "https://video.beeg.com/" + key.strip()
    vp.play_from_direct_link(videourl)


@site.register()
def Category(url):
    listjson = utils.getHtml(url, site.url)
    jdata = _load_json_payload(listjson, [])
    if not isinstance(jdata, list):
        jdata = []
    # Filter out items that are not categories (missing tg_name)
    categories = [cat for cat in jdata if "tg_name" in cat]
    for cat in sorted(categories, key=lambda x: x["tg_name"]):
        name = cat["tg_name"]
        slug = cat["tg_slug"]
        thumbs = cat.get("thumbs", [])
        img = 'https://thumbs.externulls.com/photos/{}/to.webp'.format(random.choice(thumbs).get('id', 0)) if thumbs else site.img_cat
        caturl = 'https://store.externulls.com/facts/tag?slug={}&limit=48&offset=0'.format(slug)
        site.add_dir(name, caturl, 'List', img)
    utils.eod()
