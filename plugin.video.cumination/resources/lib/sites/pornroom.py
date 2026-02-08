"""
Cumination
Copyright (C) 2018 Whitecream

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
    "pornroom",
    "[COLOR hotpink]ThePornRoom[/COLOR]",
    "https://thepornroom.com/",
    "pornroom.png",
    "pornroom",
)


@site.register(default_mode=True)
def pornroom_main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "pornroom_cat",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    pornroom_list(site.url + "?filter=latest")


@site.register()
def pornroom_list(url):
    listhtml = utils.getHtml(url)
    if "0 videos found" in listhtml:
        utils.notify("No videos found", "No videos found on this page")
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    video_items = soup.select("[data-post-id]")

    for item in video_items:
        try:
            link = item.select_one("a[href]")
            if not link:
                continue

            video = utils.safe_get_attr(link, "href")
            name = utils.safe_get_attr(link, "title") or utils.safe_get_text(link)

            img_tag = item.select_one("img")
            img = utils.safe_get_attr(img_tag, "poster", ["data-src", "src"])

            duration_tag = item.select_one(".duration")
            duration = utils.safe_get_text(duration_tag)

            if not video or not name:
                continue

            name = utils.cleantext(name)
            site.add_download_link(
                name, video, "pornroom_play", img, name, duration=duration
            )
        except Exception as e:
            utils.kodilog("Error parsing video item in pornroom: " + str(e))
            continue

    # Handle pagination
    pagination = soup.select_one(".pagination")
    if pagination:
        current = pagination.select_one(".current, .active")
        if current:
            # Look for the link immediately after current
            next_link = current.find_next("a")
            if next_link:
                next_url = utils.safe_get_attr(next_link, "href")
                if next_url:
                    page_number = next_url.split("/")[-2] if "/" in next_url else "Next"
                    site.add_dir(
                        "Next Page (" + page_number + ")",
                        next_url,
                        "pornroom_list",
                        site.img_next,
                    )

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        searchUrl = url + keyword.replace(" ", "+")
        pornroom_list(searchUrl)


@site.register()
def pornroom_cat(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    categories = []
    # Based on regex: class="thumb" href="([^"]+)" title="([^"]+)".+?data-src="([^"]+)".+?class="video-datas">([^<]+)<
    cat_items = soup.select(".thumb")
    for link in cat_items:
        try:
            catpage = utils.safe_get_attr(link, "href")
            name = utils.safe_get_attr(link, "title")

            img_tag = link.select_one("img")
            img = utils.safe_get_attr(img_tag, "data-src", ["src"])

            # Video count is often in a sibling or nested element
            parent = link.parent
            count_tag = parent.select_one(".video-datas") if parent else None
            videos = utils.safe_get_text(count_tag)

            if name and catpage:
                name = utils.cleantext(name.strip())
                if videos:
                    name += " [COLOR hotpink](" + videos.strip() + ")[/COLOR]"
                categories.append((name, catpage + "?filter=latest", img))
        except Exception as e:
            utils.kodilog("Error parsing category in pornroom: " + str(e))
            continue

    for name, caturl, img in sorted(categories, key=lambda x: x[0].lower()):
        site.add_dir(name, caturl, "pornroom_list", img)
    utils.eod()


@site.register()
def pornroom_play(url, name, download=None):
    vp = utils.VideoPlayer(
        name, download=download, regex=r'<iframe.+?src="([^"]+)"', direct_regex=None
    )
    vp.play_from_site_link(url)
