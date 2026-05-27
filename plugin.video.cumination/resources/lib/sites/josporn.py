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
    "[COLOR hotpink]josporn.net[/COLOR]",
    "https://josporn.net/",
    "josporn.png",
    "josporn",
    category="Video Tubes",
    requires_flaresolverr=True,
)


@site.register(default_mode=True)
def Main(url):
    site.add_dir("[COLOR hotpink]Most Popular[/COLOR]", site.url + "most-popular/", "List", "")
    site.add_dir("[COLOR hotpink]Latest Updates[/COLOR]", site.url + "latest-updates/", "List", "")
    site.add_dir("[COLOR hotpink]Top Rated[/COLOR]", site.url + "top-rated/", "List", "")
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url + "categories/", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Models[/COLOR]", site.url + "models/", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search)
    utils.eod()


@site.register()
def List(url, page=1):
    html, _ = utils.get_html_with_cloudflare_retry(
        url, site.url, retry_on_empty=True
    )

    if not html:
        utils.notify(msg="List blocked/challenged")
        utils.eod()
        return

    soup = utils.parse_html(html)
    if not soup:
        utils.eod()
        return
    
    # Video items are in .item div
    items = soup.select(".item")
    for item in items:
        link = item.select_one("a[href*='/sex-video-online/']")
        if not link:
            continue
            
        videopage = utils.safe_get_attr(link, "href")
        videopage = urllib_parse.urljoin(site.url, videopage)
        
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-original", ["src"])
        if img:
            img = urllib_parse.urljoin(site.url, img)
            
        name = utils.safe_get_attr(link, "title") or utils.safe_get_text(item.select_one(".title"))
        name = utils.cleantext(name)
        
        duration = utils.safe_get_text(item.select_one(".duration"))
        
        site.add_download_link(
            name, videopage, "Playvid", img, name, duration=duration
        )

    # Pagination
    next_el = soup.select_one(".pagination a.next") or \
              soup.select_one(".pagination a:-soup-contains('Next')")
    if next_el:
        np_url = utils.safe_get_attr(next_el, "href")
        if np_url:
            np_url = urllib_parse.urljoin(site.url, np_url)
            site.add_dir("Next Page", np_url, "List", site.img_next)

    utils.eod()


@site.register()
def Categories(url):
    html, _ = utils.get_html_with_cloudflare_retry(
        url, site.url, retry_on_empty=True
    )

    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    
    # Categories are in .item a tags or .category_tegs or #leftcategories or sidebars
    cats = soup.select(".item[href*='/categories/'], .item[href*='/models/'], .category_tegs a, #leftcategories a, .list li a[href*='/categories/']")
        
    for cat in cats:
        catpage = utils.safe_get_attr(cat, "href")
        catpage = urllib_parse.urljoin(site.url, catpage)
        
        name = utils.safe_get_attr(cat, "title") or utils.safe_get_text(cat.select_one(".category_name")) or utils.safe_get_text(cat)
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
    
    html, _ = utils.get_html_with_cloudflare_retry(
        url, site.url, retry_on_empty=True
    )
    if not html:
        utils.notify("Error", "Could not load video page")
        return
    
    # Try schema.org contentUrl extraction
    # "contentUrl": "https://josporn.net/get_file/..."
    content_match = re.search(r'"contentUrl":\s*"([^"]+)"', html)
    if content_match:
        video_url = content_match.group(1).replace("\\/", "/")
        utils.kodilog("josporn: Found contentUrl: {}".format(video_url))
        vp.play_from_direct_link(video_url + "|Referer=" + site.url + "&User-Agent=" + utils.USER_AGENT)
        return

    # Try Playerjs extraction
    pjs_match = re.search(r'new\s+Playerjs\({(?:id:"[^"]+",\s*)?file:"([^"]+)"', html)
    if pjs_match:
        file_data = pjs_match.group(1)
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
