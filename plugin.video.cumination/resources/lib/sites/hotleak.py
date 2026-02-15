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
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "hotleak",
    "[COLOR lightblue]Hotleak[/COLOR]",
    "https://hotleak.vip/",
    "hotleak.png",
    "hotleak",
)


@site.register(default_mode=True)
def Main(url):
    site.add_dir("[COLOR lightblue]Videos[/COLOR]", site.url + "videos", "List", "")
    site.add_dir("[COLOR lightblue]Search[/COLOR]", site.url + "videos", "Search", site.img_search)
    utils.eod()


@site.register()
def List(url, page=1):
    try:
        from resources.lib.playwright_helper import fetch_with_playwright
        listhtml = fetch_with_playwright(url, wait_for="load")
    except (ImportError, Exception):
        listhtml = utils.getHtml(url)

    soup = utils.parse_html(listhtml)
    items = soup.select("article.movie-item")
    for item in items:
        link = item.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href")
        if not videopage or "tantaly.com" in videopage: # Skip ads
            continue
        videopage = urllib_parse.urljoin(site.url, videopage)

        img_tag = item.select_one("img.post-thumbnail")
        img = utils.safe_get_attr(img_tag, "src")
        if img:
            img = urllib_parse.urljoin(site.url, img)
            img = img + "|User-Agent=" + utils.USER_AGENT

        name = utils.safe_get_text(item.select_one(".movie-name h3"))
        if not name:
            name = utils.safe_get_attr(img_tag, "alt", default="Video")

        date = utils.safe_get_text(item.select_one(".date"))
        views = utils.safe_get_text(item.select_one(".view"))
        meta = []
        if date: meta.append(date)
        if views: meta.append(views)
        description = " | ".join(meta)

        site.add_download_link(
            name, videopage, "Playvid", img, desc=description
        )

    # Next Page
    next_el = soup.select_one("a.page-link[rel='next']")
    if next_el:
        np_url = utils.safe_get_attr(next_el, "href")
        if np_url:
            np_url = urllib_parse.urljoin(site.url, np_url)
            page_match = re.search(r"page=(\d+)", np_url)
            np = page_match.group(1) if page_match else str(int(page) + 1)
            site.add_dir("Next Page ({})".format(np), np_url, "List", site.img_next, page=np)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    try:
        from resources.lib.playwright_helper import sniff_video_url
        vp.progress.update(50, "[CR]Sniffing with Playwright...[CR]")
        
        ad_domains = ["leakedzone.com", "ourdream.ai", "adtng.com", "trafficjunky.net", "jwpltx.com"]
        
        video_url = sniff_video_url(
            url, 
            play_selectors=["#media-player", ".jw-video", ".btn-play"], 
            exclude_domains=ad_domains,
            debug=True
        )
        
        if video_url:
            vp.play_from_direct_link(video_url + "|Referer=" + site.url)
            return
            
    except (ImportError, Exception) as e:
        utils.kodilog("hotleak: Playwright sniffing failed: {}".format(e))

    # Fallback to HTML parsing
    html = utils.getHtml(url)
    vp.play_from_html(html)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = site.url + "search?search=" + urllib_parse.quote(keyword)
        List(search_url)
