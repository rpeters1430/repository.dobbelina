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
from six.moves import urllib_parse, urllib_error
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "bongacams",
    "[COLOR hotpink]BongaCams[/COLOR]",
    "https://bongacams.com/",
    "bongacams.png",
    "bongacams",
    webcam=True,
    category="Cams & Live",
)


@site.register(default_mode=True)
def Main():
    female = utils.addon.getSetting("chatfemale") == "true"
    male = utils.addon.getSetting("chatmale") == "true"
    couple = utils.addon.getSetting("chatcouple") == "true"
    trans = utils.addon.getSetting("chattrans") == "true"
    site.add_dir(
        "[COLOR red]Refresh bongacams.com images[/COLOR]",
        "",
        "clean_database",
        "",
        Folder=False,
    )
    site.add_dir(
        "Hour's TOP chat rooms",
        "https://bongacams.com/contest/top-room?cp=1",
        "List2",
        "",
        "",
    )
    bu = "https://tools.bongacash.com/promo.php?c=226355&type=api&api_type=json&categories[]="
    if female:
        site.add_dir(
            "[COLOR hotpink]Female[/COLOR]", "{0}female".format(bu), "List", "", ""
        )
        site.add_dir(
            "[COLOR yellow]Online Favorites[/COLOR]",
            "https://tools.bongacash.com/promo.php?c=226355&type=api&api_type=json",
            "onlineFav",
            "",
            "",
        )
        site.add_dir(
            "  International - Queen of Queens",
            site.url + "contest/queen-of-queens-international",
            "List3",
            "",
            "",
        )
        site.add_dir(
            "  North America & Western Europe's - Queen of Queens",
            site.url + "contest/queen-of-queens",
            "List3",
            "",
            "",
        )
        site.add_dir(
            "  Latin American - Queen of Queens",
            site.url + "contest/queen-of-queens-latin-america",
            "List3",
            "",
            "",
        )
    if couple:
        site.add_dir(
            "[COLOR hotpink]Couples[/COLOR]", "{0}couples".format(bu), "List", "", ""
        )
        site.add_dir(
            "  Couples' Top 50", site.url + "contest/top-couple-models", "List3", "", ""
        )
    if male:
        site.add_dir(
            "[COLOR hotpink]Male[/COLOR]", "{0}male".format(bu), "List", "", ""
        )
        site.add_dir(
            "  Guys and Trans' Top 10",
            site.url + "contest/top-male-models",
            "List3",
            "",
            "",
        )
    if trans:
        site.add_dir(
            "[COLOR hotpink]Transsexual[/COLOR]",
            "{0}transsexual".format(bu),
            "List",
            "",
            "",
        )
        site.add_dir(
            "  Guys and Trans' Top 10",
            site.url + "contest/top-male-models",
            "List3",
            "",
            "",
        )

    utils.eod()


def _loads_json(data):
    if not data:
        return None
    if isinstance(data, (list, dict)):
        return data
    payload = data.strip()
    if not payload:
        return None
    try:
        return json.loads(payload)
    except Exception:
        # Some endpoints prepend anti-JSON or banner text.
        match = re.search(r"(\{.*\}|\[.*\])", payload, re.DOTALL)
        if not match:
            return None
        return json.loads(match.group(1))


def _model_subject(model):
    subject = ""
    if model.get("is_geo"):
        subject += "[B][COLOR hotpink]GeoLocked[/COLOR][/B]\n"
    if model.get("hometown"):
        subject += "Location: {}".format(model.get("hometown"))
    if model.get("homecountry"):
        subject += (
            ", {}\n".format(model.get("homecountry"))
            if subject and not subject.endswith("\n")
            else "Location: {}\n".format(model.get("homecountry"))
        )
    if model.get("ethnicity"):
        subject += "\n- {}\n".format(model.get("ethnicity"))
    if model.get("primary_language"):
        subject += "- Speaks {}\n".format(model.get("primary_language"))
    if model.get("secondary_language"):
        subject = subject[:-1] + ", {}\n".format(model.get("secondary_language"))
    if model.get("eye_color"):
        subject += "- {} Eyed\n".format(model.get("eye_color"))
    if model.get("hair_color"):
        subject = subject[:-1] + " {}\n".format(model.get("hair_color"))
    if model.get("height"):
        subject += "- {} tall\n".format(model.get("height"))
    if model.get("weight"):
        subject += "- {} weight\n".format(model.get("weight"))
    if model.get("bust_penis_size"):
        subject += (
            "- {} Boobs\n".format(model.get("bust_penis_size"))
            if "Female" in model.get("gender", "")
            else "- {} Cock\n".format(model.get("bust_penis_size"))
        )
    if model.get("pubic_hair"):
        subject = subject[:-1] + " and {} Pubes\n".format(model.get("pubic_hair"))
    if model.get("vibratoy"):
        subject += "- Lovense Toy\n\n"
    if model.get("turns_on"):
        subject += "- Likes: {}\n".format(model.get("turns_on"))
    if model.get("turns_off"):
        subject += "- Dislikes: {}\n\n".format(model.get("turns_off"))
    if model.get("tags"):
        subject += ", ".join(model.get("tags"))
    return subject


