"""
Cumination
Copyright (C) 2020 Whitecream

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
    "erome",
    "[COLOR hotpink]Erome[/COLOR]",
    "https://www.erome.com/",
    "erome.png",
    "erome",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search?o=new&q=",
        "Search",
        site.img_search,
    )
    List(site.url + "explore/new")


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    # Find all album divs
    albums = soup.select('.album, div[id*="album-"]')
    for album in albums:
        # Get thumbnail image
        img_tag = album.select_one("img[data-src], img.album-thumbnail")
        if not img_tag:
            continue
        img = utils.safe_get_attr(img_tag, "data-src") or utils.safe_get_attr(
            img_tag, "src"
        )
        if img:
            img += "|Referer={0}".format(site.url)

        # Get album title and URL
        title_link = album.select_one("a.album-title")
        if not title_link:
            continue
        iurl = utils.safe_get_attr(title_link, "href")
        name = utils.safe_get_text(title_link)
        if not iurl or not name:
            continue
        name = utils.cleantext(name)

        # Check for images and videos count
        pics = False
        vids = False
        album_images = album.select_one(".album-images")
        if album_images:
            items_text = utils.safe_get_text(album_images)
            # Extract number from text like "54" or similar
            items_match = re.search(r"\d+", items_text)
            if items_match:
                items = items_match.group(0)
                name += "[COLOR orange][I] {0} pics[/I][/COLOR]".format(items)
                pics = True

        album_videos = album.select_one(".album-videos")
        if album_videos:
            items_text = utils.safe_get_text(album_videos)
            items_match = re.search(r"\d+", items_text)
            if items_match:
                items = items_match.group(0)
                name += "[COLOR hotpink][I] {0} vids[/I][/COLOR]".format(items)
                vids = True

        # Add directory based on content type
        if pics and vids:
            site.add_dir(name, iurl, "List2", img, desc=name, section="both")
        elif pics:
            site.add_dir(name, iurl, "List2", img, desc=name, section="pics")
        elif vids:
            site.add_dir(name, iurl, "List2", img, desc=name, section="vids")

    # Handle pagination
    next_link = soup.select_one('a[rel="next"]')
    if next_link:
        nurl = utils.safe_get_attr(next_link, "href")
        if nurl:
            nurl = urllib_parse.urljoin(url, nurl).replace("&amp;", "&")

            # Find current and last page numbers
            currpg = "1"
            lastpg = "1"

            # Current page is in .active span or li.active
            active_page = soup.select_one(".pagination .active, .pagination li.active")
            if active_page:
                currpg_text = utils.safe_get_text(active_page)
                currpg_match = re.search(r"\d+", currpg_text)
                if currpg_match:
                    currpg = currpg_match.group(0)

            # Last page is the highest number before the next link
            pagination = soup.select_one(".pagination")
            if pagination:
                page_links = pagination.select("a")
                page_numbers = []
                for link in page_links:
                    link_text = utils.safe_get_text(link)
                    page_match = re.search(r"\d+", link_text)
                    if page_match:
                        page_numbers.append(int(page_match.group(0)))
                if page_numbers:
                    lastpg = str(max(page_numbers))

            site.add_dir(
                "Next Page... (Currently in Page {0} of {1})".format(currpg, lastpg),
                nurl,
                "List",
                site.img_next,
            )

    utils.eod()


@site.register()
def List2(url, section):
    if section == "both":
        site.add_dir("Photos", url, "List2", "", section="pics")
        site.add_dir("Videos", url, "List2", "", section="vids")
    else:
        listhtml = utils.getHtml(url, site.url)
        items = listhtml.split('<div class="media-group')
        if len(items) > 1:
            items.pop(0)
            itemcount = 0
            for item in items:
                item = item.split('class="clearfix"')[0]
                if 'class="video"' in item and section == "vids":
                    itemcount += 1
                    img, surl, hd, duration = re.findall(
                        r"""poster="([^"]+).+?source\s*src="([^"]+).+?label='([^']+).+?class="duration"\s*>([^<]+)""",
                        item,
                        re.DOTALL,
                    )[0]
                    img += "|Referer={0}".format(site.url)
                    surl += "|Referer={0}".format(site.url)
                    site.add_download_link(
                        "Video {0}".format(itemcount),
                        surl,
                        "Playvid",
                        img,
                        duration=duration,
                        quality=hd,
                    )
                elif 'class="video"' not in item and section == "pics":
                    img = re.search(
                        r'class="img-front(?:\s*lasyload)?"\s*(?:data-)?src="([^"]+)',
                        item,
                        re.DOTALL,
                    )
                    if img:
                        itemcount += 1
                        img = img.group(1) + "|Referer={0}".format(site.url)
                        site.add_img_link("Photo {0}".format(itemcount), img, "Showpic")

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "+")
        url += title
        List(url)


@site.register()
def Showpic(url, name):
    utils.showimage(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.play_from_direct_link(url)
