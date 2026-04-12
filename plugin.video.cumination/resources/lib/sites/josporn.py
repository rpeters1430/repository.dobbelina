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

import re
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "josporn",
    "[COLOR hotpink]josporn.com[/COLOR]",
    "https://josporn.club/",
    "josporn.png",
    "josporn",
)


@site.register(default_mode=True)
def Main(url):
    site.add_dir("[COLOR hotpink]Latest Updates[/COLOR]", site.url + "videos/", "List", "")
    site.add_dir("[COLOR hotpink]Most Popular[/COLOR]", site.url + "most-popular/", "List", "")
    site.add_dir("[COLOR hotpink]Top Rated[/COLOR]", site.url + "top-rated/", "List", "")
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url + "categories/", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search)
    utils.eod()


@site.register()
def List(url, page=1):
    headers = {"User-Agent": utils.USER_AGENT, "Referer": site.url}
    try:
        html = utils.getHtml(url, site.url, headers=headers)
    except Exception as e:
        utils.kodilog("@@@@Cumination: failure in josporn: " + str(e))
        # Fallback with different UA and bypass param
        headers["User-Agent"] = utils.random_ua.get_ua()
        fallback_url = url + ("?" if "?" not in url else "&") + "label_W9dmamG9w9zZg45g93FnLAVbSyd0bBDv=1"
        html = utils.getHtml(fallback_url, site.url, headers=headers)

    if hasattr(html, "select"):
        soup = html
    else:
        if not isinstance(html, (str, bytes)):
            html = ""
        soup = utils.parse_html(html)
    
    # Video items are in .innercont div
    items = soup.select(".innercont")
    for item in items:
        link = item.select_one(".preview_screen a") or item.select_one(".preview_title a")
        if not link:
            continue
            
        videopage = utils.safe_get_attr(link, "href")
        videopage = urllib_parse.urljoin(site.url, videopage)
        
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src")
        if img:
            img = urllib_parse.urljoin(site.url, img)
            
        name = utils.safe_get_attr(img_tag, "alt") or utils.safe_get_text(link)
        name = utils.cleantext(name)
        
        duration = utils.safe_get_text(item.select_one(".duration"))
        
        site.add_download_link(
            name, videopage, "Playvid", img, name, duration=duration
        )

    # Pagination
    # Use -soup-contains for compatibility
    next_el = soup.select_one(".navigation a:-soup-contains('Next')") or \
              soup.select_one(".navigation a:-soup-contains('>')") or \
              soup.select_one(".mobnavigation a:-soup-contains('Next')")
    if next_el:
        np_url = utils.safe_get_attr(next_el, "href")
        if np_url:
            np_url = urllib_parse.urljoin(site.url, np_url)
            site.add_dir("Next Page", np_url, "List", site.img_next)

    utils.eod()


@site.register()
def Categories(url):
    headers = {"User-Agent": utils.USER_AGENT, "Referer": site.url}
    try:
        html = utils.getHtml(url, site.url, headers=headers)
    except Exception as e:
        headers["User-Agent"] = utils.random_ua.get_ua()
        html = utils.getHtml(url, site.url, headers=headers)

    soup = utils.parse_html(html)
    
    # Categories are in .category_tegs or #leftcategories
    cats = soup.select(".category_tegs a")
    if not cats:
        cats = soup.select("#leftcategories a")
        
    for cat in cats:
        catpage = utils.safe_get_attr(cat, "href")
        catpage = urllib_parse.urljoin(site.url, catpage)
        
        name = utils.safe_get_text(cat.select_one(".category_name")) or utils.safe_get_text(cat)
        name = utils.cleantext(name)
        
        img = ""
        img_tag = cat.select_one("img")
        if img_tag:
            img = utils.safe_get_attr(img_tag, "src")
            img = urllib_parse.urljoin(site.url, img)
            
        site.add_dir(name, catpage, "List", img)
        
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    
    # The site uses pjs player which often has the direct mp4 link in the source
    html = utils.getHtml(url)
    
    # Try Playerjs extraction
    # var player = new Playerjs({id:"videoplayer", file:"[240p] https://...mp4,[360p] ..."})
    pjs_match = re.search(r'new\s+Playerjs\({(?:id:"[^"]+",\s*)?file:"([^"]+)"', html)
    if pjs_match:
        file_data = pjs_match.group(1)
        # file_data can be "[720p] https://url1,[480p] https://url2" or just "https://url"
        sources = {}
        if "[" in file_data:
            qualities = re.findall(r'\[(\d+p)\]\s*([^\s,]+)', file_data)
            if qualities:
                sources = {q: u for q, u in qualities}
        
        if sources:
            video_url = utils.prefquality(sources, sort_by=lambda x: int(x[:-1]), reverse=True)
            if video_url:
                utils.kodilog("josporn: Found Playerjs video URL: {}".format(video_url))
                vp.play_from_direct_link(video_url + "|Referer=" + site.url + "&User-Agent=" + utils.USER_AGENT)
                return
        elif file_data.startswith("http"):
            video_url = file_data
            utils.kodilog("josporn: Found direct Playerjs URL: {}".format(video_url))
            vp.play_from_direct_link(video_url + "|Referer=" + site.url + "&User-Agent=" + utils.USER_AGENT)
            return

    # Check for <video src="...">
    video_match = re.search(r'<video[^>]+src=["\']\s*([^"\']+)["\']', html, re.IGNORECASE)
    if video_match:
        video_url = video_match.group(1).strip()
        video_url = urllib_parse.urljoin(site.url, video_url)
        utils.kodilog("josporn: Found direct video URL: {}".format(video_url))
        vp.play_from_direct_link(video_url + "|Referer=" + site.url + "&User-Agent=" + utils.USER_AGENT)
        return

    # Fallback: <source src="..."> within the player markup.
    source_match = re.search(
        r'<source[^>]+src=["\']\s*([^"\']+)["\']', html, re.IGNORECASE
    )
    if source_match:
        video_url = urllib_parse.urljoin(site.url, source_match.group(1).strip())
        utils.kodilog("josporn: Found source video URL: {}".format(video_url))
        vp.play_from_direct_link(
            video_url + "|Referer=" + site.url + "&User-Agent=" + utils.USER_AGENT
        )
        return

    utils.notify("Error", "Could not find video URL")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        # Search URL structure: site.url + "search/?text=" + keyword
        search_url = site.url + "search/?text=" + urllib_parse.quote_plus(keyword)
        List(search_url)
