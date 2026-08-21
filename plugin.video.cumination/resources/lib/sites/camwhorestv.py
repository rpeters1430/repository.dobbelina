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

import json
import re

import xbmc
import xbmcgui
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "camwhorestv",
    "[COLOR hotpink]CamWhores.tv[/COLOR]",
    "https://www.camwhores.tw/",
    "camwhorestv.png",
    "camwhorestv",
    category="Amateur & Social",
)

cwtvhdr = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

camwhores_logged = utils.addon.getSetting("camwhores_logged").lower() == "true"


@site.register(default_mode=True)
def Main():
    global camwhores_logged
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Models[/COLOR]",
        site.url + "models/",
        "Models",
        utils.cum_image("cum-models.png"),
    )
    if camwhores_logged:
        site.add_dir(
            "[COLOR fuchsia]Logout[/COLOR]",
            "",
            "logout_camwhores",
            utils.cum_image("cum-logout.png"),
            Folder=False,
        )
    else:
        site.add_dir(
            "[COLOR red]Login[/COLOR]",
            "",
            "login_camwhores",
            utils.cum_image("cum-login.png"),
            Folder=False,
        )

    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url + "latest-updates/1/")


@site.register()
def List(url):
    if isinstance(url, list):
        url = "".join(url)
    listhtml = utils.getHtml(url, site.url)
    if isinstance(listhtml, list):
        listhtml = "".join(listhtml)
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    
    for block in soup.select('div[class*="item"]'):
        anchor = block.select_one('a')
        if not anchor:
            continue
            
        videopage = anchor.get('href')
        if not videopage:
            continue
            
        name = anchor.get('title')
        if not name:
            img_tag = anchor.select_one('img')
            name = img_tag.get('alt') if img_tag else ""
        if not name:
            continue
            
        img_tag = anchor.select_one('img')
        img = img_tag.get('data-original') if img_tag else ""
        if not img and img_tag:
            img = img_tag.get('src') or ""
            
        duration_tag = anchor.select_one('.duration')
        duration = duration_tag.get_text().strip() if duration_tag else ""
        
        views_tag = block.select_one('.views')
        views = views_tag.get_text().strip() if views_tag else ""
        
        is_private = anchor.select_one('.ico-private') is not None or block.select_one('.ico-private') is not None
        
        title = utils.cleantext(name)
        label = "[COLOR blue][PV] [/COLOR]" if is_private else ""
        label += f"{title} [COLOR yellow][{views}][/COLOR]"
        
        if img:
            parts = img.rstrip("/").split("/")
            img_preview = "/".join(parts[:-2]) + "/preview.jpg"
        else:
            img_preview = site.image
            
        site.add_download_link(
            label, videopage, "Playvid", img_preview, label, duration=duration
        )

    if "/search/" in url or "/categories/" in url or "/models/" in url:
        _add_async_next_page(url, listhtml)
    else:
        re_npurl = r'class="next"><a href="([^"]+)"'
        re_npnr = r'class="next"><a href="[^"]*/(\d+)/"'
        re_lpnr = r'class="last"><a href="[^"]*/(\d+)/"'
        utils.next_page(site, "camwhorestv.List", listhtml, re_npurl, re_npnr, re_lpnr=re_lpnr)

    utils.eod()


def _add_async_next_page(url, listhtml):
    """Follow the site's AJAX-driven pagination on categories/models/search pages."""
    if isinstance(listhtml, list):
        listhtml = "".join(listhtml)
    npnr_match = re.search(
        r'<li class="next">.*?[from_albums|from]:(\d+)">Next', listhtml, re.DOTALL
    )
    lpnr_match = re.search(
        r'<li class="last">.*?[from_albums|from]:(\d+)">Last', listhtml, re.DOTALL
    )
    np_match = re.compile(
        r'>\.\.\.<.*?data-parameters="([^"]+):([^:]+)">.*?[from_albums|from]:(\d+)">.*Next',
        re.DOTALL | re.IGNORECASE,
    ).search(listhtml)

    if not (npnr_match and lpnr_match and np_match):
        return

    re_npnr = npnr_match.group(1)
    re_lpnr = lpnr_match.group(1)

    npurl = np_match.group(1).replace(":", "=").replace(";", "&").replace(
        "+", f"={re_npnr}&"
    )
    if "/search/" in url:
        block = "&block_id=list_videos_videos_list_search_result&"
    else:
        block = "&block_id=list_videos_common_videos_list&"

    base = url.split("?")[0] if "?" in url else url
    npurl = base + "?mode=async&function=get_block" + block + npurl + "=" + re_npnr

    site.add_dir(
        f"Next Page... ({re_npnr}/{re_lpnr})", npurl, "List", site.img_next
    )


