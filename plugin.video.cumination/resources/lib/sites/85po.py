"""
Cumination
Copyright (C) 2025 Cumination

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
import time
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse
import xbmc
import xbmcgui
from resources.lib.decrypters.kvsplayer import kvs_decode


site = AdultSite(
    "85po", "[COLOR hotpink]85po[/COLOR]", "https://85po.com/", "85po.png", "85po"
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]4K[/COLOR]", site.url + "4k/", "List", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "en/search/{}/",
        "Search",
        site.img_search,
    )
    List(site.url + "en/latest-updates/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url)
    if "There is no data in this list." in listhtml:
        utils.notify(msg="No videos found!")
        return

    soup = utils.parse_html(listhtml)

    # Find all video items
    items = soup.select('div.thumb.thumb_rel.item, div[class*="thumb"][class*="item"]')

    cm = []
    cm_lookupinfo = utils.addon_sys + "?mode=" + str("85po.Lookupinfo") + "&url="
    cm.append(
        ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + cm_lookupinfo + ")")
    )
    cm_related = utils.addon_sys + "?mode=" + str("85po.Related") + "&url="
    cm.append(
        ("[COLOR deeppink]Related videos[/COLOR]", "RunPlugin(" + cm_related + ")")
    )

    for item in items:
        link = item.select_one("a")
        if not link:
            continue

        videourl = utils.safe_get_attr(link, "href")
        name = utils.safe_get_attr(link, "title")

        if not videourl or not name:
            continue

        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-original", ["src", "data-src"])

        # Duration
        duration_tag = item.select_one("span.fa-clock")
        if duration_tag and duration_tag.parent:
            duration = (
                utils.safe_get_text(duration_tag.parent, "").replace("\n", "").strip()
            )
        else:
            duration = ""

        # Quality - normalize quality labels
        quality_tag = item.select_one('div.qualtiy, div[class*="qualtiy"]')
        quality = utils.safe_get_text(quality_tag, "")
        quality = (
            quality.replace("1K", "720p").replace("2K", "1080p").replace("4K", "2160p")
        )

        # Build name with quality and duration
        if quality:
            name = "[COLOR yellow]" + quality + "[/COLOR] " + name
        if duration:
            name = name + " [COLOR deeppink]" + duration + "[/COLOR]"

        site.add_download_link(name, videourl, "Playvid", img, name, contextm=cm)

    # Pagination - try async first, then fallback to standard
    pagination_added = False
    active_page = soup.select_one("a.active")
    next_link = soup.select_one("a.next")

    if active_page and next_link:
        current_page = utils.safe_get_text(active_page)
        if current_page:
            try:
                npage = int(current_page) + 1
                block_id = utils.safe_get_attr(next_link, "data-block-id")
                params = utils.safe_get_attr(next_link, "data-parameters")

                if block_id and params:
                    params = params.replace(";", "&").replace(":", "=")
                    ts = int(time.time() * 1000)
                    nurl = url.split("?")[
                        0
                    ] + "?mode=async&function=get_block&block_id={0}&{1}&_={2}".format(
                        block_id, params, ts
                    )

                    lpnr, lastp = 0, ""
                    # Find last page number
                    page_links = soup.select("a[href]")
                    for plink in reversed(page_links):
                        if plink.get("class") and "next" in plink.get("class"):
                            # Check previous sibling for last page number
                            prev_sibling = plink.find_previous_sibling("a")
                            if prev_sibling:
                                last_text = utils.safe_get_text(prev_sibling)
                                if last_text.isdigit():
                                    lpnr = last_text
                                    lastp = "/{}".format(lpnr)
                                    break

                    nurl = nurl.replace("+from_albums", "")
                    nurl = re.sub(
                        r"&from([^=]*)=\d+", r"&from\1={}".format(npage), nurl
                    )

                    cm_page = (
                        utils.addon_sys
                        + "?mode=85po.GotoPage"
                        + "&url="
                        + urllib_parse.quote_plus(nurl)
                        + "&np="
                        + str(npage)
                        + "&lp="
                        + str(lpnr)
                    )
                    cm = [
                        (
                            "[COLOR violet]Goto Page #[/COLOR]",
                            "RunPlugin(" + cm_page + ")",
                        )
                    ]

                    site.add_dir(
                        "[COLOR hotpink]Next Page...[/COLOR] ("
                        + str(npage)
                        + lastp
                        + ")",
                        nurl,
                        "List",
                        site.img_next,
                        contextm=cm,
                    )
                    pagination_added = True
            except (ValueError, AttributeError):
                pass

    # Fallback: standard pagination
    if not pagination_added:
        # Try finding pagination div and next link
        pagination = soup.select_one("div.pagination, nav.pagination, .pager")
        if pagination:
            next_link = pagination.select_one('a.next, a[rel="next"], li.next a')
            if next_link:
                next_href = utils.safe_get_attr(next_link, "href")
                if next_href:
                    next_url = urllib_parse.urljoin(url, next_href)
                    site.add_dir(
                        "[COLOR hotpink]Next Page...[/COLOR]",
                        next_url,
                        "List",
                        site.img_next,
                    )

    utils.eod()


@site.register()
def GotoPage(url, np, lp=0):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        url = re.sub(r"&from([^=]*)=\d+", r"&from\1={}".format(pg), url, re.IGNORECASE)
        contexturl = (
            utils.addon_sys + "?mode=" + "85po.List&url=" + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        List(url.format(keyword.replace(" ", "-")))


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, site.url)
    sources = {}
    license = re.compile(
        r"license_code:\s*'([^']+)", re.DOTALL | re.IGNORECASE
    ).findall(videopage)[0]
    patterns = [
        r"video_url:\s*'([^']+)[^;]+?video_url_text:\s*'([^']+)",
        r"video_alt_url:\s*'([^']+)[^;]+?video_alt_url_text:\s*'([^']+)",
        r"video_alt_url2:\s*'([^']+)[^;]+?video_alt_url2_text:\s*'([^']+)",
        r"video_alt_url3:\s*'([^']+)[^;]+?video_alt_url3_text:\s*'([^']+)",
        r"video_url:\s*'([^']+)',\s*(postfix):\s*'\.mp4'",
    ]
    for pattern in patterns:
        items = re.compile(pattern, re.DOTALL | re.IGNORECASE).findall(videopage)
        for surl, qual in items:
            qual = "480p" if qual == "postfix" else qual
            qual = "2160p" if qual == "4K" else qual
            surl = kvs_decode(surl, license)
            sources.update({qual: surl})
    vp.progress.update(50, "[CR]Loading video[CR]")
    videourl = utils.selector(
        "Select quality",
        sources,
        setting_valid="qualityask",
        sort_by=lambda x: 1081 if x == "4k" else int(x[:-1]),
        reverse=True,
    )
    if videourl:
        vp.progress.update(75, "[CR]Video found[CR]")
        vp.play_from_direct_link(videourl)


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Tags", r'href="https://www.85po.com/(en/tags/[^"]+)">([^<]+)<', "")
    ]
    lookupinfo = utils.LookupInfo(site.url, url, "85po.List", lookup_list)
    lookupinfo.getinfo()


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("85po.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")
