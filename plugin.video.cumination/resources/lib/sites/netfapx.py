"""
Cumination
Copyright (C) 2022 Team Cumination

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
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "netfapx",
    "[COLOR hotpink]Netfapx[/COLOR]",
    "https://netfapx.com/",
    "netfapx.png",
    "netfapx",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories & Tags[/COLOR]",
        site.url + "categories",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Pornstars[/COLOR]",
        site.url + "pornstar/?orderby=popular",
        "Pornstars",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url + "?orderby=newest")
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if (
        ">No posts found.<" in html
        or "Sorry, the page you were looking for was not found" in html
    ):
        utils.notify(msg="Nothing found")
        utils.eod()
        return

    soup = utils.parse_html(html)
    if not soup:
        utils.eod()
        return

    for article in soup.select("article.pinbox"):
        link = article.select_one(".thumb[href]")
        if not link:
            link = article.select_one("a[href]")
        if not link:
            continue

        videopage = urllib_parse.urljoin(
            site.url, utils.safe_get_attr(link, "href", default="")
        )
        name = utils.cleantext(
            utils.safe_get_attr(
                link,
                "title",
                default=utils.safe_get_text(
                    article.select_one(".title") or link, default=""
                ),
            )
        )
        if not videopage or not name:
            continue

        img_tag = article.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"])
        duration = utils.safe_get_text(
            article.select_one('[title="Duration"]'), default=""
        )

        site.add_download_link(
            name, videopage, "netfapx.Playvid", img, name, duration=duration
        )

    pagination = soup.select_one("a.next[href]")
    if pagination:
        next_url = utils.safe_get_attr(pagination, "href", default="")
        page_match = re.search(r"/page/(\d+)", next_url)
        page_num = page_match.group(1) if page_match else ""
        last_page = ""
        last_link = soup.select_one(".pagination a:last-of-type[href]")
        if last_link:
            last_match = re.search(
                r"/page/(\d+)", utils.safe_get_attr(last_link, "href", default="")
            )
            last_page = last_match.group(1) if last_match else ""

        contextmenu = []
        if page_num and last_page:
            contexturl = (
                utils.addon_sys
                + "?mode=netfapx.GotoPage"
                + "&list_mode=netfapx.List"
                + "&url="
                + urllib_parse.quote_plus(url)
                + "&np="
                + page_num
                + "&lp="
                + last_page
            )
            contextmenu.append(
                ("[COLOR violet]Goto Page[/COLOR]", "RunPlugin(" + contexturl + ")")
            )

        label = "Next Page"
        if page_num and last_page:
            label += f" ({page_num}/{last_page})"
        elif page_num:
            label += f" ({page_num})"
        site.add_dir(
            label, next_url, "netfapx.List", site.img_next, contextm=contextmenu
        )
    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = url.replace("/page/{}".format(np), "/page/{}".format(pg))
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
def Categories(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    if not soup:
        utils.eod()
        return

    category_section = soup.select(".infovideo-cat img[src]")
    for img_tag in category_section:
        caturl = utils.safe_get_attr(img_tag.find_parent("a"), "href", default="")
        img = utils.safe_get_attr(img_tag, "src", default="")
        name = img.split("/")[-1].split(".")[0].replace("-", " ") if img else ""
        if not caturl or not name:
            continue
        site.add_dir(name, caturl, "List", img)

    footer_section = soup.select_one(".footerbar") or soup
    for link in footer_section.select("a[href]"):
        name = utils.cleantext(utils.safe_get_text(link, default=""))
        caturl = utils.safe_get_attr(link, "href", default="")
        if not name or not caturl:
            continue
        site.add_dir("[tag] " + name, caturl, "List", "")
    utils.eod()


@site.register()
def Pornstars(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    if not soup:
        utils.eod()
        return

    for preview in soup.select(".preview"):
        link = preview.select_one("a[href]")
        img_tag = preview.select_one("img")
        name_elem = preview.select_one("img[alt]") or link
        count_elem = preview.select_one('[title="Videos"]') or preview.select_one(
            ".videos-count"
        )

        caturl = utils.safe_get_attr(link, "href", default="")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"])
        name = utils.cleantext(
            utils.safe_get_attr(
                name_elem, "alt", default=utils.safe_get_text(name_elem, default="")
            )
        )
        count = utils.safe_get_text(count_elem, default="")

        if not caturl or not name:
            continue

        caturl = caturl.replace("/pornstar/", "/videos/")
        if count:
            name = f"{name}[COLOR hotpink] ({count} videos)[/COLOR]"
        site.add_dir(name, caturl, "List", img)

    pagination = soup.select_one("a.next[href]")
    if pagination:
        next_url = utils.safe_get_attr(pagination, "href", default="")
        page_match = re.search(r"/page/(\d+)", next_url)
        page_num = page_match.group(1) if page_match else ""
        last_page = ""
        last_link = soup.select_one(".pagination a:last-of-type[href]")
        if last_link:
            last_match = re.search(
                r"/page/(\d+)", utils.safe_get_attr(last_link, "href", default="")
            )
            last_page = last_match.group(1) if last_match else ""

        contextmenu = []
        if page_num and last_page:
            contexturl = (
                utils.addon_sys
                + "?mode=netfapx.GotoPage"
                + "&list_mode=netfapx.Pornstars"
                + "&url="
                + urllib_parse.quote_plus(url)
                + "&np="
                + page_num
                + "&lp="
                + last_page
            )
            contextmenu.append(
                ("[COLOR violet]Goto Page[/COLOR]", "RunPlugin(" + contexturl + ")")
            )

        label = "Next Page"
        if page_num and last_page:
            label += f" ({page_num}/{last_page})"
        elif page_num:
            label += f" ({page_num})"
        site.add_dir(
            label, next_url, "netfapx.Pornstars", site.img_next, contextm=contextmenu
        )
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}".format(url, keyword.replace(" ", "%20"))
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    videohtml = utils.getHtml(url, site.url)
    match = re.compile(
        r"ajax_object\s*=\s*({[^}]+})", re.IGNORECASE | re.DOTALL
    ).findall(videohtml)
    if match:
        match_data = json.loads(match[0])
        id = match_data.get("post_id")
        ajax_url = match_data.get("ajax_url")

        if id and ajax_url:
            videourl = utils.getHtml(
                ajax_url, site.url, data="action=get_download_url&idpost={}".format(id)
            )
            if videourl:
                vp.play_from_direct_link(videourl)
                return

    utils.notify("Oh Oh", "No Videos found")
