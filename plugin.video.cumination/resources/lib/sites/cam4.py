"""
Cumination
Copyright (C) 2016 Whitecream

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
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "cam4",
    "[COLOR hotpink]Cam4[/COLOR]",
    "https://www.cam4.com/",
    "cam4.png",
    "cam4",
    True,
    category="Cams & Live",
)
IOS_UA = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML%2C like Gecko) Mobile/15E148"
}

cam4logged = utils.addon.getSetting('cam4logged').lower() == 'true'


def _load_json_payload(raw_payload):
    if not raw_payload:
        return {}
    if isinstance(raw_payload, bytes):
        raw_payload = raw_payload.decode("utf-8", "ignore")
    if not isinstance(raw_payload, str):
        return {}
    try:
        payload = json.loads(raw_payload)
    except (TypeError, ValueError) as exc:
        utils.kodilog("cam4: invalid JSON payload - {}".format(exc))
        return {}
    return payload if isinstance(payload, dict) else {}


@site.register(default_mode=True)
def Main():
    global cam4logged
    player = utils.addon.getSetting('cam4player')
    if not player:
        utils.addon.setSetting('cam4player', 'Playvid_Adaptive')
        player = 'Playvid_Adaptive'
    pretty_name = {
        'Playvid_Adaptive': 'Adaptive',
        'Playvid_proxy': 'Proxy',
        'Playvid_classic': 'Classic'
    }.get(player)
    site.add_download_link(
        'Current player: [COLOR fuchsia][B]{0}[/B][/COLOR] - [COLOR red][B]Change[/B][/COLOR]'.format(pretty_name),
        site.url,
        'Playvid_change',
        '',
        '',
        noDownload=True
    )
    female = utils.addon.getSetting("chatfemale") == "true"
    male = utils.addon.getSetting("chatmale") == "true"
    couple = utils.addon.getSetting("chatcouple") == "true"
    trans = utils.addon.getSetting("chattrans") == "true"
    site.add_dir(
        "[COLOR red]Refresh Cam4 images[/COLOR]", "", "clean_database", "", Folder=False
    )
    site.add_dir(
        "[COLOR yellow]Online Favorites[/COLOR]",
        "",
        "onlineFav",
        "",
        "",
    )
    if female:
        site.add_dir(
            "[COLOR hotpink]Females[/COLOR]",
            "&gender=female&broadcastType=female_group&broadcastType=solo&broadcastType=male_female_group",
            "List",
            "",
            1,
        )
    if couple:
        site.add_dir(
            "[COLOR hotpink]Couples[/COLOR]",
            "&broadcastType=male_group&broadcastType=female_group&broadcastType=male_female_group",
            "List",
            "",
            1,
        )
    if male:
        site.add_dir(
            "[COLOR hotpink]Males[/COLOR]",
            "&gender=male&broadcastType=male_group&broadcastType=solo&broadcastType=male_female_group",
            "List",
            "",
            1,
        )
    if trans:
        site.add_dir(
            "[COLOR hotpink]Transsexual[/COLOR]", "&gender=shemale", "List", "", 1
        )
    utils.eod()


@site.register(clean_mode=True)
def clean_database(showdialog=True):
    conn = sqlite3.connect(utils.TRANSLATEPATH("special://database/Textures13.db"))
    try:
        with conn:
            list = conn.execute(
                "SELECT id, cachedurl FROM texture WHERE url LIKE ?;",
                ("%" + ".cam4s.com" + "%",),
            )
            for row in list:
                conn.execute("DELETE FROM sizes WHERE idtexture = ?;", (row[0],))
                try:
                    os.remove(utils.TRANSLATEPATH("special://thumbnails/" + row[1]))
                except Exception as e:
                    utils.kodilog("@@@@Cumination: Silent failure in cam4: " + str(e))
            conn.execute(
                "DELETE FROM texture WHERE url LIKE ?;", ("%" + ".cam4.com" + "%",)
            )
            if showdialog:
                utils.notify("Finished", "Cam4 images cleared")
    except Exception as e:
        utils.kodilog("@@@@Cumination: Silent failure in cam4: " + str(e))


@site.register()
def Playvid_change(url, name):
    import xbmc
    current = utils.addon.getSetting('cam4player')
    if current == 'Playvid_Adaptive':
        utils.addon.setSetting('cam4player', 'Playvid_proxy')
        utils.notify('Player switched', 'Now using Proxy mode')
    elif current == 'Playvid_proxy':
        utils.addon.setSetting('cam4player', 'Playvid_classic')
        utils.notify('Player switched', 'Now using Classic mode')
    elif current == 'Playvid_classic':
        utils.addon.setSetting('cam4player', 'Playvid_Adaptive')
        utils.notify('Player switched', 'Now using Adaptive mode')
    xbmc.executebuiltin('Container.Refresh')


@site.register()
def List(url, page=1):
    if utils.addon.getSetting("chaturbate") == "true":
        clean_database(False)

    conn = sqlite3.connect(utils.favoritesdb)
    conn.text_factory = str
    c = conn.cursor()
    c.execute("SELECT url FROM favorites WHERE mode='cam4.Playvid'")
    favorite = [row[0] for row in c.fetchall()]
    c.close()

    perPage_setting = utils.addon.getSetting('cam4per_page')
    perPage = int(perPage_setting) if perPage_setting and perPage_setting.strip().isdigit() else 60
    if not perPage_setting:
        utils.addon.setSetting("cam4per_page", str(perPage))

    listurl = "{0}/api/directoryCams?directoryJson=true&online=true&url=true&orderBy=VIDEO_QUALITY{1}&page={2}&resultsPerPage={3}".format(
        site.url, url, page, perPage
    )
    listhtml = utils._getHtml(listurl, headers=IOS_UA)
    cams = _load_json_payload(listhtml).get("users", {})
    for cam in cams:
        username = cam.get("username")
        if any(username in u for u in favorite):
            prefix = '[COLOR yellow]★ [/COLOR]'
            fav = 'del'
        else:
            prefix = ''
            fav = 'add'
        name = prefix + username
        age = cam.get("age")
        if age:
            name = "{0} [COLOR deeppink][{1}][/COLOR]".format(name, age)
        hd = ""
        if cam.get("hdStream"):
            hd = "HD"
        img = cam.get("snapshotImageLink")
        if not img:
            img = cam.get("defaultImageLink")

        subject = ""
        if cam.get("viewers"):
            subject += "[COLOR deeppink]Viewers:[/COLOR] {}[CR]".format(cam.get("viewers"))
        if cam.get("countryCode"):
            subject += "[CR][COLOR deeppink]Country:[/COLOR] {}[CR]".format(utils.get_country(cam.get("countryCode")))
            name = "{0} [COLOR blue][{1}][/COLOR]".format(name, utils.get_country(cam.get("countryCode")))
        if cam.get("languages"):
            langs = [utils.get_language(lang) for lang in cam.get("languages")]
            subject += "[COLOR deeppink]Languages:[/COLOR] {}[CR]".format(", ".join(langs))
        if cam.get("resolution"):
            subject += "[COLOR deeppink]Resolution:[/COLOR] {}[CR]".format(cam.get("resolution"))
        if cam.get("sexPreference"):
            subject += "[CR][COLOR deeppink]Sexual Preference:[/COLOR] {}[CR]".format(cam.get("sexPreference"))
        if cam.get("statusMessage"):
            subject += "[CR]{}[CR][CR]".format(
                cam.get("statusMessage").encode("utf8") if utils.PY2 else cam.get("statusMessage")
            )
        if cam.get("showTags"):
            subject += (
                ", ".join(cam.get("showTags")).encode("utf8")
                if utils.PY2
                else ", ".join(cam.get("showTags"))
            )

        contextrecord = (utils.addon_sys + "?mode=chaturbate.Record&id=" + urllib_parse.quote_plus(username))
        context = [('[COLOR violet]Find recordings featuring [/COLOR]{0}[COLOR violet] on Cloudbate[/COLOR]'.format(username), 'RunPlugin(' + contextrecord + ')')]

        video = "{}rest/v1.0/profile/{}/streamInfo".format(site.url, username)
        site.add_download_link(
            name, video, "Playvid", img, subject, noDownload=True, quality=hd, contextm=context, fav=fav
        )

    if len(cams) == perPage:
        page += 1
        site.add_dir("Next Page ({})".format(page), url, "List", site.img_next, page)
    utils.eod()


@site.register()
def Playvid(url, name):
    player = utils.addon.getSetting('cam4player')
    if player == 'Playvid_proxy':
        return Playvid_proxy(url, name)
    elif player == 'Playvid_classic':
        return Playvid_classic(url, name)
    return Playvid_Adaptive(url, name)


def Playvid_Adaptive(url, name):
    import urllib.parse
    import xbmcgui
    import xbmc

    html = utils._getHtml(url)
    try:
        cdn_list = json.loads(html).get('cdnURL')
    except:
        utils.notify('Cam4', 'Cannot fetch CDN URL')
        return

    if not cdn_list:
        utils.notify('Cam4', 'The model is not broadcasting at this moment.')
        return

    if isinstance(cdn_list, list):
        cdn_urls = cdn_list
    else:
        cdn_urls = [cdn_list]

    headers = {
        'User-Agent': utils.USER_AGENT,
        'Referer': site.url,
        'Origin': site.url
    }

    final_url = None
    for cdn in cdn_urls:
        test_url = cdn + '|' + urllib.parse.urlencode(headers)
        if utils._getHtml(cdn, error='return'):
            final_url = test_url
            break

    if not final_url:
        utils.notify('Cam4', 'All CDNs failed')
        return

    li = xbmcgui.ListItem(name, path=final_url)
    li.setProperty('inputstream', 'inputstream.adaptive')
    li.setProperty('inputstream.adaptive.manifest_type', 'hls')
    manifest_headers = "User-Agent={0}&Referer={1}&Origin={2}".format(
        headers['User-Agent'], headers['Referer'], headers['Origin']
    )
    li.setProperty('inputstream.adaptive.manifest_headers', manifest_headers)
    li.setProperty('inputstream.adaptive.stream_headers', manifest_headers)
    li.setProperty('http-user-agent', headers['User-Agent'])
    li.setProperty('http-referrer', headers['Referer'])
    xbmc.Player().play(final_url, li)


def Playvid_proxy(url, name):
    Playvid_Adaptive(url, name)


def Playvid_classic(url, name):
    vp = utils.VideoPlayer(name)
    html = utils._getHtml(url)
    cdn = _load_json_payload(html).get("cdnURL")
    if isinstance(cdn, list):
        cdn = cdn[0] if cdn else None
    if not cdn:
        utils.notify("Cam4", "No Video found")
        return
    vp.play_from_direct_link(cdn)


@site.register()
def onlineFav(url):
    listurl = '{0}/api/directoryCams?directoryJson=true&online=true&url=true&orderBy=VIDEO_QUALITY'.format(site.url)
    data = utils._getHtml(listurl)
    model_list = json.loads(data).get('users', {})

    conn = sqlite3.connect(utils.favoritesdb)
    conn.text_factory = str
    c = conn.cursor()
    c.execute("SELECT DISTINCT name, url, image FROM favorites WHERE mode='cam4.Playvid'")
    favorite_data = {
        row[0].split('[COLOR')[0].strip(): {'db_url': row[1], 'db_image': row[2]}
        for row in c.fetchall()
    }
    c.close()

    model_lookup = {
        item['username']: dict(item, **favorite_data[item['username']])
        for item in model_list
        if item['username'] in favorite_data
    }

    for model_name, info in model_lookup.items():
        username = info['username']
        name = username
        age = info.get('age')
        if age:
            name = '{0} [COLOR deeppink][{1}][/COLOR]'.format(name, age)
        hd = 'HD' if info.get('hdStream') else ''
        img = info.get('snapshotImageLink') or info.get('defaultImageLink')

        subject = ''
        if info.get('viewers'):
            subject += '[COLOR deeppink]Viewers:[/COLOR] {}[CR]'.format(info['viewers'])
        if info.get('countryCode'):
            subject += '[CR][COLOR deeppink]Country:[/COLOR] {}[CR]'.format(utils.get_country(info['countryCode']))
            name = '{0} [COLOR blue][{1}][/COLOR]'.format(name, utils.get_country(info['countryCode']))
        if info.get('languages'):
            langs = [utils.get_language(lang) for lang in info['languages']]
            subject += '[COLOR deeppink]Languages:[/COLOR] {}[CR]'.format(', '.join(langs))
        if info.get('resolution'):
            subject += '[COLOR deeppink]Resolution:[/COLOR] {}[CR]'.format(info['resolution'])
        if info.get('sexPreference'):
            subject += '[CR][COLOR deeppink]Sexual Preference:[/COLOR] {}[CR]'.format(info['sexPreference'])
        if info.get('statusMessage'):
            subject += '[CR]{}[CR][CR]'.format(
                info['statusMessage'].encode('utf8') if utils.PY2 else info['statusMessage']
            )
        if info.get('showTags'):
            subject += ', '.join(info['showTags']).encode('utf8') if utils.PY2 else ', '.join(info['showTags'])

        video = '{}rest/v1.0/profile/{}/streamInfo'.format(site.url, username)
        contextrecord = (utils.addon_sys + "?mode=chaturbate.Record&id=" + urllib_parse.quote_plus(username))
        contextmenu = [('[COLOR violet]Find recordings featuring [/COLOR]{0}[COLOR violet] on Cloudbate[/COLOR]'.format(username), 'RunPlugin(' + contextrecord + ')')]
        site.add_download_link(name, video, 'Playvid', img, subject.encode('utf-8') if utils.PY2 else subject, contextm=contextmenu, noDownload=True, quality=hd, fav='del')

    utils.eod()
