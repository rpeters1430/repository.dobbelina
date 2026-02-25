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
    "pornhoarder",
    "[COLOR hotpink]PornHoarder[/COLOR]",
    "https://pornhoarder.tv/",
    "pornhoarder.png",
    "pornhoarder",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Studios[/COLOR]",
        site.url + "porn-studios/",
        "Studios",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Pornstars[/COLOR]",
        site.url + "porn-stars/",
        "Pornstars",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/?search={0}",
        "Search",
        site.img_search,
    )
    List(site.url + "ajax_search.php", page=1)
    utils.eod()


@site.register()
def List(url, page=1, section=None):
    search = ""
    referer = url
    if "ajax_search.php" in url:
        ajax_url = url
        post_data = {"page": page, "search": search}
        referer = site.url
    else:
        # If it's a search URL or other page, try to use AJAX
        ajax_url = site.url + "ajax_search.php"
        search_match = re.findall(r"search=([^&]+)", url)
        search = urllib_parse.unquote(search_match[0]) if search_match else ""
        
        author_match = re.findall(r"/(?:porn-star|porn-studio)/([^/]+)/", url)
        author = author_match[0] if author_match else "0"
        
        post_data = {"page": page, "search": search}
        if author != "0":
            # We don't have the numeric author ID easily, but the site seems to 
            # use Referer to filter AJAX results when search is empty.
            pass

    headers = {
        "Referer": referer,
        "X-Requested-With": "XMLHttpRequest"
    }
    
    listhtml = utils.postHtml(ajax_url, data=post_data, headers=headers)
    if not listhtml:
        # Fallback to GET if POST failed
        listhtml = utils.getHtml(url, site.url)
        
    soup = utils.parse_html(listhtml)
    items = soup.select(".video, article")
    for item in items:
        link = item.select_one("a.video-link, a[href*='/pornvideo/']")
        if not link:
            continue
            
        videourl = utils.safe_get_attr(link, "href", default="")
        if not videourl:
            continue
            
        videourl = urllib_parse.urljoin(site.url, videourl)
        
        img_tag = item.select_one(".video-image.primary, img")
        img = utils.get_thumbnail(img_tag)
        if img and img.startswith("/"):
            img = urllib_parse.urljoin(site.url, img)
            
        name = utils.cleantext(utils.safe_get_text(item.select_one("h1"), default=""))
        if not name:
            name = utils.cleantext(utils.safe_get_attr(link, "title", default=""))
        if not name:
            h2 = item.select_one("h2")
            name = utils.cleantext(h2.get_text()) if h2 else ""
        if not name:
            name = utils.cleantext(utils.safe_get_text(link))
            
        duration = utils.safe_get_text(item.select_one(".video-length"), default="")
        
        site.add_download_link(
            name, videourl, "Playvid", img, name, duration=duration
        )

    if len(items) >= 20:
        site.add_dir(
            "Next Page...",
            url,
            "List",
            site.img_next,
            page=int(page) + 1
        )

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download=download)
    html = utils.getHtml(url, site.url)
    
    # Extract embed URL from json-ld or iframe
    embed_url = "".join(re.findall(r'"embedUrl":\s*"([^"]+)"', html))
    if not embed_url:
        embed_url = utils.safe_get_attr(utils.parse_html(html).select_one("iframe[src]"), "src", default="")
        
    if not embed_url:
        # Try to find any player.php link
        embed_url = "".join(re.findall(r'https?://pornhoarder\.net/player\.php\?video=[^"\'\s>]+', html))

    if not embed_url:
        vp.progress.close()
        return
        
    if embed_url.startswith("//"):
        embed_url = "https:" + embed_url
        
    vp.play_from_link_to_resolve(embed_url)


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    for item in soup.select(".video.category"):
        link = item.select_one("a.video-link")
        if not link: continue
        
        caturl = utils.safe_get_attr(link, "href", default="")
        caturl = urllib_parse.urljoin(site.url, caturl)
        
        name = utils.cleantext(utils.safe_get_text(item.select_one("h2")))
        img_tag = item.select_one("img")
        img = utils.get_thumbnail(img_tag)
        if img and img.startswith("/"):
            img = urllib_parse.urljoin(site.url, img)
            
        site.add_dir(name, caturl, "List", img)
    utils.eod()


@site.register()
def Studios(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    for item in soup.select(".video.category"):
        link = item.select_one("a.video-link")
        if not link: continue
        
        sturl = utils.safe_get_attr(link, "href", default="")
        sturl = urllib_parse.urljoin(site.url, sturl)
        
        name = utils.cleantext(utils.safe_get_text(item.select_one("h2")))
        site.add_dir(name, sturl, "List", "")
    utils.eod()


@site.register()
def Pornstars(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    for item in soup.select(".video.category"):
        link = item.select_one("a.video-link")
        if not link: continue
        
        psurl = utils.safe_get_attr(link, "href", default="")
        psurl = urllib_parse.urljoin(site.url, psurl)
        
        name = utils.cleantext(utils.safe_get_text(item.select_one("h2")))
        img_tag = item.select_one("img")
        img = utils.get_thumbnail(img_tag)
        if img and img.startswith("/"):
            img = urllib_parse.urljoin(site.url, img)
            
        site.add_dir(name, psurl, "List", img)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = url.format(urllib_parse.quote(keyword))
        List(search_url)
