"""
Cumination
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

import re
import xbmc
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "pornez",
    "[COLOR hotpink]PornEZ[/COLOR]",
    "https://pornezoo.net",
    "pornez.png",
    "pornez",
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url, "Cat", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url)


@site.register()
def List(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    for item in soup.select(".video-block, [data-post-id], article, .video-item, .item"):
        link = item.select_one("a.infos[href], a[href][title], a[href]")
        videourl = utils.safe_get_attr(link, "href", default="")
        if not videourl:
            continue
        img_tag = item.select_one(".video-img, img")
        img = utils.get_thumbnail(img_tag)
        
        # Try to get name from .title span, then link title, then link text
        title_span = item.select_one(".title")
        if title_span:
            name = utils.cleantext(title_span.get_text())
        else:
            name = utils.cleantext(utils.safe_get_attr(link, "title", default=""))
            
        if not name:
            name = utils.cleantext(utils.safe_get_text(link, default=""))
        if not name or name == "Live Cams":
            continue
        duration = utils.safe_get_text(item.select_one(".duration"), default="")

        cm_related = (
            utils.addon_sys
            + "?mode="
            + str("pornez.ContextRelated")
            + "&url="
            + urllib_parse.quote_plus(videourl)
        )
        cm = [
            (
                "[COLOR violet]Related videos[/COLOR]",
                "RunPlugin(" + cm_related + ")",
            )
        ]
        site.add_download_link(
            name, videourl, "Play", img, name, duration=duration, contextm=cm
        )

    npage = ""
    np = ""
    for a in soup.select("a[href]"):
        href = utils.safe_get_attr(a, "href", default="")
        text = utils.safe_get_text(a, default="")
        if "/page/" in href and (
            "\xbb" in text or "»" in text or "next" in text.lower()
        ):
            npage = href
            m = re.search(r"/page/(\d+)", href)
            np = m.group(1) if m else ""
            break
    if npage:
        lp = ""
        page_links = []
        for a in soup.select("a.page-link[href]"):
            page_text = utils.safe_get_text(a, default="").replace(",", "")
            if page_text.isdigit():
                page_links.append(page_text)
        if page_links:
            lp = "/" + page_links[-1]
        site.add_dir(
            "[COLOR hotpink]Next Page...[/COLOR] ({0}{1})".format(np, lp),
            npage,
            "List",
            site.img_next,
        )
    utils.eod()


@site.register()
def Cat(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    matches = []
    for link in soup.select("a.btn.btn-grey[href]"):
        caturl = utils.safe_get_attr(link, "href", default="")
        name = utils.safe_get_text(link, default="")
        if caturl and name:
            matches.append((caturl, name))
    matches = matches[:-1]
    for caturl, name in matches:
        name = utils.cleantext(name)
        site.add_dir(name, caturl, "List", "")
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}".format(url, keyword.replace(" ", "%20"))
        List(url)


@site.register()
def ContextRelated(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("pornez.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download=download)
    videohtml = utils.getHtml(url)
    soup = utils.parse_html(videohtml)
    
    # Try to find embed URL (myvidplay or others)
    playerurl = utils.safe_get_attr(soup.select_one("iframe[src]"), "src", default="")
    if not playerurl:
        playerurl = "".join(re.findall(r'meta itemprop="embedURL" content="([^"]+)"', videohtml))
        
    if not playerurl:
        return
        
    if playerurl.startswith("//"):
        playerurl = "https:" + playerurl
        
    if vp.resolveurl.HostedMediaFile(playerurl):
        vp.play_from_link_to_resolve(playerurl)
    else:
        playerhtml = utils.getHtml(playerurl, url)
        player_soup = utils.parse_html(playerhtml)
        videourl = utils.safe_get_attr(
            player_soup.select_one("source[src]"), "src", default=""
        )
        if videourl:
            vp.play_from_direct_link(videourl)
