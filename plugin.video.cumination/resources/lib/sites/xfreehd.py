"""
Cumination
Copyright (C) 2018 Whitecream

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

import re
import xbmc
import xbmcgui
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "xfreehd",
    "[COLOR hotpink]XFreeHD[/COLOR]",
    "https://beta.xfreehd.com/",
    "xfreehd.png",
    "xfreehd",
)

getinput = utils._get_keyboard
xflogged = "true" in utils.addon.getSetting("xflogged")


@site.register(default_mode=True)
def Main():
    search_orders = {
        "Relevance": "",
        "Most Recent": "mr",
        "Being Watched": "bw",
        "Most Viewed": "mv",
        "Most Commented": "md",
        "Top Rated": "tr",
        "Top Favorited": "tf",
        "Longest": "lg",
    }
    search_order = utils.addon.getSetting("xfreeorder") or "Relevance"
    search_order = search_order if search_order in search_orders else "Relevance"
    context = utils.addon_sys + "?mode=xfreehd.Sortorder"
    contextmenu = [("[COLOR orange]Search Order[/COLOR]", "RunPlugin(" + context + ")")]

    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories",
        "Cat",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR] [COLOR orange][{}][/COLOR]".format(search_order),
        site.url + "search?search_query=",
        "Search",
        site.img_search,
        contextm=contextmenu,
    )
    if not xflogged:
        site.add_dir("[COLOR hotpink]Login[/COLOR]", "", "Login", "", Folder=False)
    else:
        xfuser = utils.addon.getSetting("xfuser")
        site.add_dir(
            "[COLOR hotpink]Logout [/COLOR][COLOR orange][{}][/COLOR]".format(xfuser),
            "",
            "Logout",
            "",
            Folder=False,
        )
    List(site.url + "videos?o=mr")


@site.register()
def List(url):
    hdr = dict(utils.base_hdrs)
    hdr["Cookie"] = get_cookies()
    try:
        listhtml = utils.getHtml(url, site.url, headers=hdr)
    except Exception as e:
        utils.kodilog("@@@@Cumination: failure in xfreehd: " + str(e))
        return None

    if xflogged and '"/user">My Profile<' not in listhtml:
        Login()
        hdr["Cookie"] = get_cookies()
        listhtml = utils.getHtml(url, site.url, headers=hdr)

    soup = utils.parse_html(listhtml)
    video_items = soup.select(".well.well-sm")

    for item in video_items:
        link = item.select_one('a[href*="/video/"]')
        if not link:
            continue

        videourl = utils.safe_get_attr(link, "href")
        if not videourl.startswith("http"):
            videourl = site.url[:-1] + videourl

        title_tag = item.select_one(".title-new")
        name = utils.cleantext(utils.safe_get_text(title_tag))

        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])
        if img and not img.startswith("http"):
            img = site.url[:-1] + img

        duration_tag = item.select_one(".duration-new")
        duration = utils.safe_get_text(duration_tag)

        # HD and Private status are often in badges or labels
        badges = item.select(".badge, span[class*='label']")
        hd = ""
        is_private = False
        for badge in badges:
            text = utils.safe_get_text(badge).upper()
            if "HD" in text:
                hd = "HD"
            if "PRIVATE" in text:
                is_private = True

        if is_private:
            if xflogged:
                name = "[COLOR blue][PV][/COLOR] " + name
            else:
                continue

        cm = []
        cm_lookupinfo = (
            utils.addon_sys
            + "?mode="
            + str("xfreehd.Lookupinfo")
            + "&url="
            + urllib_parse.quote_plus(videourl)
        )
        cm.append(
            ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + cm_lookupinfo + ")")
        )
        cm_related = (
            utils.addon_sys
            + "?mode="
            + str("xfreehd.Related")
            + "&url="
            + urllib_parse.quote_plus(videourl)
        )
        cm.append(
            ("[COLOR deeppink]Related videos[/COLOR]", "RunPlugin(" + cm_related + ")")
        )

        site.add_download_link(
            name,
            videourl,
            "Play",
            img,
            name,
            duration=duration,
            quality=hd,
            contextm=cm,
        )

    next_page_tag = soup.select_one('a.prevnext[href*="page="]')
    if next_page_tag and not url.startswith(site.url + "video/"):
        next_page = utils.safe_get_attr(next_page_tag, "href")
        if not next_page.startswith("http"):
            next_page = site.url[:-1] + next_page

        # Extract page info
        page_number = "".join([nr for nr in next_page.split("=")[-1] if nr.isdigit()])
        showing_text = soup.select_one(".pagination-wrapper, .pagination-info")
        pages = None
        last_page = ""

        # Try to find total pages from "Showing ... of Z videos"
        showing_info = utils.safe_get_text(showing_text)
        lp_match = re.search(r"of (\d+) videos", showing_info)
        if lp_match:
            total_videos = int(lp_match.group(1))
            pages = total_videos // 30 + 1
            last_page = "/" + str(pages)

        cm_page = (
            utils.addon_sys
            + "?mode=xfreehd.GotoPage"
            + "&url="
            + urllib_parse.quote_plus(next_page)
            + "&np="
            + page_number
            + "&lp="
            + str(pages)
        )
        cm = [("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")]

        site.add_dir(
            "Next Page (" + page_number + last_page + ")",
            next_page,
            "List",
            site.img_next,
            contextm=cm,
        )
    utils.eod()


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("xfreehd.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Cat(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    # Selector based on regex: class="col-xs-6\s*col-sm-4\scol
    cat_items = soup.select('div[class*="col-xs-6"][class*="col-sm-4"]')

    for item in cat_items:
        link = item.select_one("a[href]")
        if not link:
            continue

        catpage = utils.safe_get_attr(link, "href")
        caturl = site.url[:-1] + catpage if catpage.startswith("/") else catpage

        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])
        if img and not img.startswith("http"):
            img = site.url[:-1] + img

        name_tag = item.select_one("h3, .title, a[title]")
        name = utils.safe_get_attr(link, "title") or utils.safe_get_text(name_tag)

        count_tag = item.select_one(".badge")
        videos = utils.safe_get_text(count_tag)

        display_name = utils.cleantext(name)
        if videos:
            display_name += " [COLOR hotpink]%s Videos[/COLOR]" % videos

        site.add_dir(display_name, caturl, "List", img)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "%20")
        search_orders = {
            "Relevance": "",
            "Most Recent": "mr",
            "Being Watched": "bw",
            "Most Viewed": "mv",
            "Most Commented": "md",
            "Top Rated": "tr",
            "Top Favorited": "tf",
            "Longest": "lg",
        }
        search_order = utils.addon.getSetting("xfreeorder") or "Relevance"
        search_order = search_order if search_order in search_orders else "Relevance"
        url = (
            url + title + "&search_type=videos&o={}".format(search_orders[search_order])
            if search_order != "Relevance"
            else url + title + "&search_type=videos"
        )
        List(url)


@site.register()
def Sortorder():
    search_orders = {
        "Relevance": "",
        "Most Recent": "mr",
        "Being Watched": "bw",
        "Most Viewed": "mv",
        "Most Commented": "md",
        "Top Rated": "tr",
        "Top Favorited": "tf",
        "Longest": "lg",
    }
    order = utils.selector("Select sort order", search_orders.keys())
    if order:
        utils.addon.setSetting("xfreeorder", order)
        utils.refresh()


@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    hdr = dict(utils.base_hdrs)
    hdr["Cookie"] = get_cookies()
    html = utils.getHtml(url, site.url, headers=hdr)

    if "This is a private video." in html:
        if '/user">My Profile<' not in html:
            utils.notify("Cumination", "Not logged in!")
            return
        match = re.compile(r'data-id="([^"]+)">', re.DOTALL | re.IGNORECASE).findall(
            html
        )
        if match:
            userid = match[0]
            posturl = site.url + "ajax/subscribe"
            postdata = {"user_id": userid}
            response = utils._postHtml(posturl, form_data=postdata, headers=hdr)
            html = utils._getHtml(url, site.url, headers=hdr)
        if not match or '"status":-1' in response:
            utils.notify("Cumination", "Subscribe error...")
            return

    sources = {}
    srcs = re.compile(
        r'''src="([^"]+)"\s*title="(SD|HD)"''', re.DOTALL | re.IGNORECASE
    ).findall(html)

    if srcs:
        sources = {x[1]: x[0] for x in srcs}
        videourl = utils.selector(
            "Select quality", sources, setting_valid="qualityask", sort_by=lambda x: x
        )
        if videourl:
            videourl = videourl + "|verifypeer=false"
            vp.play_from_direct_link(videourl)


@site.register()
def Login():
    xfuser = (
        utils.addon.getSetting("xfuser") if utils.addon.getSetting("xfuser") else ""
    )
    xfpass = (
        utils.addon.getSetting("xfpass") if utils.addon.getSetting("xfpass") else ""
    )
    if xfuser == "":
        xfuser = getinput(default=xfuser, heading="Input your XFreeHD username")
        xfpass = getinput(
            default=xfpass, heading="Input your XFreeHD password", hidden=True
        )
    loginurl = "{0}login".format(site.url)
    postRequest = {"username": xfuser, "password": xfpass, "submit_login": ""}
    response = utils._postHtml(loginurl, form_data=postRequest)
    if "Welcome {}!".format(xfuser) in response:
        utils.addon.setSetting("xflogged", "true")
        utils.addon.setSetting("xfuser", xfuser)
        utils.addon.setSetting("xfpass", xfpass)
        success = True
        utils.refresh()
    else:
        utils.notify(
            "Failure logging in", "Failure, please check your username or password"
        )
        utils.addon.setSetting("xfuser", "")
        utils.addon.setSetting("xfpass", "")
        success = False
    return success


@site.register()
def Logout():
    clear = utils.selector("Clear stored user & password?", ["Yes", "No"], reverse=True)
    if clear:
        if clear == "Yes":
            utils.addon.setSetting("xfuser", "")
            utils.addon.setSetting("xfpass", "")
        utils.addon.setSetting("xflogged", "false")
        utils._getHtml(site.url + "logout")
        utils.refresh()


@site.register()
def GotoPage(url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        if "page=" in url:
            url = url.replace("page={}".format(np), "page={}".format(pg))
        contexturl = (
            utils.addon_sys + "?mode=xfreehd.List&url=" + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


def get_cookies():
    cookiestr = ""
    for cookie in utils.cj:
        if cookie.domain == ".xfreehd.com" and cookie.name == "FX":
            cookiestr = "FX=" + cookie.value + "; enterModal=1"
    if xflogged and "FX=" not in cookiestr:
        Login()
    return cookiestr


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Category", '<a class="standard-link" href="(/videos/[^"]+)">([^<]+)</a>', ""),
        (
            "Tag",
            '<a class="tag" href="https://www.xfreehd.com/(tag/[^"]+)">([^<]+)</a>',
            "",
        ),
    ]
    lookupinfo = utils.LookupInfo(site.url, url, "xfreehd.List", lookup_list)
    lookupinfo.getinfo()
