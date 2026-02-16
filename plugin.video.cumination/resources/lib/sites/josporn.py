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
    site.add_dir("[COLOR hotpink]Latest Updates[/COLOR]", site.url + "latest-updates/", "List", "")
    site.add_dir("[COLOR hotpink]Most Popular[/COLOR]", site.url + "most-popular/", "List", "")
    site.add_dir("[COLOR hotpink]Top Rated[/COLOR]", site.url + "top-rated/", "List", "")
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url + "categories/", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "latest-updates/", "Search", site.img_search)
    utils.eod()


@site.register()
def List(url, page=1):
    html = utils.getHtml(url)
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
    html = utils.getHtml(url)
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
    
    # Check for <video src="...">
    video_match = re.search(r'<video[^>]+src=["\']\s*([^"\']+)["\']', html, re.IGNORECASE)
    if video_match:
        video_url = video_match.group(1).strip()
        utils.kodilog("josporn: Found direct video URL: {}".format(video_url))
        vp.play_from_direct_link(video_url + "|Referer=" + site.url + "&User-Agent=" + utils.USER_AGENT)
        return

    utils.notify("Error", "Could not find video URL")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        # Search URL structure: site.url + "search/" + keyword + "/"
        search_url = site.url + "search/" + urllib_parse.quote(keyword) + "/"
        List(search_url)