def _cloudbate_context(username, name):
    contextrecord = (
        utils.addon_sys
        + "?mode=chaturbate.Record&id="
        + urllib_parse.quote_plus(username or "")
    )
    return [
        (
            "[COLOR violet]Find recordings featuring [/COLOR]{}[COLOR violet] on Cloudbate[/COLOR]".format(
                name
            ),
            "RunPlugin(" + contextrecord + ")",
        )
    ]


@site.register()
def List(url):
    if utils.addon.getSetting("chaturbate") == "true":
        clean_database(False)

    data, _ = utils.get_html_with_cloudflare_retry(url)
    model_list = _loads_json(data)
    if not isinstance(model_list, list):
        utils.notify(site.name, "No models available")
        utils.eod()
        return
    for model in model_list:
        profile_imgs = model.get("profile_images", {})
        img = profile_imgs.get("thumbnail_image_big_live") or profile_imgs.get("thumbnail_image_medium_live") or profile_imgs.get("thumbnail_image_small_live")
        if img and not img.startswith("http"):
            img = "https:" + img
        username = model.get("username")
        name = model.get("display_name", username)
        age = model.get("display_age", "??")
        name += " [COLOR hotpink][{}][/COLOR]".format(age)
        if model.get("hd_cam"):
            name += " [COLOR gold]HD[/COLOR]"
        subject = _model_subject(model)
        site.add_download_link(
            name,
            username,
            "Playvid",
            img,
            subject.encode("utf-8") if utils.PY2 else subject,
            contextm=_cloudbate_context(username, name),
            noDownload=True,
        )
    utils.eod()


@site.register(clean_mode=True)
def clean_database(showdialog=True):
    conn = sqlite3.connect(utils.TRANSLATEPATH("special://database/Textures13.db"))
    try:
        with conn:
            list = conn.execute(
                "SELECT id, cachedurl FROM texture WHERE url LIKE ?;",
                ("%" + "bongacams.com" + "%",),
            )
            for row in list:
                conn.execute("DELETE FROM sizes WHERE idtexture = ?;", (row[0],))
                try:
                    os.remove(utils.TRANSLATEPATH("special://thumbnails/" + row[1]))
                except Exception as e:
                    utils.kodilog(
                        "@@@@Cumination: Silent failure in bongacams: " + str(e)
                    )
            conn.execute(
                "DELETE FROM texture WHERE url LIKE ?;", ("%" + "bongacams.com" + "%",)
            )
            if showdialog:
                utils.notify("Finished", "bongacams.com images cleared")
    except Exception as e:
        utils.kodilog("@@@@Cumination: Silent failure in bongacams: " + str(e))


