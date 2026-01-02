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
import requests

site = AdultSite(
    "pornhoarder",
    "[COLOR hotpink]PornHoarder[/COLOR]",
    "https://www.pornhoarder.tv/",
    "pornhoarder.png",
    "pornhoarder",
)

ph_headers = {
    "Origin": site.url[:-1],
    "User-Agent": utils.USER_AGENT,
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": "pornhoarder_settings=0---0---1---0",
}


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Pornstars[/COLOR]",
        site.url + "porn-stars/",
        "Pornstars",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Studios[/COLOR]",
        site.url + "porn-studios/",
        "Studios",
        site.img_cat,
    )
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url, "Search", site.img_search)
    List(site.url + "ajax_search.php")
    utils.eod()


@site.register()
def List(url, page=1, section=None):
    search = "" if url.startswith("https://") else url
    siteurl = section if section else requests.head(site.url, allow_redirects=True).url

    data = Createdata(page, search)
    listhtml = utils.postHtml(
        siteurl + "ajax_search.php", headers=ph_headers, form_data=data
    )
    soup = utils.parse_html(listhtml)

    # Find all article/video links
    links = soup.select("a[href]")
    for link in links:
        try:
            videopage = utils.safe_get_attr(link, "href")
            if not videopage:
                continue

            # Get image
            img_tag = link.select_one("img[data-src], img[src]")
            if not img_tag:
                continue
            img = utils.safe_get_attr(img_tag, "data-src", ["src"])

            # Get video title from h1
            h1_tag = link.select_one("h1")
            if not h1_tag:
                continue
            name = utils.safe_get_text(h1_tag, "").strip()
            name = utils.cleantext(name)
            if not name:
                continue

            # Get duration/length
            length_tag = link.select_one(".length")
            length = utils.safe_get_text(length_tag, "").strip() if length_tag else ""

            if videopage.startswith("/"):
                videopage = siteurl[:-1] + videopage

            site.add_download_link(
                name, videopage, "Playvid", img, name, duration=length
            )
        except Exception as e:
            utils.log("pornhoarder List: Error processing video - {}".format(e))
            continue

    # Pagination
    next_button = soup.select_one(".next .pagination-button[data-page]")
    if next_button:
        page_number = utils.safe_get_attr(next_button, "data-page")
        if page_number:
            site.add_dir(
                "Next Page (" + page_number + ")",
                url,
                "List",
                site.img_next,
                page=int(page_number),
                section=siteurl,
            )
    utils.eod()


@site.register()
def List2(url, page=1):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    # Find all articles with links
    articles = soup.select("article")
    for article in articles:
        try:
            link = article.select_one("a[href]")
            if not link:
                continue

            videopage = utils.safe_get_attr(link, "href")
            if not videopage:
                continue

            # Get image
            img_tag = link.select_one("img[data-src]")
            if not img_tag:
                img_tag = link.select_one("img[src]")
            img = utils.safe_get_attr(img_tag, "data-src", ["src"]) if img_tag else ""

            # Get video title from h1
            h1_tag = link.select_one("h1")
            if not h1_tag:
                continue
            name = utils.safe_get_text(h1_tag, "").strip()
            name = utils.cleantext(name)
            if not name:
                continue

            # Get duration/length
            length_tag = link.select_one(".length")
            length = utils.safe_get_text(length_tag, "").strip() if length_tag else ""

            if videopage.startswith("/"):
                videopage = site.url[:-1] + videopage

            site.add_download_link(
                name, videopage, "Playvid", img, name, duration=length
            )
        except Exception as e:
            utils.log("pornhoarder List2: Error processing video - {}".format(e))
            continue

    # Pagination
    next_link = soup.select_one(".next a[href][data-page]")
    if next_link:
        nextpage = utils.safe_get_attr(next_link, "href")
        page_number = utils.safe_get_attr(next_link, "data-page")
        if nextpage and page_number:
            if nextpage.startswith("/"):
                nextpage = site.url + nextpage
            site.add_dir(
                "Next Page (" + page_number + ")",
                nextpage,
                "List2",
                site.img_next,
                page=int(page_number),
            )
    utils.eod()


