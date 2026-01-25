"""
Cumination site scraper
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

import re
from six.moves import urllib_parse
import xbmc
import xbmcgui
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.decrypters.kvsplayer import kvs_decode
import ast


site = AdultSite(
    "xxxtube",
    "[COLOR hotpink]X-X-X Video[/COLOR]",
    "https://x-x-x.tube/",
    "xxxtube.png",
    "xxxtube",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "/search/{0}/",
        "Search",
        site.img_search,
    )
    List(site.url + "videos/?by=post_date")
    utils.eod()


@site.register()
def List(url):
    if "/videos/" not in url and (
        "/categories/" in url or "/tags/" in url or "/models/" in url
    ):
        url += "videos/?by=post_date"
    listhtml = utils.getHtml(url)

    cm = []
    cm_lookupinfo = utils.addon_sys + "?mode=" + str("xxxtube.Lookupinfo") + "&url="
    cm.append(
        ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + cm_lookupinfo + ")")
    )
    cm_related = utils.addon_sys + "?mode=" + str("xxxtube.Related") + "&url="
    cm.append(
        ("[COLOR deeppink]Related videos[/COLOR]", "RunPlugin(" + cm_related + ")")
    )

    soup = utils.parse_html(listhtml)
    items = soup.select(".thumb-inner")
    if not items:
        utils.notify(msg="No videos found!")
        return
    for item in items:
        link = item.find("a", href=True)
        if not link:
            continue
        videopage = utils.safe_get_attr(link, "href")
        if not videopage:
            continue
        videopage = urllib_parse.urljoin(site.url, videopage)
        name = utils.safe_get_attr(link, "title")
        if not name:
            img_tag = link.find("img")
            name = utils.safe_get_attr(img_tag, "alt") if img_tag else ""
        if not name:
            name = utils.safe_get_text(link)
        name = utils.cleantext(name)
        if not name:
            continue
        img_tag = item.find("img")
        img = utils.safe_get_attr(
            img_tag, "data-original", ["data-src", "data-lazy", "src"]
        )
        if img:
            img = urllib_parse.urljoin(site.url, img)
        duration_tag = item.select_one(".duration")
        duration = utils.cleantext(utils.safe_get_text(duration_tag))
        site.add_download_link(
            name,
            videopage,
            "xxxtube.Playvid",
            img or site.image,
            name,
            contextm=cm,
            duration=duration,
        )

    next_link = None
    active = soup.select_one("li.item.active")
    if active:
        next_li = active.find_next_sibling("li")
        if next_li:
            next_link = next_li.find("a", href=True)
    if next_link:
        href = utils.safe_get_attr(next_link, "href")
        if href:
            next_url = urllib_parse.urljoin(site.url, href)
            npnr = utils.safe_get_text(next_link)
            if not npnr.isdigit():
                match = re.search(r"/(\\d+)/", href)
                npnr = match.group(1) if match else ""
            lpnr = ""
            page_numbers = []
            for anchor in soup.select("li.item a"):
                text = utils.safe_get_text(anchor)
                if text.isdigit():
                    page_numbers.append(int(text))
            if page_numbers:
                lpnr = str(max(page_numbers))
            label = "Next Page"
            if npnr:
                label = "Next Page ({})".format(npnr)
                if lpnr:
                    label = "Next Page ({}/{})".format(npnr, lpnr)
            cm_page = (
                utils.addon_sys
                + "?mode="
                + "xxxtube.GotoPage"
                + "&list_mode="
                + "xxxtube.List"
                + "&url="
                + urllib_parse.quote_plus(next_url)
                + "&np="
                + str(npnr)
                + "&lp="
                + str(lpnr or 0)
            )
            cm = [("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")]
            site.add_dir(label, next_url, "List", contextm=cm)
    utils.eod()


@site.register()
def GotoPage(url, np, lp=None):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        url = re.sub(r"&from([^=]*)=\d+", r"&from\1={}".format(pg), url, re.IGNORECASE)
        url = url.replace("/{}/".format(np), "/{}/".format(pg))
        contexturl = (
            utils.addon_sys
            + "?mode="
            + "xxxtube.List&url="
            + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    vpage = utils.getHtml(url, site.url)

    sources = {}
    flashvars = re.compile(
        r"flashvars\s*=\s*({.+?});", re.DOTALL | re.IGNORECASE
    ).findall(vpage)
    if flashvars:
        vpage = flashvars[0]
        vpage = re.sub(r"(\w+):\s+", r'"\1":', vpage)
        fwdict = ast.literal_eval(vpage)
        license = fwdict.get("license_code", "")

        for k, v in (
            (fwdict.get("video_url_text"), fwdict.get("video_url")),
            (fwdict.get("video_alt_url_text"), fwdict.get("video_alt_url")),
            (fwdict.get("video_alt_url2_text"), fwdict.get("video_alt_url2")),
        ):
            if v and k:
                key = k if k.upper() not in ("MAX", "HD") else "720p"
                sources[key] = v
            elif v:
                for q in [
                    "4k",
                    "2160p",
                    "1440p",
                    "1080p",
                    "720p",
                    "480p",
                    "360p",
                    "240p",
                ]:
                    if q in v:
                        sources[q] = v
                        continue
                if v not in sources.values():
                    sources["0p"] = v
    try:
        enc_videourl = utils.prefquality(
            sources,
            setting_valid="qualityask",
            sort_by=lambda x: 2160 if x == "4k" else int(x[:-1]),
            reverse=True,
        )
    except:
        enc_videourl = utils.selector("Select quality", sources, reverse=True)

    if enc_videourl:
        videourl = (
            kvs_decode(enc_videourl, license)
            if enc_videourl.startswith("function/0/")
            else enc_videourl
        )
        vp.play_from_direct_link(videourl + "|Referer=" + url)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        List(url.format(keyword.replace(" ", "-")))


@site.register()
def Lookupinfo(url):
    lookup_list = [
        (
            "Actor",
            r'<a href="{}(models/([^"]+)/)" class="btn">\s*View Model\s*<'.format(
                site.url
            ),
            "",
        ),
        (
            "Category",
            r'<a class="btn" href="{}(categories/[^"]+)">([^<]+)<'.format(site.url),
            "",
        ),
        ("Tag", r'<a class="btn" href="{}(tags/[^"]+)">([^<]+)<'.format(site.url), ""),
    ]
    lookupinfo = utils.LookupInfo(site.url, url, "xxxtube.List", lookup_list)
    lookupinfo.getinfo()


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("xxxtube.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")