@site.register()
def Playvid(url, name):
    if url is None or url == "":
        utils.notify(name, "Model Offline", icon="thumb")
        return

    vp = utils.VideoPlayer(name)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    try:
        postRequest = [
            ("method", "getRoomData"),
            ("args[]", str(url)),
            ("args[]", ""),
            ("args[]", ""),
        ]
        hdr = utils.base_hdrs
        hdr.update({"X-Requested-With": "XMLHttpRequest"})
        response = utils._postHtml(
            "{0}tools/amf.php".format(site.url),
            form_data=postRequest,
            headers=hdr,
            compression=False,
        )
    except Exception as e:
        utils.kodilog("@@@@Cumination: failure in bongacams: " + str(e))
        utils.notify("Oh oh", "Couldn't find a playable webcam link", icon="thumb")
        return None

    amf_json = json.loads(response)
    if amf_json["status"] == "error":
        utils.notify("Oh oh", "Couldn't find a playable webcam link", icon="thumb")
        return

    if "private" in amf_json.get("performerData", {}).get("showType"):
        utils.notify(name, "Model in private chat", icon="thumb")
        vp.progress.close()
        return

    amf = amf_json.get("localData", {}).get("videoServerUrl")

    if amf is None:
        utils.notify(name, "Model Offline", icon="thumb")
        vp.progress.close()
        return
    elif amf.startswith("//mobile"):
        stream_user = amf_json.get("performerData", {}).get("username") or url
        videourl = "https:" + amf + "/hls/stream_" + stream_user + ".m3u8"
    else:
        stream_user = amf_json.get("performerData", {}).get("username") or url
        videourl = "https:" + amf + "/hls/stream_" + stream_user + "/playlist.m3u8"
        try:
            m3u8 = utils._getHtml(videourl, referer=site.url)
        except Exception:
            utils.notify(name, "Model Offline or GeoLocked", icon="thumb")
            vp.progress.close()
            return
        quals = re.findall(r"\d+x(\d+).+\n(.+)", m3u8)
        if quals:
            sources = {
                qual: urllib_parse.urljoin(videourl, vurl) for qual, vurl in quals
            }
            videourl = utils.selector(
                "Select quality",
                sources,
                setting_valid="qualityask",
                sort_by=lambda x: int(x.split("x")[-1]),
                reverse=True,
            )

    videourl += "|User-Agent={0}&Referer={1}&Origin={2}".format(
        utils.USER_AGENT, site.url, site.url[:-1]
    )
    vp.progress.update(75, "[CR]Found Stream[CR]")
    vp.play_from_direct_link(videourl)


