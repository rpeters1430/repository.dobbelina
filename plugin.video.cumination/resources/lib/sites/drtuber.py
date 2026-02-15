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
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite
import json

site = AdultSite(
    "drtuber",
    "[COLOR hotpink]DrTuber[/COLOR]",
    "https://www.drtuber.com/",
    "drtuber.png",
    "drtuber",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Cat",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/videos/",
        "Search",
        site.img_search,
    )
    site.add_dir("[COLOR hotpink]HD[/COLOR]", site.url + "hd/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]4k[/COLOR]", site.url + "4k/", "List", site.img_cat)

    List(site.url)


@site.register()
def List(url):
    # Add small delay for paginated/search requests to avoid rate limiting
    # (drtuber rate limits after ~30 search results if requests are too fast)
    is_paginated = any(
        x in url for x in ["/search/", "?page=", "/page/", "/2/", "/3/", "/4/"]
    )
    if is_paginated:
        import time

        time.sleep(1.5)  # 1.5 second delay to avoid rate limits

    listhtml = utils.getHtml(url)

    # Check for rate limit or empty response
    if not listhtml or len(listhtml) < 100:
        utils.kodilog("drtuber: Empty or very short response - possible rate limit")
        utils.notify(
            msg="DrTuber may have rate limited this request. Try again in a few seconds."
        )
        utils.eod()
        return

    soup = utils.parse_html(listhtml)

    # Find all video items (they use <a> tags with class "th ch-video")
    video_items = soup.select('a.th[href*="/video"]')

    for item in video_items:
        try:
            # item IS the <a> tag, so get href directly
            videopage = utils.safe_get_attr(item, "href")
            if not videopage:
                continue

            # Make absolute URL if needed
            if videopage.startswith("/"):
                videopage = site.url[:-1] + videopage
            elif not videopage.startswith("http"):
                videopage = site.url + videopage

            # Get image
            img_tag = item.select_one("img")
            img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])

            # Get title from alt attribute or span > em
            name = utils.safe_get_attr(img_tag, "alt")
            if not name:
                name_tag = item.select_one("span em")
                name = utils.safe_get_text(name_tag) if name_tag else "Video"
            name = utils.cleantext(name)

            # Get duration from .time_thumb em
            duration_tag = item.select_one(".time_thumb > em")
            duration = utils.safe_get_text(duration_tag)

            # Get quality (HD icon)
            quality = "HD" if item.select_one(".ico_hd") else ""

            # Add video to list
            site.add_download_link(
                name, videopage, "Play", img, name, duration=duration, quality=quality
            )

        except Exception as e:
            # Log error but continue processing other videos
            utils.kodilog("Error parsing video item: " + str(e))
            continue

    # Handle pagination
    next_link = soup.select_one("a.next, li.next a")
    if not next_link:
        # Try alternate pagination patterns
        pagination = soup.select("div.pagination a, ul.pagination a")
        for link in pagination:
            if "next" in utils.safe_get_text(link).lower():
                next_link = link
                break

    if next_link:
        next_url = utils.safe_get_attr(next_link, "href")
        if next_url:
            # Make absolute URL
            if next_url.startswith("/"):
                next_url = site.url[:-1] + next_url
            elif not next_url.startswith("http"):
                next_url = site.url + next_url

            # Extract page numbers for display
            page_match = re.search(r"/(\d+)(?:/|$|\?)", next_url)
            np = page_match.group(1) if page_match else ""

            # Try to find last page number
            lp = ""
            last_page_links = soup.select("div.pagination a, ul.pagination a")
            page_numbers = []
            for link in last_page_links:
                text = utils.safe_get_text(link)
                if text.isdigit():
                    page_numbers.append(int(text))
            if page_numbers:
                lp = str(max(page_numbers))

            # Create context menu for goto page
            cm_page = (
                utils.addon_sys
                + "?mode=drtuber.GotoPage&list_mode=drtuber.List&url="
                + urllib_parse.quote_plus(next_url)
                + "&np="
                + str(np)
                + "&lp="
                + str(lp)
            )
            cm = [("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")]

            page_label = "Next Page"
            if np:
                page_label += " (" + np
                if lp:
                    page_label += "/" + lp
                page_label += ")"

            site.add_dir(page_label, next_url, "List", site.img_next, contextm=cm)

    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = url.replace("/{}".format(np), "/{}".format(pg))
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
def Cat(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)

    # Find all category items
    category_items = soup.select("li.item")

    categories = []
    for item in category_items:
        try:
            # Get category link
            link = item.select_one("a")
            if not link:
                continue

            caturl = utils.safe_get_attr(link, "href")
            if not caturl:
                continue

            # Make absolute URL if needed
            if caturl.startswith("/"):
                caturl = site.url[:-1] + caturl
            elif not caturl.startswith("http"):
                caturl = site.url + caturl

            # Get category name
            name_tag = item.select_one("span")
            name = utils.safe_get_text(name_tag)

            # Get video count
            count_tag = item.select_one("b")
            count = utils.safe_get_text(count_tag)

            # Combine name and count
            full_name = (
                utils.cleantext(name + " " + count) if count else utils.cleantext(name)
            )

            categories.append((full_name, caturl))

        except Exception as e:
            utils.kodilog("Error parsing category item: " + str(e))
            continue

    # Add categories in sorted order
    for name, caturl in sorted(categories, key=lambda x: x[0].lower()):
        site.add_dir(name, caturl, "List", "")

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}".format(url, keyword.replace(" ", "+"))
        List(url)


