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
import requests
import xbmc
import xbmcgui
from six.moves import urllib_error, urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
site = AdultSite(
    "watchpornx",
    "[COLOR hotpink]Watchpornx[/COLOR]",
    "https://watchpornx.com/",
    "https://i2.wp.com/watchpornx.com/wp-content/uploads/2026/10/watchpornx-logo.png",
    "watchpornx",
    category="Video Tubes",
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]X Movies[/COLOR]", site.url + "adult/x-movies", "List", site.img_movies)
    site.add_dir("[COLOR hotpink]X Popular[/COLOR]", site.url + "adult/x-popular", "List", site.img_movies)
    site.add_dir("[COLOR hotpink]X Top Rated[/COLOR]", site.url + "adult/x-top-rated", "List", site.img_movies)
    site.add_dir("[COLOR hotpink]Pornstars[/COLOR]", site.url + "adult/pornstars", "Studios", site.img_star)
    site.add_dir("[COLOR hotpink]Studios[/COLOR]", site.url + "adult/studios", "Studios", site.img_cat)
    site.add_dir("[COLOR hotpink]Genres[/COLOR]", site.url + "adult/porn-genres", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Year[/COLOR]", site.url + "adult/porn-years", "Studios", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search)
    List(site.url + "adult")
    utils.eod()


@site.register()
def List(url):
    try:
        listhtml = utils.getHtml(url)
    except urllib_error.URLError as e:
        utils.notify(str(e))
        return
    if not listhtml or 'class="error404' in listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    cards = soup.select("article.card")
    for card in cards:
        link = card.select_one("a[href]")
        if not link:
            continue
        videopage = utils.safe_get_attr(link, "href")
        img_el = card.select_one("img")
        img = utils.safe_get_attr(img_el, "data-lazy-src") or utils.safe_get_attr(img_el, "src")
        alt = utils.safe_get_attr(img_el, "alt") or utils.safe_get_text(link)
        if alt.lower().startswith("watch "):
            alt = alt[6:]
        q_el = card.select_one(".card__q")
        q = utils.safe_get_text(q_el)
        dur_el = card.select_one(".card__dur")
        duration = utils.safe_get_text(dur_el)

        name = utils.cleantext(alt)
        if q:
            name += " [COLOR hotpink]({})[/COLOR]".format(q)
        site.add_download_link(name, videopage, "Playvid", img, "", duration=duration)

    next_btn = soup.select_one("a.next.page-numbers")
    if next_btn:
        next_url = utils.safe_get_attr(next_btn, "href").replace("&#038;", "&")
        curr_el = soup.select_one(".page-numbers.current")
        curr_pg = utils.safe_get_text(curr_el) or "1"
        page_nums = [
            utils.safe_get_text(p)
            for p in soup.select("a.page-numbers")
            if utils.safe_get_text(p).isdigit()
        ]
        last_pg = page_nums[-1] if page_nums else curr_pg
        site.add_dir(
            "Next Page... (Currently in Page {} of {})".format(curr_pg, last_pg),
            next_url,
            "List",
            site.img_next,
        )

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = url + keyword.replace(" ", "+")
        List(search_url)


@site.register()
def Categories(url):
    for pg in ("", "?pg=2", "?pg=3"):
        page_url = url + pg
        try:
            cathtml = utils.getHtml(page_url, site.url)
        except urllib_error.URLError:
            continue
        if not cathtml:
            continue
        soup = utils.parse_html(cathtml)
        chips = soup.select("a.chip")
        for chip in chips:
            catpage = utils.safe_get_attr(chip, "href")
            cnt_el = chip.select_one("small")
            cnt = utils.safe_get_text(cnt_el)
            if cnt_el:
                cnt_el.decompose()
            name = utils.safe_get_text(chip)
            if not catpage or not name:
                continue
            title = utils.cleantext(name)
            if cnt:
                title += " [COLOR hotpink]({})[/COLOR]".format(cnt)
            site.add_dir(title, catpage, "List", site.img_cat)

    utils.eod()


@site.register()
def Studios(url):
    try:
        studhtml = utils.getHtml(url, site.url)
    except urllib_error.URLError as e:
        utils.notify(str(e))
        return

    soup = utils.parse_html(studhtml)
    cards = soup.select("a.tcard")
    for card in cards:
        studpage = utils.safe_get_attr(card, "href")
        img_el = card.select_one("img")
        img = utils.safe_get_attr(img_el, "src") or ""
        alt = utils.safe_get_attr(img_el, "alt")
        bold_el = card.select_one("b")
        bold = utils.safe_get_text(bold_el)
        movies_el = card.select_one("small")
        movies = utils.safe_get_text(movies_el)
        name = alt or bold or ""
        title = utils.cleantext(name)
        if movies:
            title += " [COLOR hotpink]({})[/COLOR]".format(movies)
        site.add_dir(title, studpage, "List", img)

    re_npurl = r'<a\s+class="next\spage-numbers"\s+href="([^"]+)"[^>]*>'
    re_npnr = r'<a\s+class="next\spage-numbers"\s+href=".+?pg=(\d+)"[^>]*>'
    re_lpnr = r'\?pg=.+?(\d+)</a><a class="next'
    utils.next_page(
        site,
        "watchpornx.Studios",
        studhtml,
        re_npurl,
        re_npnr,
        re_lpnr=re_lpnr,
        contextm="watchpornx.GotoPage",
    )
    utils.eod()


@site.register()
def GotoPage(url, np, lp=None):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        if lp and int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        url = url.split("?")[0] + "?pg={}".format(pg)
        contexturl = (
            utils.addon_sys
            + "?mode=watchpornx.Studios&url="
            + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


def extract_servers(html):
    soup = utils.parse_html(html)
    hlm = soup.select_one("[data-servers], section.hlm, div.hlm")
    if not hlm:
        return None, 0, []
    data_rest = utils.safe_get_attr(hlm, "data-rest")
    post_id = int(utils.safe_get_attr(hlm, "data-post") or "0")
    raw = utils.safe_get_attr(hlm, "data-servers") or ""
    try:
        servers = json.loads(raw)
    except Exception:
        servers = []
    return data_rest, post_id, servers


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    dontask = utils.addon.getSetting("dontask") == "true"

    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    try:
        r = session.get(url, timeout=15)
        if r.status_code != 200:
            xbmcgui.Dialog().notification(
                "Playvid", "Could not load video page", xbmcgui.NOTIFICATION_ERROR
            )
            return
        html = r.text
    except Exception as e:
        utils.kodilog("watchpornx Playvid request error: {}".format(e))
        xbmcgui.Dialog().notification(
            "Playvid", "Failed to connect", xbmcgui.NOTIFICATION_ERROR
        )
        return

    data_rest, post_id, servers = extract_servers(html)
    if not servers:
        xbmcgui.Dialog().notification(
            "Playvid", "No servers found", xbmcgui.NOTIFICATION_ERROR
        )
        return

    server_names = [s.get("l", "Server {}".format(i + 1)) for i, s in enumerate(servers)]

    if not dontask:
        idx = xbmcgui.Dialog().select("Select server", server_names)
        if idx == -1:
            return
    else:
        idx = 0

    def resolve_server(server):
        if server.get("u"):
            return server["u"]

        if not data_rest:
            return ""

        api = data_rest + "link"
        payload = {"p": post_id, "h": server.get("h")}
        try:
            rr = session.post(api, json=payload, timeout=10)
            j = rr.json()
            return j.get("go", "")
        except Exception as err:
            utils.kodilog("watchpornx server resolve error: {}".format(err))
            return ""

    # Automatic Fallback through available servers
    for i in range(idx, len(servers)):
        server = servers[i]
        utils.kodilog("watchpornx trying server: {}".format(server))
        go = resolve_server(server)
        if go:
            if vp.play_from_link_to_resolve(go):
                return

    xbmcgui.Dialog().notification(
        "Playvid", "All servers have failed.", xbmcgui.NOTIFICATION_ERROR
    )
