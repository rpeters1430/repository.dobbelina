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
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "xozilla",
    "[COLOR hotpink]Xozilla[/COLOR]",
    "https://www.xozilla.com/",
    "xozilla.png",
    "xozilla",
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
        "[COLOR hotpink]Categories - TOP RATED[/COLOR]",
        site.url + "categories/",
        "CategoriesTR",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Channels[/COLOR]",
        site.url + "channels/",
        "Channels",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url + "latest-updates/")
    utils.eod()


@site.register()
def List(url):
    try:
        listhtml = utils.getHtml(url, "")
    except Exception as e:
        utils.kodilog("@@@@Cumination: failure in xozilla: " + str(e))
        return None

    soup = utils.parse_html(listhtml)
    video_items = soup.select("a.item")

    for item in video_items:
        try:
            videopage = utils.safe_get_attr(item, "href")
            img = utils.safe_get_attr(item, "thumb", ["data-original", "src"])

            duration_tag = item.select_one(".duration")
            duration = utils.safe_get_text(duration_tag)

            title_tag = item.select_one(".title")
            name = utils.safe_get_text(title_tag)

            if not videopage or not name:
                continue

            if not videopage.startswith("http"):
                videopage = site.url[:-1] + videopage

            name = utils.cleantext(name)
            site.add_download_link(
                name, videopage, "Playvid", img, name, duration=duration
            )
        except Exception as e:
            utils.kodilog("Error parsing video item in xozilla: " + str(e))
            continue

    next_tag = soup.select_one(".next a")
    if next_tag:
        next_url = utils.safe_get_attr(next_tag, "href")
        if next_url and next_url != "#":
            if next_url.startswith("/"):
                next_url = site.url[:-1] + next_url

            # Extract page info for display
            page_num = ""
            lp = ""
            next_link_text = utils.safe_get_text(next_tag)
            if ":" in next_link_text:
                page_num = next_link_text.split(":")[-1]

            last_tag = soup.select_one('.last a, a[title*="Last"]')
            if last_tag:
                last_text = utils.safe_get_text(last_tag)
                if ":" in last_text:
                    lp = "/" + last_text.split(":")[-1]

            site.add_dir(
                "Next Page ({}{})".format(page_num, lp), next_url, "List", site.img_next
            )
        else:
            # Handle async pagination if href is #
            dbi = utils.safe_get_attr(next_tag, "data-block-id")
            dp = utils.safe_get_attr(next_tag, "data-parameters")
            if dbi and dp:
                dp = dp.replace(":", "=").replace(";", "&").replace("+from_albums", "")
                next_url = "{0}?mode=async&function=get_block&block_id={1}&{2}".format(
                    url.split("?mode")[0], dbi, dp
                )
                site.add_dir("Next Page", next_url, "List", site.img_next)

    utils.eod()


@site.register()
def Categories(url):
    try:
        cathtml = utils.getHtml(url, "")
    except Exception as e:
        utils.kodilog("@@@@Cumination: failure in xozilla: " + str(e))
        return None

    soup = utils.parse_html(cathtml)
    categories = []
    # Based on regex: a href="([^"]+)">([^<]+)<span class="rating">
    links = soup.select('a[href*="/categories/"]')
    for link in links:
        if link.select_one(".rating"):
            catpage = utils.safe_get_attr(link, "href")
            name = utils.safe_get_text(link).split("<span")[0].strip()
            if name and catpage:
                categories.append((utils.cleantext(name), catpage))

    for name, catpage in sorted(categories, key=lambda x: x[0].lower()):
        site.add_dir(name, catpage, "List", "")
    utils.eod()


@site.register()
def CategoriesTR(url):
    try:
        cathtml = utils.getHtml(url, "")
    except Exception as e:
        utils.kodilog("@@@@Cumination: failure in xozilla: " + str(e))
        return None

    soup = utils.parse_html(cathtml)
    categories = []
    # Based on regex: "item" href="([^"]+)" title="([^"]+)".+?src="([^"]+)".+?i>([^<]+)videos<
    items = soup.select(".item")
    for item in items:
        link = item if item.name == "a" else item.select_one("a")
        if not link:
            continue

        catpage = utils.safe_get_attr(link, "href")
        name = utils.safe_get_attr(link, "title")

        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src")

        count_tag = item.select_one("i")
        count = utils.safe_get_text(count_tag)

        if name and catpage:
            display_name = (
                utils.cleantext(name) + "[COLOR deeppink] " + count + "[/COLOR]"
            )
            categories.append((display_name, catpage, img))

    for name, catpage, img in sorted(categories, key=lambda x: x[0].lower()):
        site.add_dir(name, catpage, "List", img)
    utils.eod()


@site.register()
def Channels(url):
    try:
        cathtml = utils.getHtml(url, "")
    except Exception as e:
        utils.kodilog("@@@@Cumination: failure in xozilla: " + str(e))
        return None

    soup = utils.parse_html(cathtml)
    channels = []
    # Based on regex: "item" href="([^"]+)" title="([^"]+)".+?src="([^"]+)"
    items = soup.select(".item")
    for item in items:
        link = item if item.name == "a" else item.select_one("a")
        if not link:
            continue

        catpage = utils.safe_get_attr(link, "href")
        name = utils.safe_get_attr(link, "title")

        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src")

        if name and catpage:
            channels.append((utils.cleantext(name), catpage, img))

    for name, catpage, img in sorted(channels, key=lambda x: x[0].lower()):
        site.add_dir(name, catpage, "List", img)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, "")

    srcs = re.compile(
        r"video_(?:alt_|)url:\s*'([^']+)'.+?video_(?:alt_|)url_text:\s*'([^']+)'",
        re.DOTALL | re.IGNORECASE,
    ).findall(videopage)
    sources = {}
    for videourl, quality in srcs:
        if videourl:
            sources[quality] = videourl
    videourl = utils.prefquality(
        sources, sort_by=lambda x: 1081 if x == "4k" else int(x[:-1]), reverse=True
    )
    if videourl:
        vp.progress.update(75, "[CR]Loading video page[CR]")
        vp.play_from_direct_link(videourl)


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "-")
        searchUrl = searchUrl + title + "/"
        List(searchUrl)