def Createdata(page=1, search=""):
    return [
        ("search", search),
        ("sort", "0"),
        ("date", "0"),
        ("servers[]", "21"),
        ("servers[]", "40"),
        ("servers[]", "12"),
        ("servers[]", "35"),
        ("servers[]", "25"),
        ("servers[]", "41"),
        ("servers[]", "46"),
        ("servers[]", "17"),
        ("servers[]", "44"),
        ("servers[]", "42"),
        ("servers[]", "43"),
        ("servers[]", "29"),
        ("author", "0"),
        ("page", page),
    ]


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(
        name, download, regex=r"""<iframe.+?src\s*=\s*["']([^'"]+)"""
    )
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videohtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(videohtml)

    # Get default iframe source
    default_iframe = soup.select_one("iframe[src]")
    if not default_iframe:
        vp.progress.close()
        return
    defaulthost = utils.safe_get_attr(default_iframe, "src")

    # Get default host name from title attribute
    host_link = soup.select_one('[title*="hosted on"]')
    if host_link:
        title = utils.safe_get_attr(host_link, "title")
        # Extract host name from "hosted on XXX" title
        host_match = re.search(r'hosted on ([^"\']+)', title, re.IGNORECASE)
        host = host_match.group(1) if host_match else "Default"
    else:
        host = "Default"

    # Get alternative video sources
    sources = {}
    alt_links = soup.select('a[href][title*="Watch this video on"]')
    for link in alt_links:
        try:
            href = utils.safe_get_attr(link, "href")
            title = utils.safe_get_attr(link, "title")
            # Extract source name from "Watch this video on XXX" title
            source_match = re.search(
                r'Watch this video on ([^"\']+)', title, re.IGNORECASE
            )
            if source_match and href:
                source_name = source_match.group(1)
                full_url = site.url[:-1] + href if href.startswith("/") else href
                sources[source_name] = full_url
        except Exception as e:
            utils.log(
                "pornhoarder Playvid: Error processing alternative source - {}".format(
                    e
                )
            )
            continue

    sources[host] = defaulthost
    videolink = utils.selector("Select video source", sources)
    if videolink:
        if "player.php" not in videolink:
            html = utils.getHtml(videolink)
            # Use regex for iframe extraction from the alternate page
            iframe_match = re.compile(
                'iframe src="([^"]+)"', re.DOTALL | re.IGNORECASE
            ).findall(html)
            if iframe_match:
                videolink = iframe_match[0]
            else:
                vp.progress.close()
                return

        vidhtml = utils.postHtml(videolink, headers=ph_headers, form_data={"play": ""})
        match = re.compile(
            r"""<iframe.+?src\s*=\s*["']([^'"]+)""", re.DOTALL | re.IGNORECASE
        ).findall(vidhtml)
        if match:
            videolink = match[0]
            vp.progress.update(75, "[CR]Loading video page[CR]")
            vp.play_from_link_to_resolve(videolink)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        List(keyword, page=1)


