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

import re
import xbmc
import xbmcgui
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "tubxporn",
    "[COLOR hotpink]TubXporn[/COLOR]",
    "https://web.tubxporn.com/",
    "tubxporn.png",
    "tubxporn",
    category="Video Tubes",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/?q=",
        "Search",
        site.img_search,
    )
    List(site.url + "latest-updates/")
    utils.eod()


@site.register()
def List(url):
    headers = {"User-Agent": utils.USER_AGENT, "Referer": site.url}
    html = ""
    candidates = [url]
    if "/latest-updates/" not in url and "/search/" not in url and "/categories/" not in url:
        candidates.append(site.url + "latest-updates/")
    tried = set()
    for candidate in candidates:
        if not candidate or candidate in tried:
            continue
        tried.add(candidate)
        try:
            html = utils.getHtml(candidate, site.url, headers=headers)
        except Exception as e:
            utils.kodilog("@@@@Cumination: failure in tubxporn: " + str(e))
            # Fallback with different UA and bypass parameter
            headers["User-Agent"] = utils.random_ua.get_ua()
            fallback_url = candidate + (
                "?" if "?" not in candidate else "&"
            ) + "label_W9dmamG9w9zZg45g93FnLAVbSyd0bBDv=1"
            try:
                html = utils.getHtml(fallback_url, site.url, headers=headers)
            except Exception as fallback_err:
                utils.kodilog(
                    "@@@@Cumination: fallback failure in tubxporn: "
                    + str(fallback_err)
                )
                html = ""
        if html:
            break

    if not html:
        utils.notify(msg="List blocked/challenged in harness")
        utils.eod()
        return
    if isinstance(html, bytes):
        html = html.decode("utf-8", errors="ignore")
    challenge_markers = (
        "attention required",
        "checking your browser",
        "cf-chl",
        "cf-ray",
        "captcha",
    )
    if isinstance(html, str) and any(marker in html.lower() for marker in challenge_markers):
        utils.notify(msg="List blocked/challenged in harness (Cloudflare)")
        utils.eod()
        return
    if "There are no videos in the list" in html:
        utils.notify(msg="Nothing found")
        utils.eod()
        return

    soup = utils.parse_html(html)
    if not soup:
        utils.eod()
        return

    for inner in soup.select(".inner"):
        link = inner.select_one("a[href][title]")
        if not link:
            continue

        videopage = utils.safe_get_attr(link, "href", default="")
        # Skip rexporn.com links
        if "www.rexporn.com" in videopage:
            continue

        name = utils.cleantext(utils.safe_get_attr(link, "title", default=""))
        img_tag = inner.select_one("img")
        img = utils.get_thumbnail(img_tag)
        if img and not img.startswith("http"):
            img = "https:" + img

        duration_elem = inner.select_one(".length")
        duration = utils.safe_get_text(duration_elem, default="")

        if videopage and name:
            site.add_download_link(
                name,
                videopage,
                "tubxporn.Playvid",
                img,
                name,
                duration=duration,
                contextm="tubxporn.Related",
            )

    # Pagination
    next_link = soup.select_one("a.mobnav[href]")
    if next_link and "Next" in utils.safe_get_text(next_link, default=""):
        next_url = utils.safe_get_attr(next_link, "href", default="")
        if next_url:
            # Extract page number from next URL
            np_match = re.search(r"/(\d+)(?:/\?|/)", next_url)
            np = np_match.group(1) if np_match else ""

            # Find last page number
            lp = ""
            for page_link in soup.select("a[href]"):
                page_text = utils.safe_get_text(page_link, default="")
                if page_text.isdigit():
                    lp = max(lp, page_text) if lp else page_text

            contextmenu = []
            if np and lp:
                baseurl = (
                    url.split("page")[0] if "page" in url else url.rstrip("/") + "/"
                )
                contexturl = (
                    utils.addon_sys
                    + "?mode=tubxporn.GotoPage"
                    + "&list_mode=tubxporn.List"
                    + "&url="
                    + urllib_parse.quote_plus(baseurl)
                    + "&np="
                    + np
                    + "&lp="
                    + lp
                )
                contextmenu.append(
                    ("[COLOR violet]Goto Page[/COLOR]", "RunPlugin(" + contexturl + ")")
                )

            label = "Next Page"
            if np and lp:
                label += f" ({np}/{lp})"
            elif np:
                label += f" ({np})"
            site.add_dir(
                label, next_url, "tubxporn.List", site.img_next, contextm=contextmenu
            )

    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = url.replace("/{}/".format(np), "/{}/".format(pg))
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
def Related(url):
    contexturl = (
        utils.addon_sys + "?mode=tubxporn.List&url=" + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        search_url = url if "q=" in url else site.url + "search/?q="
        site.search_dir(search_url, "Search")
    else:
        base_url = url if "q=" in url else site.url + "search/?q="
        url = "{0}{1}".format(base_url, keyword.replace(" ", "%20"))
        List(url)


@site.register()
def Categories(url):
    headers = {"User-Agent": utils.USER_AGENT, "Referer": site.url}
    try:
        cathtml = utils.getHtml(url, site.url, headers=headers)
    except Exception as e:
        utils.kodilog("@@@@Cumination: failure in tubxporn: " + str(e))
        headers["User-Agent"] = utils.random_ua.get_ua()
        cathtml = utils.getHtml(url, site.url, headers=headers)

    soup = utils.parse_html(cathtml)
    if not soup:
        utils.eod()
        return

    for item in soup.select(".item"):
        link = item.select_one("a[href]")
        if not link:
            continue

        caturl = utils.safe_get_attr(link, "href", default="")
        img_tag = item.select_one("img")
        img = utils.get_thumbnail(img_tag)

        h2 = item.select_one("h2")
        if h2:
            # Extract name and count from h2 text (e.g., "Category Name (123)")
            full_text = utils.safe_get_text(h2, default="")
            count_match = re.search(r"\((\d+)\)", full_text)
            count = count_match.group(1) if count_match else ""
            name = re.sub(r"\s*\(\d+\)\s*$", "", full_text)
            name = utils.cleantext(name)
            if count:
                name = name + "[COLOR hotpink] ({} videos)[/COLOR]".format(count)
        else:
            name = utils.cleantext(utils.safe_get_text(link, default=""))

        if caturl and name:
            site.add_dir(name, caturl, "List", img)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    try:
        videohtml = utils.getHtml(url, site.url)
    except Exception as e:
        utils.kodilog("@@@@Cumination: failure in tubxporn: " + str(e))
        videohtml = utils._getHtml(
            url + "?label_W9dmamG9w9zZg45g93FnLAVbSyd0bBDv=1", site.url
        )

    soup = utils.parse_html(videohtml)
    
    # New method: find all a tags with data-c
    data_c_items = soup.select("a[data-c]")
    sources = {}
    for item in data_c_items:
        data_c = utils.safe_get_attr(item, "data-c")
        quality_text = utils.safe_get_text(item) or data_c.split(";")[1]
        if "p" in quality_text:
            sources[quality_text] = data_c

    # Fallback to old regex if soup select fails
    if not sources:
        match = re.compile(
            r'data-c="([^"]+)">\D*(\d+p)<', re.IGNORECASE | re.DOTALL
        ).findall(videohtml)
        if match:
            sources = {x[1]: x[0] for x in match}

    if sources:
        data_c = utils.prefquality(
            sources, sort_by=lambda x: int(x[:-1]) if x[:-1].isdigit() else 0, reverse=True
        )
        videolink = data_c.split(";")
        # Format: hash;quality;size;?;id;timestamp;token;host
        # e.g. 38a2fe95...;1080p;830500;190;20554;1776024134;rhWOnEDjDEOn8h6V1PssLQ;d2
        
        host = videolink[7] if len(videolink) > 7 else "d2"
        # Try both vstor.top and vstors.top
        for base_host in ["vstors.top", "vstor.top"]:
            videourl = "https://{0}.{1}/whpvid/{2}/{3}/{4}/{5}/{5}.mp4".format(
                host,
                base_host,
                videolink[5],
                videolink[6],
                str(int(videolink[4]) // 1000 * 1000), # Folder structure usually rounded
                videolink[4],
            )
            # Some versions use a different structure
            # Let's try to find the actual structure from the video tag if possible
            video_tag = soup.find("video")
            if video_tag and utils.safe_get_attr(video_tag, "src"):
                videourl = utils.safe_get_attr(video_tag, "src")
                break
            
            # Check if this URL is likely valid (basic check)
            if len(videolink) > 6:
                 break

        vp.play_from_direct_link(videourl + "|Referer=" + site.url + "&User-Agent=" + utils.USER_AGENT)
        return

    # Direct video tag fallback
    video_tag = soup.find("video")
    if video_tag and utils.safe_get_attr(video_tag, "src"):
        videourl = utils.safe_get_attr(video_tag, "src")
        vp.play_from_direct_link(videourl + "|Referer=" + site.url + "&User-Agent=" + utils.USER_AGENT)
        return

    utils.notify("Error", "Could not find video URL")