@site.register()
def Search(url, keyword=None):
    if isinstance(url, list):
        url = "".join(url)
    if isinstance(keyword, list):
        keyword = "".join(keyword)
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url += urllib_parse.quote(keyword.strip().replace(" ", "-"), safe="-") + "/"
        List(url)


@site.register()
def Playvid(url, name, download=None):
    if isinstance(url, list):
        url = "".join(url)
    if isinstance(name, list):
        name = "".join(name)
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, headers=cwtvhdr)
    if isinstance(html, list):
        html = "".join(html)
    if 'class="message"' in html:
        message = re.search(r'span class="message">\s(.+) Only', html)
        if message:
            utils.notify("", message.group(1).lstrip(" \t"))
        return
    vp.play_from_kt_player(html, user_agent=cwtvhdr["User-Agent"])


@site.register()
def Categories(url):
    if isinstance(url, list):
        url = "".join(url)
    listhtml = utils.getHtml(url, site.url)
    if isinstance(listhtml, list):
        listhtml = "".join(listhtml)
        
    soup = utils.parse_html(listhtml)
    
    for anchor in soup.select('a.item'):
        cat_url = anchor.get('href')
        cat_title = anchor.get('title')
        
        img_tag = anchor.select_one('img')
        cat_img = img_tag.get('src') if img_tag else ""
        
        count_tag = anchor.select_one('.videos')
        cat_count = count_tag.get_text().strip() if count_tag else ""
        
        if not (cat_url and cat_title):
            continue
            
        site.add_dir(
            f"[COLOR hotpink]{cat_title} [/COLOR][COLOR yellow][{cat_count}][/COLOR]",
            cat_url,
            "List",
            cat_img,
        )
    utils.eod()


@site.register()
def Models(url):
    if isinstance(url, list):
        url = "".join(url)
    listhtml = utils.getHtml(url, site.url)
    if isinstance(listhtml, list):
        listhtml = "".join(listhtml)
        
    soup = utils.parse_html(listhtml)
    
    for anchor in soup.select('a[class*="item"]'):
        cat_url = anchor.get('href')
        cat_title = anchor.get('title')
        
        img_tag = anchor.select_one('img')
        cat_img = img_tag.get('src') if img_tag else ""
        
        count_tag = anchor.select_one('.videos')
        cat_count = count_tag.get_text().strip() if count_tag else ""
        
        if not (cat_url and cat_title):
            continue
            
        site.add_dir(
            f"{cat_title} [COLOR yellow][{cat_count}][/COLOR]",
            cat_url,
            "List",
            cat_img,
        )
        
    re_npurl = r'class="next"><a href="([^"]+)"'
    re_npnr = r'class="next"><a href="[^"]*/(\d+)/"'
    re_lpnr = r'class="last"><a href="[^"]*/(\d+)/"'
    utils.next_page(
        site,
        "camwhorestv.Models",
        listhtml,
        re_npurl,
        re_npnr,
        re_lpnr=re_lpnr,
        contextm="camwhorestv.GotoPage",
    )
    utils.eod()


