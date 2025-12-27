"""
Cumination
Copyright (C) 2021 Team Cumination

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
import json
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "sextb", "[COLOR hotpink]SEXTB[/COLOR]", "https://sextb.net/", "sextb.png", "sextb"
)
enames = {
    "VV": "VideoVard",
    "TV": "TurboVIPlay",
    "TB": "TurboVIPlay",
    "JP": "JAVPoll",
    "ST": "StreamTape",
    "DD": "DoodStream",
    "VS": "Voe",
    "SW": "StreamWish",
    "NJ": "NinjaStream",
    "NT": "Netu",
    "FL": "FileLions",
    "US": "UPN",
    "VG": "Vidguard",
}


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Amateur[/COLOR]",
        site.url + "amateur/pg-1",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Censored[/COLOR]",
        site.url + "censored/pg-1",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Uncensored Leaked[/COLOR]",
        site.url + "genre/uncensored-leaked/pg-1",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Reducing Mosaic[/COLOR]",
        site.url + "genre/reducing-mosaic/pg-1",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Subtitle[/COLOR]",
        site.url + "subtitle/pg-1",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Genres[/COLOR]", site.url + "genres", "Categories", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Actress[/COLOR]",
        site.url + "list-actress/pg-1",
        "Actress",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Studios[/COLOR]",
        site.url + "list-studio",
        "Studios",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url + "uncensored/pg-1")
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)

    if "No Video were found that matched your search query" in html or len(html) < 10:
        utils.eod()
        return

    soup = utils.parse_html(html)
    items = soup.select(".tray-item")

    for item in items:
        link = item.select_one("a")
        if not link:
            continue

        videopage = utils.safe_get_attr(link, "href")
        if not videopage:
            continue

        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])

        title_tag = item.select_one(".title")
        name = utils.safe_get_text(title_tag, "")

        time_tag = item.select_one(".time")
        duration = utils.safe_get_text(time_tag, "")

        if name:
            site.add_download_link(
                name, videopage, "Playvid", img, name, duration=duration
            )

    # Pagination
    next_link = soup.find("a", string="Next")
    if next_link:
        np = utils.safe_get_attr(next_link, "href")
        if np:
            if np.startswith("/"):
                np = urllib_parse.urljoin(site.url, np)

            # Get current page number
            current_page = soup.select_one(".current")
            pgtxt = utils.safe_get_text(current_page, "1")
            site.add_dir(
                "Next Page... (Currently in Page {0})".format(pgtxt),
                np,
                "List",
                site.img_next,
            )

    utils.eod()


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)

    # Find all fa-folder icons and get their parent links
    folder_icons = soup.find_all("i", class_="fa-folder")
    for icon in folder_icons:
        # Find the link containing this icon
        link = icon.find_parent("a")
        if not link:
            continue

        caturl = utils.safe_get_attr(link, "href")
        name = utils.safe_get_attr(link, "title")

        if not caturl or not name:
            continue

        # Get count from the text after the link
        count = ""
        # Look for text like "(123)" following the link
        next_text = link.find_next_sibling(string=re.compile(r"\(\d+\)"))
        if next_text:
            count_match = re.search(r"\((\d+)\)", next_text)
            if count_match:
                count = count_match.group(1)

        # Clean up name
        name = name.replace("Genre ", "").replace("Studio ", "")
        if count:
            name = name + " [COLOR hotpink](" + str(count) + ")[/COLOR]"

        if caturl.startswith("/"):
            caturl = urllib_parse.urljoin(site.url, caturl)

        site.add_dir(name, caturl, "List", "")

    utils.eod()


@site.register()
def Studios(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)

    items = soup.select(".tray-item.tray")
    for item in items:
        link = item.select_one("a")
        if not link:
            continue

        caturl = utils.safe_get_attr(link, "href")
        if not caturl:
            continue

        # Get name from text after icon
        icon = item.select_one("i")
        name = ""
        if icon and icon.next_sibling:
            name = utils.safe_get_text(icon.next_sibling, "").strip()

        # Get total count
        total_tag = item.select_one(".total")
        count = utils.safe_get_text(total_tag, "")

        if name:
            display_name = (
                name + " [COLOR hotpink]" + count + "[/COLOR]" if count else name
            )
            if caturl.startswith("/"):
                caturl = urllib_parse.urljoin(site.url, caturl)
            site.add_dir(display_name, caturl, "List", "")

    utils.eod()


@site.register()
def Actress(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)

    items = soup.select(".tray-item-actress")
    for item in items:
        link = item.select_one("a")
        if not link:
            continue

        caturl = utils.safe_get_attr(link, "href")
        if not caturl:
            continue

        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-src", ["src"])

        name_tag = item.select_one(".actress-title")
        name = utils.safe_get_text(name_tag, "")

        if name:
            if caturl.startswith("/"):
                caturl = urllib_parse.urljoin(site.url, caturl)
            site.add_dir(name, caturl, "List", img)

    # Pagination
    next_link = soup.find("a", string="Next")
    if next_link:
        np = utils.safe_get_attr(next_link, "href")
        if np:
            if np.startswith("/"):
                np = urllib_parse.urljoin(site.url, np)

            # Get current page number
            current_page = soup.select_one(".current")
            pgtxt = utils.safe_get_text(current_page, "1")
            site.add_dir(
                "Next Page... (Currently in Page {0})".format(pgtxt),
                np,
                "Actress",
                site.img_next,
            )

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}".format(url, keyword.replace(" ", "-"))
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    if url.startswith("/"):
        url = urllib_parse.urljoin(site.url, url)
    video_page = utils.getHtml(url, site.url)
    videourl = ""
    ajaxurl = "https://sextb.net/ajax/player"
    embeds = re.compile(
        r'class="btn-player.+?data-source="([^"]+).+?data-id="([^"]+).+?/i>\s*([^<]+)',
        re.DOTALL | re.IGNORECASE,
    ).findall(video_page)
    sources = {}
    for vid, embed, hoster in embeds:
        if "VIP" not in hoster:
            option = ""
            if "#" in hoster:
                hoster, option = hoster.split(" ")
            sources.update(
                {
                    (enames[hoster.strip()] + option)
                    if hoster.strip() in enames
                    else (hoster + option): vid + "$$" + embed
                }
            )
    source = utils.selector("Select Hoster", sources)
    if source:
        filmid, episode = source.split("$$")
        formdata = {"filmId": filmid, "episode": episode}
        player = json.loads(
            utils.postHtml(ajaxurl, form_data=formdata, headers={"Referer": site.url})
        ).get("player")
        videourl = re.findall(r'src="([^?"]+)', player)[0] + "$$" + site.url

    if not videourl:
        vp.progress.close()
        return

    vp.play_from_link_to_resolve(videourl)
