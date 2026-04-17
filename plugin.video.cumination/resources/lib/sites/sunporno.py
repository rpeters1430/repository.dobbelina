"""
    Cumination site scraper
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

from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite


site = AdultSite(
    "sunporno",
    "[COLOR yellow]SunPorno[/COLOR]",
    "https://www.sunporno.com/",
    "sunporno.png",
    "sunporno",
    category="Video Tubes",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR yellow]Recent[/COLOR]",
        site.url + "recent/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR yellow]Trending[/COLOR]",
        site.url + "trending/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR yellow]Top Rated[/COLOR]",
        site.url + "top-rated/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR yellow]Search[/COLOR]",
        site.url + "s/{0}/",
        "Search",
        site.img_search,
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    content = soup.select_one(".list-videos")
    if not content:
        content = soup

    items_added = 0
    # On some versions of the site, .item is the a tag itself, on others it's a wrapper.
    for item in content.select(".item"):
        try:
            # Check if the item itself is the link
            if item.name == "a" and "/v/" in item.get("href", ""):
                link = item
            else:
                link = item.select_one('a[href*="/v/"]')
            
            if not link:
                continue

            videopage = utils.safe_get_attr(link, "href")
            if not videopage.startswith("http"):
                videopage = urllib_parse.urljoin(site.url, videopage)

            # Prefer .video-title text over 'title' attribute which often has prefix
            name_tag = item.select_one(".video-title")
            if name_tag:
                name = utils.safe_get_text(name_tag)
            else:
                name = utils.safe_get_attr(link, "title")
            
            if not name:
                continue
            name = utils.cleantext(name)

            img_tag = item.select_one("img")
            # Try data-webp, then data-original, then src
            img = utils.safe_get_attr(img_tag, "data-webp", ["data-original", "src"])
            if img and not img.startswith("http"):
                img = urllib_parse.urljoin(site.url, img)

            duration_tag = item.select_one(".duration")
            duration = utils.safe_get_text(duration_tag)

            site.add_download_link(
                name, videopage, "Playvid", img, name, duration=duration
            )
            items_added += 1
        except Exception as e:
            utils.kodilog("SunPorno parse error: {}".format(e))
            continue

    # Pagination
    pagination = soup.select_one(".pagination")
    if pagination:
        next_link = pagination.select_one(".next a")
        if next_link:
            next_url = utils.safe_get_attr(next_link, "href")
            if next_url:
                if not next_url.startswith("http"):
                    next_url = urllib_parse.urljoin(site.url, next_url)
                
                # Extract page number for label
                parts = next_url.strip("/").split("/")
                np = parts[-1] if parts[-1].isdigit() else ""
                
                label = "Next Page"
                if np:
                    label += " ({})".format(np)
                
                site.add_dir(label, next_url, "List", site.img_next)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    vpage = utils.getHtml(url, site.url)
    if "kt_player" in vpage:
        vp.progress.update(60, "[CR]{0}[CR]".format("kt_player detected"))
        vp.play_from_kt_player(vpage, url)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        # url is 'https://www.sunporno.com/s/{0}/'
        List(url.format(keyword.replace(" ", "-")))