@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download=download)
    
    # Try Playwright sniffer first
    try:
        from resources.lib.playwright_helper import fetch_with_playwright_and_network
        vp.progress.update(40, "[CR]Sniffing with Playwright...[CR]")
        _, requests = fetch_with_playwright_and_network(url, wait_for="load")
        for req in requests:
            if any(ext in req["url"].lower() for ext in [".mp4", ".m3u8"]):
                if not any(x in req["url"].lower() for x in ["/thumbs/", "/images/"]):
                    vp.play_from_direct_link(req["url"])
                    return
    except (ImportError, Exception):
        pass

    # More robust video ID extraction
    videoid_match = re.search(r"/video/(\d+)", url)
    if not videoid_match:
        # Try finding it in the page if not in URL
        vpage = utils.getHtml(url, site.url)
        videoid_match = re.search(r'video_id:\s*(\d+)', vpage)
        if not videoid_match:
            videoid_match = re.search(r'vid=(\d+)', url)
            
    if not videoid_match:
        utils.notify("Error", "Could not find video ID")
        return
        
    videoid = videoid_match.group(1)
    jsonurl = (
        site.url
        + "player_config_json/?vid={}&aid=0&domain_id=0&embed=0&ref=null&check_speed=0".format(
            videoid
        )
    )
    hdr = utils.base_hdrs.copy()
    hdr["accept"] = "application/json, text/javascript, */*; q=0.01"
    jsondata = utils.getHtml(jsonurl, url, headers=hdr)
    if not jsondata:
        utils.notify("Error", "Could not load player config")
        return

    try:
        data = json.loads(jsondata)
    except Exception:
        utils.notify("Error", "Failed to parse player config")
        return
    
    srcs = {}
    files = {}
    if isinstance(data, dict):
        files = data.get("files", {})
    elif isinstance(data, list) and len(data) > 0:
        # If it's a list, the first item might contain the files
        item = data[0]
        if isinstance(item, dict):
            files = item.get("files", {})

    if isinstance(files, dict):
        for v, link in files.items():
            if link:
                if v == "lq":
                    srcs["480p"] = link
                elif v == "hq":
                    srcs["720p"] = link
                elif v == "4k":
                    srcs["2160p"] = link
    elif isinstance(files, list):
        for item in files:
            if isinstance(item, dict):
                v = item.get("label", "").lower()
                link = item.get("url") or item.get("file")
                if link:
                    if "lq" in v or "480" in v:
                        srcs["480p"] = link
                    elif "hq" in v or "720" in v:
                        srcs["720p"] = link
                    elif "2160" in v or "4k" in v:
                        srcs["2160p"] = link
                    elif v:
                        srcs[v] = link

    video = utils.prefquality(srcs, sort_by=lambda x: int(x[:-1]), reverse=True)
    if video:
        vp.play_from_direct_link(video)