@site.register()
def GotoPage(url, np, lp=None, list_mode="List"):
    if isinstance(url, list):
        url = "".join(url)
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        if lp and str(lp).isdigit() and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        url = re.sub(r"&from([^=]*)=\d+", rf"&from\1={pg}", url, flags=re.IGNORECASE)
        contexturl = (
            utils.addon_sys
            + "?mode=camwhorestv."
            + list_mode
            + "&url="
            + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


def get_camwhores_session():
    domain = ".camwhores.tv"
    for cookie in utils.cj:
        if cookie.domain == domain and cookie.name == "PHPSESSID":
            return cookie.value
    return ""


@site.register()
def login_camwhores():
    global camwhores_logged

    sessionid = utils.addon.getSetting("camwhores_sessionid")
    if sessionid:
        current = get_camwhores_session()
        if sessionid == current:
            utils.addon.setSetting("camwhores_logged", "true")
            camwhores_logged = True
            return True

        cookie_structure = {
            "solution": {
                "cookies": [
                    {
                        "name": "PHPSESSID",
                        "domain": ".www.camwhores.tv",
                        "value": sessionid,
                        "path": "/",
                        "secure": True,
                        "expiry": None,
                        "httpOnly": True,
                    }
                ],
                "userAgent": utils.USER_AGENT,
            }
        }
        utils.savecookies(cookie_structure)
        utils.addon.setSetting("camwhores_logged", "true")
        camwhores_logged = True
        utils.refresh()
        return True

    cw_user = utils.addon.getSetting("camwhores_user") or ""
    cw_pass = utils.addon.getSetting("camwhores_pass") or ""

    if not cw_user:
        cw_user = utils._get_keyboard(default=cw_user, heading="Input your CamWhores username")
        if not cw_user:
            return False

        cw_pass = utils._get_keyboard(
            default=cw_pass, heading="Input your CamWhores password", hidden=True
        )
        if not cw_pass:
            return False

    login_url = site.url + "login/"

    payload_dict = {
        "username": cw_user,
        "pass": cw_pass,
        "remember_me": "1",
        "action": "login",
        "email_link": site.url + "email/",
        "format": "json",
        "mode": "async",
    }

    headers = {
        "Accept": "*/*",
        "Origin": site.url.rstrip("/"),
        "Referer": site.url,
        "User-Agent": utils.USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        response_html = utils._postHtml(login_url, form_data=payload_dict, headers=headers)
        response_json = json.loads(response_html)
        status = response_json.get("status", "")
        if status != "success":
            utils.notify("CamWhores", "Login failed")
            utils.addon.setSetting("camwhores_logged", "false")
            camwhores_logged = False
            return False

        display_name = response_json.get("username") or cw_user
        utils.addon.setSetting("camwhores_display_name", display_name)

        new_session_id = get_camwhores_session()
        if new_session_id:
            utils.notify("CamWhores", f"Login successful for {display_name}")
            utils.addon.setSetting("camwhores_sessionid", new_session_id)
            utils.addon.setSetting("camwhores_logged", "true")
            utils.addon.setSetting("camwhores_user", cw_user)
            utils.addon.setSetting("camwhores_pass", cw_pass)

            camwhores_logged = True

            cookie_structure = {
                "solution": {
                    "cookies": [
                        {
                            "name": "PHPSESSID",
                            "domain": ".www.camwhores.tv",
                            "value": new_session_id,
                            "path": "/",
                            "secure": True,
                            "expiry": None,
                            "httpOnly": True,
                        }
                    ],
                    "userAgent": utils.USER_AGENT,
                }
            }
            utils.savecookies(cookie_structure)
            utils.refresh()
            return True

    except Exception as e:
        utils.kodilog(f"Error on utils._postHtml for Login CamWhores: {e}")
        utils.notify("CamWhores", "Authentication error")

    utils.addon.setSetting("camwhores_logged", "false")
    camwhores_logged = False
    return False


@site.register()
def logout_camwhores():
    logout_url = site.url + "logout/"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": site.url,
        "User-Agent": utils.USER_AGENT,
    }

    try:
        utils._getHtml(logout_url, headers=headers)

        utils.notify("CamWhores", "Session ended successfully.")

        clear = utils.selector("Clear stored user & password?", ["Yes", "No"], reverse=True)
        if clear == "Yes":
            utils.addon.setSetting("camwhores_user", "")
            utils.addon.setSetting("camwhores_pass", "")

        utils.addon.setSetting("camwhores_sessionid", "")
        utils.addon.setSetting("camwhores_logged", "false")

        global camwhores_logged
        camwhores_logged = False

        utils.refresh()
        return True

    except Exception as e:
        utils.kodilog(f"Error on utils._getHtml for Logout CamWhores: {e}")
        return False