@site.register()
def List2(url):
    headers = {"X-Requested-With": "XMLHttpRequest"}
    data, _ = utils.get_html_with_cloudflare_retry(url, site.url, headers=headers)
    payload = _loads_json(data) or {}
    time_period = (
        payload.get("data", {})
        .get("topRooms", {})
        .get("content", {})
        .get("winners", {})
        .get("timePeriod")
    )
    refresh_label = "[COLOR red][B]Refresh[/B][/COLOR]"
    if time_period:
        refresh_label = "Current contest standings: {} - {}".format(
            time_period, refresh_label
        )
    site.add_download_link(
        refresh_label,
        url,
        "utils.refresh",
        "",
        "",
        noDownload=True,
    )
    if utils.addon.getSetting("online_only") == "true":
        online_only = True
        url = url + "?isOnlineOnly=on"
        site.add_download_link(
            "[COLOR red][B]Show all models[/B][/COLOR]",
            url,
            "online",
            "",
            "",
            noDownload=True,
        )
    else:
        online_only = False
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
    items = (
        payload.get("data", {})
        .get("topRooms", {})
        .get("content", {})
        .get("winners", {})
        .get("thumbs", [])
    )
    if not items:
        items = payload.get("result", {}).get("chatActivities", [])
    for item in items:
        if "user" in item:
            username = item.get("user", {}).get("username")
            name = item.get("user", {}).get("displayName")
            img = "https:" + item.get("user", {}).get("profileImageUrls", {}).get("thumb_xbig_lq", "")
            status = "Online" if item.get("user", {}).get("isOnline") else "Offline"
            place = item.get("chatActivity", {}).get("place")
            viewers = item.get("chatActivity", {}).get("viewers")
            prize = item.get("chatActivity", {}).get("prizeFormatted")
        else:
            status = "Online" if item.get("liveBadge") is not None else "Offline"
            if online_only and status == "Offline":
                continue
            name = item.get("footer", {}).get("displayName", "")
            link_path = item.get("link", {}).get("url", {}).get("url", "")
            username = link_path.strip("/") if status == "Online" and link_path else " "
            img_src = item.get("avatar", {}).get("src", "")
            img = "https:" + img_src if img_src.startswith("//") else "https://" + img_src if img_src else ""
            place = item.get("stripe", {}).get("place", "")
            viewers = ""
            prize = ""
            for content in item.get("content", []):
                text = content.get("text", "")
                if "members" in text.lower():
                    viewers = "".join(filter(str.isdigit, text))
                elif "prize" in text.lower():
                    prize = text
        name = name.encode("utf8") if utils.PY2 else name
        if status == "Offline":
            username = " "
        subject = "Status: {0}[CR]".format(status)
        subject += "Place: {0}[CR]".format(place)
        subject += "Viewers: {0}[CR]".format(viewers)
        subject += "Prize: {0}[CR]".format(prize)
        site.add_download_link(name, username, "Playvid", img, subject, noDownload=True)
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
        url = url + "?online_only=1"
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
    data, _ = utils.get_html_with_cloudflare_retry(url, site.url, headers=headers)
    payload = _loads_json(data) or {}
    json_data = payload.get("data", {})
    items = (
        json_data.get("topModels", {})
        .get("content", {})
        .get("topWinners", {})
        .get("thumbs", [])
    )
    items += (
        json_data.get("topModels", {})
        .get("content", {})
        .get("winners", {})
        .get("thumbs", [])
    )
    if not items:
        items = payload.get("result", {}).get("contestItems", [])
    for item in items:
        if "user" in item:
            username = item.get("user", {}).get("username")
            name = item.get("user", {}).get("displayName")
            img = "https:" + item.get("user", {}).get("profileImageUrls", {}).get("thumb_xbig_lq", "")
            status = "Online" if item.get("user", {}).get("isOnline") else "Offline"
            place = item.get("contestItem", {}).get("place")
            metric_label = "Points"
            metric_value = item.get("contestItem", {}).get("points")
            prize = item.get("contestItem", {}).get("prizeFormatted")
        else:
            status = "Online" if item.get("liveBadge") is not None else "Offline"
            name = item.get("footer", {}).get("displayName", "")
            link_path = item.get("link", {}).get("url", {}).get("url", "")
            username = link_path.strip("/") if status == "Online" and link_path else " "
            img_src = item.get("avatar", {}).get("src", "")
            img = "https:" + img_src if img_src.startswith("//") else "https://" + img_src if img_src else ""
            place = item.get("stripe", {}).get("place", "")
            metric_label = "Viewers"
            metric_value = ""
            prize = ""
            for content in item.get("content", []):
                text = content.get("text", "")
                if "members" in text.lower():
                    metric_value = "".join(filter(str.isdigit, text))
                elif "prize" in text.lower():
                    prize = text
        name = name.encode("utf8") if utils.PY2 else name
        if status == "Offline":
            username = " "
        subject = "Status: {0}[CR]".format(status)
        subject += "Place: {0}[CR]".format(place)
        subject += "{0}: {1}[CR]".format(metric_label, metric_value)
        subject += "Prize: {0}[CR]".format(prize)
        site.add_download_link(name, username, "Playvid", img, subject, noDownload=True)
    utils.eod()


@site.register()
def online(url):
    if utils.addon.getSetting("online_only") == "true":
        utils.addon.setSetting("online_only", "false")
    else:
        utils.addon.setSetting("online_only", "true")
    utils.refresh()


@site.register()
def onlineFav(url):
    data, _ = utils.get_html_with_cloudflare_retry(url)
    model_list = _loads_json(data)
    if not isinstance(model_list, list):
        utils.notify(site.name, "No favorite models available")
        utils.eod()
        return

    conn = sqlite3.connect(utils.favoritesdb)
    conn.text_factory = str
    c = conn.cursor()
    c.execute(
        "SELECT DISTINCT name, url, image FROM favorites WHERE mode='bongacams.Playvid'"
    )
    favorite_data = {}
    for fav_name, fav_url, fav_image in c.fetchall():
        favorite_data[fav_name.split("[COLOR")[0].strip()] = {
            "db_url": fav_url,
            "db_image": fav_image,
        }
    c.close()
    conn.close()

    for model in model_list:
        display_name = model.get("display_name")
        if display_name not in favorite_data:
            continue
        info = model.copy()
        info.update(favorite_data[display_name])
        username = info.get("username")
        name = display_name
        age = info.get("display_age", "??")
        name += " [COLOR hotpink][{}][/COLOR]".format(age)
        if info.get("hd_cam"):
            name += " [COLOR gold]HD[/COLOR]"
        img = info.get("db_image")
        subject = _model_subject(info)
        site.add_download_link(
            name,
            username,
            "Playvid",
            img,
            subject.encode("utf-8") if utils.PY2 else subject,
            contextm=_cloudbate_context(username, name),
            noDownload=True,
        )
    utils.eod()
