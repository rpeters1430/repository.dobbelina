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

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "fullporner",
    "[COLOR hotpink]Fullporner[/COLOR]",
    "https://fullporner.org/",
    "fullporner.png",
    "fullporner",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]", site.url, "Categories", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Pornstars[/COLOR]",
        site.url + "porno-actors/page/1/",
        "Actors",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Channels[/COLOR]",
        site.url + "porno-channels/page/1/",
        "Actors",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url + "porn-channels/latest-videos/page/1/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, "")
    soup = utils.parse_html(listhtml)

    video_items = soup.select("article")
    if not video_items:
        return

    for item in video_items:
        try:
            link = item.select_one("a[href]")
            if not link:
                continue

            videopage = utils.safe_get_attr(link, "href")
            name = utils.safe_get_attr(link, "title")

            img_tag = item.select_one("img")
            img = utils.safe_get_attr(img_tag, "poster", ["src"])

            # Look for duration in various places
            duration_tag = item.select_one("i")
            duration = utils.safe_get_text(duration_tag) if duration_tag else ""

            if not videopage or not name:
                continue

            name = utils.cleantext(name)
            site.add_download_link(
                name, videopage, "Playvid", img, name, duration=duration
            )

        except Exception as e:
            utils.kodilog("Error parsing video item: " + str(e))
            continue

    # Handle pagination
    pagination = soup.select_one(".pagination")
    if pagination:
        current = pagination.select_one(".current")
        if current:
            next_link = current.find_next("a")
            if next_link and next_link.get("href"):
                next_url = next_link.get("href")
                page_number = next_url.split("/")[-2] if "/" in next_url else ""
                site.add_dir(
                    "Next Page (" + page_number + ")", next_url, "List", site.img_next
                )

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.play_from_site_link(url, url)


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(searchUrl, "Search")
    else:
        title = keyword.replace(" ", "+")
        searchUrl = searchUrl + title
        List(searchUrl)


@site.register()
def Categories(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    categories = []
    articles = soup.select("article")
    for article in articles:
        try:
            link = article.select_one("a[href]")
            if not link:
                continue

            catpage = utils.safe_get_attr(link, "href")
            if not catpage:
                continue

            img_tag = article.select_one("img")
            img = utils.safe_get_attr(img_tag, "src")

            title_tag = article.select_one(".cat-title")
            name = utils.safe_get_text(title_tag) if title_tag else ""

            if name and catpage:
                name = utils.cleantext(name.strip())
                categories.append((name, catpage + "&filter=latest", img))

        except Exception as e:
            utils.kodilog("Error parsing category: " + str(e))
            continue

    # Sort by name and add directories
    for name, catpage, img in sorted(categories, key=lambda x: x[0].lower()):
        site.add_dir(name, catpage, "List", img)

    utils.eod()


@site.register()
def Actors(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    actors = []
    articles = soup.select("article")
    for article in articles:
        try:
            link = article.select_one("a[href]")
            if not link:
                continue

            catpage = utils.safe_get_attr(link, "href")
            name = utils.safe_get_attr(link, "title")

            img_tag = article.select_one("img")
            img = utils.safe_get_attr(img_tag, "src")

            if name and catpage:
                name = utils.cleantext(name.strip())
                actors.append((name, catpage, img))

        except Exception as e:
            utils.kodilog("Error parsing actor: " + str(e))
            continue

    # Sort by name and add directories
    for name, catpage, img in sorted(actors, key=lambda x: x[0].lower()):
        site.add_dir(name, catpage, "List", img)

    # Handle pagination for actors
    pagination = soup.select_one(".pagination")
    if pagination:
        current = pagination.select_one(".current")
        if current:
            next_link = current.find_next("a")
            if next_link and next_link.get("href"):
                next_url = next_link.get("href")
                page_number = next_url.split("/")[-2] if "/" in next_url else ""
                site.add_dir(
                    "Next Page (" + page_number + ")", next_url, "Actors", site.img_next
                )

    utils.eod()
