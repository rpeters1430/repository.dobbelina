"""
Cumination
Copyright (C) 2024 Team Cumination

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

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "ask4porn",
    "[COLOR orange]Ask4Porn[/COLOR]",
    "https://ask4porn.cc/",
    "ask4porn.png",
    "ask4porn",
)


@site.register(default_mode=True)
def Main(url):
    site.add_dir("Newest", site.url + "videos/?filter=latest", "List", "")
    site.add_dir("Best", site.url + "videos/?filter=popular", "List", "")
    site.add_dir("Most Viewed", site.url + "videos/?filter=most-viewed", "List", "")
    site.add_dir("Longest", site.url + "videos/?filter=longest", "List", "")
    site.add_dir("Random", site.url + "videos/?filter=random", "List", "")
    site.add_dir("Studios", site.url + "categories/", "Studios", "")
    site.add_dir("Categories", site.url + "tags/", "Categories", "")
    site.add_dir("Girls", site.url + "actors-1/", "Girls", "")
    site.add_dir("Search", site.url, "Search", site.img_search)
    utils.eod()


@site.register()
def List(url):
    html, used_fs = utils.get_html_with_cloudflare_retry(url)
    soup = utils.parse_html(html)

    selectors = {
        "items": "article.thumb-block",
        "url": {"selector": "a", "attr": "href"},
        "title": {"selector": "span.title", "text": True},
        "thumbnail": {"selector": "img", "attr": "src"},
        "duration": {"selector": "span.duration", "text": True},
        "pagination": {
            "selector": "div.pagination a",
            "text_matches": ["next"],
            "attr": "href",
        },
    }

    utils.soup_videos_list(site, soup, selectors)
    utils.eod()


@site.register()
def Studios(url):
    html, _ = utils.get_html_with_cloudflare_retry(url)
    soup = utils.parse_html(html)
    
    items = soup.select(".categories-list .thumb-block")
    for item in items:
        name = utils.safe_get_text(item.select_one(".cat-title"))
        href = utils.safe_get_attr(item.select_one("a"), "href")
        img = utils.get_thumbnail(item.select_one("img"))
        
        if name and href:
            site.add_dir(name, urllib_parse.urljoin(site.url, href), "List", img)
            
    utils.eod()


@site.register()
def Categories(url):
    html, _ = utils.get_html_with_cloudflare_retry(url)
    soup = utils.parse_html(html)
    
    items = soup.select(".tags-letter-block .tag-item a")
    for item in items:
        name = utils.safe_get_text(item)
        href = utils.safe_get_attr(item, "href")
        if name and href:
            site.add_dir(name, urllib_parse.urljoin(site.url, href), "List", "")
            
    utils.eod()


@site.register()
def Girls(url):
    html, _ = utils.get_html_with_cloudflare_retry(url)
    soup = utils.parse_html(html)
    
    items = soup.select(".actors-list .thumb-block")
    for item in items:
        name = utils.safe_get_text(item.select_one(".cat-title"))
        href = utils.safe_get_attr(item.select_one("a"), "href")
        img = utils.get_thumbnail(item.select_one("img"))
        
        if name and href:
            site.add_dir(name, urllib_parse.urljoin(site.url, href), "List", img)
            
    # Pagination
    next_el = soup.select_one("div.pagination a:-soup-contains('Next')")
    if next_el:
        next_url = utils.safe_get_attr(next_el, "href")
        site.add_dir("Next Page", urllib_parse.urljoin(site.url, next_url), "Girls", site.img_next)
        
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download, IA_check="skip")
    html, _ = utils.get_html_with_cloudflare_retry(url)
    
    # Try direct link parsing first (includes hornyhill iframe detection)
    vp.play_from_html(html, url)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = site.url + "?s=" + urllib_parse.quote(keyword)
        List(search_url)
