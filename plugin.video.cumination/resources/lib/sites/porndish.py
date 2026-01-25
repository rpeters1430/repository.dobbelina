"""
Ultimate Whitecream
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

site = AdultSite(
    "porndish",
    "[COLOR hotpink]Porndish[/COLOR]",
    "https://www.porndish.com/",
    "porndish.png",
    "porndish",
)


@site.register(default_mode=True)
def Main():
    List(site.url + "page/1/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, "")
    soup = utils.parse_html(listhtml)

    # Handle first page differently - split at "More Porn Videos"
    if "/page/1/" in url:
        # Look for "New Porn Videos" section
        new_videos_section = None
        headings = soup.find_all(text=lambda text: text and "New Porn Videos" in text)
        if headings:
            for heading in headings:
                parent = heading.parent
                if parent:
                    # Find the next sibling or find "More Porn Videos"
                    next_element = parent.find_next()
                    while next_element:
                        if "More Porn Videos" in next_element.get_text():
                            break
                        new_videos_section = next_element
                        next_element = next_element.find_next()

        if new_videos_section:
            # Parse videos from the new videos section
            video_links = new_videos_section.find_all("a[title][href]")
            for link in video_links:
                try:
                    name = utils.safe_get_attr(link, "title")
                    videopage = utils.safe_get_attr(link, "href")
                    img_tag = link.find("img") or link.find_next("img")
                    img = utils.safe_get_attr(img_tag, "data-src") if img_tag else ""

                    if name and videopage:
                        name = utils.cleantext(name)
                        site.add_download_link(name, videopage, "Playvid", img, name)

                except Exception as e:
                    utils.kodilog("Error parsing new video: " + str(e))
                    continue

    # Look for "More Porn Videos" section
    more_videos_section = None
    headings = soup.find_all(text=lambda text: text and "More Porn Videos" in text)
    if headings:
        for heading in headings:
            parent = heading.parent
            if parent:
                # Find the next elements until "g1-pagination-end"
                next_element = parent.find_next()
                while next_element:
                    if (
                        "g1-pagination-end" in next_element.get_text()
                        or next_element.get("class")
                        and 'pagination' in str(next_element.get("class"))
                    ):
                        break
                    if more_videos_section is None:
                        more_videos_section = next_element
                    else:
                        # Append to existing section
                        more_videos_section.append(next_element)
                    next_element = next_element.find_next()

    if more_videos_section:
        # Parse videos from the more videos section
        video_links = more_videos_section.find_all("a[title][href]")
        for link in video_links:
            try:
                name = utils.safe_get_attr(link, "title")
                videopage = utils.safe_get_attr(link, "href")
                img_tag = link.find("img") or link.find_next("img")
                img = utils.safe_get_attr(img_tag, "data-src") if img_tag else ""

                if name and videopage:
                    name = utils.cleantext(name)
                    site.add_download_link(name, videopage, "Playvid", img, name)

            except Exception as e:
                utils.kodilog("Error parsing video: " + str(e))
                continue

    # Handle pagination
    next_link = soup.select_one('a[rel="next"]')
    if next_link and next_link.get("href"):
        site.add_dir("Next Page", next_link.get("href"), "List", site.img_next)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download, direct_regex=None)
    vp.play_from_site_link(url, url)