@site.register()
def Categories(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    # Find all articles with category links
    articles = soup.select("article")
    for article in articles:
        try:
            # Find search links (categories use search URLs)
            link = article.select_one('a[href*="/search/"]')
            if not link:
                continue

            href = utils.safe_get_attr(link, "href")
            if not href or "?search=" not in href:
                continue

            # Extract search term from URL
            catpage = href.split("?search=")[-1] if "?search=" in href else ""
            if not catpage:
                continue

            # Get image
            img_tag = article.select_one("img[data-src]")
            if img_tag:
                img = utils.safe_get_attr(img_tag, "data-src", ["src"])
                if img.startswith("/"):
                    img = site.url + img
            else:
                img = ""

            # Get category name from h2
            h2_tag = article.select_one("h2")
            if not h2_tag:
                continue
            name = utils.safe_get_text(h2_tag, "").strip()
            name = utils.cleantext(name)
            if not name:
                continue

            site.add_dir(name, catpage, "List", img)
        except Exception as e:
            utils.log(
                "pornhoarder Categories: Error processing category - {}".format(e)
            )
            continue

    # Pagination
    next_link = soup.select_one(".next a[href]")
    if next_link:
        page_link = utils.safe_get_attr(next_link, "href")
        if page_link:
            # Extract page number from URL
            page_nr_match = re.findall(r"\d+", page_link)
            page_nr = page_nr_match[-1] if page_nr_match else ""
            if page_link.startswith("/"):
                page_link = site.url + page_link
            site.add_dir(
                "Next Page ({})".format(page_nr), page_link, "Categories", site.img_next
            )
    utils.eod()


@site.register()
def Pornstars(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    # Find all articles with pornstar links
    articles = soup.select("article")
    for article in articles:
        try:
            link = article.select_one("a[href]")
            if not link:
                continue

            catpage = utils.safe_get_attr(link, "href")
            if not catpage:
                continue

            # Get image
            img_tag = article.select_one("img[data-src]")
            if img_tag:
                img = utils.safe_get_attr(img_tag, "data-src", ["src"])
                if img.startswith("/"):
                    img = site.url + img
            else:
                img = ""

            # Get pornstar name from h2
            h2_tag = article.select_one("h2")
            if not h2_tag:
                continue
            name = utils.safe_get_text(h2_tag, "").strip()
            name = utils.cleantext(name)

            # Get video count from meta
            meta_tag = article.select_one(".meta")
            videos = utils.safe_get_text(meta_tag, "").strip() if meta_tag else ""

            if not name:
                continue

            if videos:
                name = "{} [COLOR deeppink]{}[/COLOR]".format(name, videos)

            # Build full URL
            if catpage.startswith("/"):
                catpage = site.url + catpage
            if not catpage.endswith("videos/"):
                catpage = catpage + "videos/"

            site.add_dir(name, catpage, "List2", img)
        except Exception as e:
            utils.log("pornhoarder Pornstars: Error processing pornstar - {}".format(e))
            continue

    # Pagination
    next_link = soup.select_one(".next a[href]")
    if next_link:
        page_link = utils.safe_get_attr(next_link, "href")
        if page_link:
            # Extract page number from URL
            page_nr_match = re.findall(r"\d+", page_link)
            page_nr = page_nr_match[-1] if page_nr_match else ""
            if page_link.startswith("/"):
                page_link = site.url + page_link
            site.add_dir(
                "Next Page ({})".format(page_nr), page_link, "Pornstars", site.img_next
            )
    utils.eod()


@site.register()
def Studios(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    # Find all articles with studio links
    articles = soup.select("article")
    for article in articles:
        try:
            link = article.select_one("a[href]")
            if not link:
                continue

            catpage = utils.safe_get_attr(link, "href")
            if not catpage:
                continue

            # Get studio name from h2
            h2_tag = article.select_one("h2")
            if not h2_tag:
                continue
            name = utils.safe_get_text(h2_tag, "").strip()
            name = utils.cleantext(name)

            # Get video count from conunt/count tag
            count_tag = article.select_one(".conunt, .count")
            videos = utils.safe_get_text(count_tag, "").strip() if count_tag else ""

            if not name:
                continue

            if videos:
                name = "{} [COLOR deeppink]{}[/COLOR]".format(name, videos)

            # Build full URL
            if catpage.startswith("/"):
                catpage = site.url + catpage
            if not catpage.endswith("videos/"):
                catpage = catpage + "videos/"

            site.add_dir(name, catpage, "List2", "")
        except Exception as e:
            utils.log("pornhoarder Studios: Error processing studio - {}".format(e))
            continue

    utils.eod()
