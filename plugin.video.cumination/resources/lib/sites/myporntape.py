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
from resources.lib.decrypters.kvsplayer import kvs_decode
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "myporntape",
    "[COLOR hotpink]MyPornTape[/COLOR]",
    "https://myporntape.com/",
    "myporntape.png",
    "myporntape",
    category="Video Tubes"
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Latest[/COLOR]", site.url + "latest-updates/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Top Rated[/COLOR]", site.url + "top-rated/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Most Viewed[/COLOR]", site.url + "most-popular/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url + "categories/", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search)
    List(site.url)


@site.register()
def List(url):
    html = utils.getHtml(url)
    soup = utils.parse_html(html)
    
    # Each video item is inside a div.item
    for item in soup.select("div.item"):
        link = item.select_one("a.link")
        if not link:
            # Fallback to any 'a' with title and href containing '/videos/'
            link = item.select_one("a[href*='/videos/'][title]")
        if not link:
            continue
            
        video_url = utils.safe_get_attr(link, "href")
        if not video_url:
            continue
        video_url = urllib_parse.urljoin(site.url, video_url)
        
        name = utils.safe_get_attr(link, "title")
        if not name:
            title_el = item.select_one(".title-post")
            name = utils.safe_get_text(title_el)
        name = utils.cleantext(name)
        
        img_el = item.select_one("img.thumb")
        img = utils.safe_get_attr(img_el, "data-webp", ["data-original", "src"])
        if img and img.startswith("//"):
            img = "https:" + img
        elif img and img.startswith("/"):
            img = urllib_parse.urljoin(site.url, img)
            
        duration_el = item.select_one("span.time")
        duration = utils.safe_get_text(duration_el).strip() if duration_el else ""
        
        hd = ""
        hd_el = item.select_one("span.type")
        if hd_el and "hd" in utils.safe_get_text(hd_el).lower():
            hd = "HD"
            
        views_el = item.select_one(".stat i.icon-eye")
        views = ""
        if views_el:
            parent = views_el.parent
            if parent:
                views = utils.safe_get_text(parent).strip()
                
        rating_el = item.select_one(".atten")
        rating = ""
        if rating_el:
            rating = utils.safe_get_text(rating_el).strip()
            
        label = name
        if duration:
            label += f" [COLOR yellow]({duration})[/COLOR]"
        if hd:
            label += f" [COLOR cyan][{hd}][/COLOR]"
        if views or rating:
            stats = []
            if views:
                stats.append(f"{views} views")
            if rating:
                stats.append(f"{rating} rating")
            label += f" [COLOR hotpink][{', '.join(stats)}][/COLOR]"
            
        site.add_download_link(label, video_url, "Playvid", img, name)
        
    # Pagination
    next_el = soup.select_one(".pagination div.next a, a.btn[href*='/latest-updates/'], a.btn[href*='/top-rated/'], a.btn[href*='/most-popular/'], .pagination a.btn")
    if next_el:
        np_url = utils.safe_get_attr(next_el, "href")
        if np_url:
            np_url = urllib_parse.urljoin(site.url, np_url)
            page_match = re.search(r'/(\d+)/?$', np_url)
            page_nr = page_match.group(1) if page_match else ""
            label = f"Next Page... ({page_nr})" if page_nr else "Next Page..."
            site.add_dir(label, np_url, "List", site.img_next)
            
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url)
    soup = utils.parse_html(html)
    
    # Each category item is a.item-video or div.item-video
    for item in soup.select(".block-post a.item, .block-post div.item"):
        link = item if item.name == "a" else item.select_one("a")
        if not link:
            continue
            
        cat_url = utils.safe_get_attr(link, "href")
        if not cat_url:
            continue
        cat_url = urllib_parse.urljoin(site.url, cat_url)
        
        name = utils.safe_get_attr(link, "title")
        if not name:
            title_el = item.select_one(".title-post")
            name = utils.safe_get_text(title_el)
        name = utils.cleantext(name).strip().title()
        
        img_el = item.select_one("img.thumb")
        img = utils.safe_get_attr(img_el, "src")
        if img and img.startswith("//"):
            img = "https:" + img
        elif img and img.startswith("/"):
            img = urllib_parse.urljoin(site.url, img)
            
        count_el = item.select_one(".info-view .text")
        count = utils.safe_get_text(count_el).strip() if count_el else ""
        
        label = name
        if count:
            label += f" [COLOR deeppink][{count} videos][/COLOR]"
            
        site.add_dir(label, cat_url, "List", img)
        
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        # Search form url pattern is https://myporntape.com/search/%QUERY%/
        query = keyword.replace(" ", "+")
        search_url = urllib_parse.urljoin(site.url, f"search/{query}/")
        List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url)
    
    # Try to find KVS player variables
    license = re.search(r"license_code:\s*'([^']+)", html, re.IGNORECASE)
    video_url = re.search(r"video_url:\s*'([^']+)", html, re.IGNORECASE)
    
    if license and video_url:
        lc = license.group(1)
        vu = video_url.group(1)
        
        final_url = kvs_decode(vu, lc)
        final_url += "|User-Agent={0}&Referer={1}".format(utils.USER_AGENT, url)
        vp.play_from_direct_link(final_url)
    else:
        # Fallback to direct page resolution
        vp.play_from_site_link(url)
