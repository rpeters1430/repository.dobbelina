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
    "pornxpert",
    "[COLOR hotpink]PornXpert[/COLOR]",
    "https://www.pornxpert.com/",
    "pornxpert.png",
    "pornxpert",
)


@site.register(default_mode=True)
def Main(url):
    site.add_dir("[COLOR hotpink]Latest Videos[/COLOR]", site.url + "latest-updates/", "List", "")
    site.add_dir("[COLOR hotpink]Most Popular[/COLOR]", site.url + "most-popular/", "List", "")
    site.add_dir("[COLOR hotpink]Top Rated[/COLOR]", site.url + "top-rated/", "List", "")
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url + "categories/", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "latest-updates/", "Search", site.img_search)
    utils.eod()


@site.register()
def List(url, page=1):
    html = utils.getHtml(url)
    soup = utils.parse_html(html)
    
    # KVS uses .item for video containers
    items = soup.select(".item")
    for item in items:
        link = item.select_one("a")
        if not link or "/video/" not in utils.safe_get_attr(link, "href"):
            continue

        videopage = utils.safe_get_attr(link, "href")
        videopage = urllib_parse.urljoin(site.url, videopage)

        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-original"])
        if img and img.startswith("data:"):
            img = utils.safe_get_attr(img_tag, "data-original")
        if img:
            img = urllib_parse.urljoin(site.url, img)

        name = utils.safe_get_attr(img_tag, "alt") or utils.safe_get_text(link)
        name = utils.cleantext(name)

        duration = utils.safe_get_text(item.select_one(".duration"))

        site.add_download_link(
            name, videopage, "Playvid", img, name, duration=duration
        )

    # Pagination - KVS uses .load-more with an anchor to next page
    next_el = soup.select_one(".load-more a")
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
    
    # Categories are a.item elements (the .item IS the <a> tag)
    cats = soup.select("a.item")
    for cat in cats:
        catpage = utils.safe_get_attr(cat, "href")
        if not catpage or "/categories/" not in catpage:
            continue
        catpage = urllib_parse.urljoin(site.url, catpage)

        name = utils.safe_get_text(cat.select_one(".title")) or utils.safe_get_attr(cat, "title")
        name = utils.cleantext(name)

        img = ""
        img_tag = cat.select_one("img")
        if img_tag:
            img = utils.safe_get_attr(img_tag, "src")
            if img:
                img = urllib_parse.urljoin(site.url, img)

        site.add_dir(name, catpage, "List", img)
        
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    
    html = utils.getHtml(url)
    
    # KVS player config often has video_url: '...'
    video_match = re.search(r"video_url:\s*['\"]([^\"']+)['\"]", html)
    if video_match:
        video_url = video_match.group(1)
        # Check if it starts with function/0/ (common in KVS)
        if video_url.startswith("function/0/"):
            video_url = video_url[11:]
            
        utils.kodilog("pornxpert: Found video URL in config: {}".format(video_url))
        vp.play_from_direct_link(video_url + "|Referer=" + site.url + "&User-Agent=" + utils.USER_AGENT)
        return

    # Check for JSON-LD contentUrl
    json_match = re.search(r'["\']contentUrl["\']:\s*["\']([^"\']+)["\']', html)
    if json_match:
        video_url = json_match.group(1)
        utils.kodilog("pornxpert: Found video URL in JSON-LD: {}".format(video_url))
        vp.play_from_direct_link(video_url + "|Referer=" + site.url + "&User-Agent=" + utils.USER_AGENT)
        return

    utils.notify("Error", "Could not find video URL")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        # Search URL structure: site.url + "search/" + keyword + "/"
        search_url = site.url + "search/?q=" + urllib_parse.quote(keyword)
        List(search_url)
