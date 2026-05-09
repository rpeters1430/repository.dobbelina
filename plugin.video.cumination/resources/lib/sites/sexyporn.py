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

import re
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "sexyporn",
    "[COLOR hotpink]SexyPorn[/COLOR]",
    "https://www.sexyporn.tv/",
    "sexyporn.png",
    "sexyporn",
    category="Video Tubes",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Popular[/COLOR]",
        site.url + "best/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Newest[/COLOR]",
        site.url + "recent/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Pornstars[/COLOR]",
        site.url + "actors/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Genres[/COLOR]",
        site.url + "tags/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/",
        "Search",
        site.img_search,
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    if not soup:
        utils.eod()
        return

    # Video items are in div elements with data-liz attribute (obfuscated class names)
    items = soup.select("div[data-liz]")

    for item in items:
        link = item.select_one("a[href]")
        if not link:
            continue

        videopage = urllib_parse.urljoin(
            site.url, utils.safe_get_attr(link, "href", default="")
        )
        
        # Extract name from slug or title attribute
        name = utils.safe_get_attr(link, "title")
        if not name:
            slug = videopage.rstrip("/").split("/")[-1]
            # remove leading ID part if present (e.g. 88813172-)
            name = re.sub(r"^\d+-", "", slug).replace("-", " ").title()
            
        if not videopage or not name:
            continue

        img_tag = item.select_one("img")
        thumb = utils.safe_get_attr(img_tag, "data-src", ["src"])
        if thumb and not thumb.startswith("http"):
            thumb = urllib_parse.urljoin(site.url, thumb)
            
        duration = utils.safe_get_text(item.select_one(".jenifer"), default="")

        site.add_download_link(
            name, videopage, "Playvid", thumb, name, duration=duration
        )

    pagination = soup.select_one("#paginator")
    if pagination:
        next_link = pagination.select_one("li.next.page a")
        if next_link:
            next_url = urllib_parse.urljoin(
                url, utils.safe_get_attr(next_link, "href", default="")
            )
            site.add_dir("Next Page", next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    if not soup:
        utils.eod()
        return

    # Look for category containers
    for container in soup.select(".maryanne, .category-list-container li"):
        link = container if container.name == "a" else container.select_one("a[href]")
        if not link:
            continue
            
        caturl = urllib_parse.urljoin(
            site.url, utils.safe_get_attr(link, "href", default="")
        )
        
        name_tag = container.select_one(".becky") or link
        name = utils.cleantext(utils.safe_get_text(name_tag, default=""))
        
        if not caturl or not name:
            continue
            
        img_tag = container.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])
        if img and not img.startswith("http"):
            img = urllib_parse.urljoin(site.url, img)
            
        site.add_dir(name, caturl, "List", img)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        # Site uses POST for search but we can try GET if supported, 
        # otherwise we'd need to update AdultSite to support POST in search
        query = keyword.replace(" ", "+")
        # Most WP sites support /?s=query
        search_url = urllib_parse.urljoin(site.url, f"?s={query}")
        List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videohtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(videohtml)

    if soup:
        source = soup.select_one("video source[src]")
        if source:
            videourl = utils.safe_get_attr(source, "src", default="")
            if videourl:
                vp.play_from_direct_link(f"{videourl}|referer={site.url}")
                return

        iframe = soup.select_one("iframe[src]")
        if iframe:
            iframe_url = utils.safe_get_attr(iframe, "src", default="")
            if iframe_url:
                if iframe_url.startswith("//"):
                    iframe_url = "https:" + iframe_url
                vp.play_from_link_to_resolve(iframe_url)
                return

    # Fallback to regex for direct sources in script
    match = re.search(r'["\']?file["\']?\s*[:=]\s*["\']([^"\']+\.mp4[^"\']*)["\']', videohtml)
    if match:
        vp.play_from_direct_link(match.group(1) + "|referer=" + site.url)
        return

    vp.play_from_link_to_resolve(url)
