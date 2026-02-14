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
import base64
from six.moves import urllib_error
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.decrypters.kvsplayer import kvs_decode

progress = utils.progress

site = AdultSite(
    "netflixporno",
    "[COLOR hotpink]NetflixPorno[/COLOR]",
    "https://netflixporno.net/",
    "netflixporno.png",
    "netflixporno",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]XXX Scenes[/COLOR]", site.url + "scenes/", "List", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Parody Movies[/COLOR]",
        site.url + "adult/genre/parodies/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Studios[/COLOR]",
        site.url + "adult/genre/parodies/",
        "Studios",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "adult/genre/parodies/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url + "adult")
    utils.eod()


@site.register()
def List(url):
    try:
        listhtml = utils.getHtml(url, site.url)
    except urllib_error.URLError as e:
        utils.notify(e)
        return
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    video_items = soup.select("article")

    for item in video_items:
        link = item.select_one("a[href]")
        if not link:
            continue

        videopage = utils.safe_get_attr(link, "href")
        videopage = utils.fix_url(videopage, site.url)
        if not videopage:
            continue

        title_tag = item.select_one(".Title, .title, .entry-title, h2, h3")
        title = (
            utils.safe_get_text(title_tag)
            or utils.safe_get_attr(link, "title")
            or utils.safe_get_text(link)
        )
        title = utils.cleantext(title)
        if not title:
            continue

        img_tag = item.select_one("img")
        img = utils.get_thumbnail(img_tag)
        img = utils.fix_url(img, site.url)

        site.add_download_link(title, videopage, "Playvid", img, title)

    _add_next_page(soup)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "+")
        searchUrl = searchUrl + title
        List(searchUrl)


@site.register()
def Categories(url):
    try:
        cathtml = utils.getHtml(url, site.url)
    except urllib_error.URLError as e:
        utils.notify(e)
        return
    if not cathtml:
        utils.eod()
        return

    soup = utils.parse_html(cathtml)
    seen = set()
    for link in soup.select('li[class*="cat-item"] a[href]'):
        catpage = utils.safe_get_attr(link, "href")
        catpage = utils.fix_url(catpage, site.url)
        name = utils.cleantext(utils.safe_get_text(link))
        if not catpage or not name:
            continue

        key = (catpage, name.lower())
        if key in seen:
            continue
        seen.add(key)

        site.add_dir(name, catpage, "List", site.img_cat)
    utils.eod()


@site.register()
def Studios(url):
    try:
        studhtml = utils.getHtml(url, site.url)
    except urllib_error.URLError as e:
        utils.notify(e)
        return
    if not studhtml:
        utils.eod()
        return

    soup = utils.parse_html(studhtml)
    seen = set()

    for link in soup.select('li[class*="director"] a[href]'):
        studpage = utils.safe_get_attr(link, "href")
        studpage = utils.fix_url(studpage, site.url)
        name = utils.cleantext(
            utils.safe_get_text(link) or utils.safe_get_attr(link, "title")
        )
        if not studpage or not name:
            continue

        key = (studpage, name.lower())
        if key in seen:
            continue
        seen.add(key)

        site.add_dir(name, studpage, "List", site.img_cat)
    utils.eod()


def url_decode(str):
    if "/goto/" not in str:
        result = str
    else:
        try:
            result = url_decode(base64.b64decode(re.search("/goto/(.+)", str).group(1)))
        except Exception as e:
            utils.kodilog("@@@@Cumination: failure in netflixporno: " + str(e))
            result = str
    return result


@site.register()
def Playvid(url, name, download=None):
    links = {}
    videourl = None
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    try:
        html = utils.getHtml(url, site.url)
    except urllib_error.URLError as e:
        utils.notify(e)
        return
    srcs = re.compile(
        r'<a\s*title="([^"]+)"\s*href="([^"]+)"', re.DOTALL | re.IGNORECASE
    ).findall(html)
    for title, src in srcs:
        title = utils.cleantext(title)
        title = title.split(" on ")[-1]
        src = src.split("?link=")[-1]
        if "/goto/" in src:
            src = url_decode(src)
        if "mangovideo" in src:
            html = utils.getHtml(src, url)
            if "=" in src:
                src = src.split("=")[-1]
            murl = re.compile(
                r"video_url:\s*'([^']+)'", re.DOTALL | re.IGNORECASE
            ).findall(html)
            if murl:
                if murl[0].startswith("function/"):
                    license = re.findall(r"license_code:\s*'([^']+)", html)[0]
                    murl = kvs_decode(murl[0], license)
            else:
                murl = re.compile(
                    r"action=[^=]+=([^\?]+)/\?download", re.DOTALL | re.IGNORECASE
                ).findall(html)
                if murl:
                    murl = murl[0]
            if murl:
                links[title] = murl
        elif vp.resolveurl.HostedMediaFile(src).valid_url():
            links[title] = src
    if links:
        videourl = utils.selector("Select server", links, setting_valid=False)
    if not videourl:
        vp.progress.close()
        utils.notify("Oh Oh", "No Playable Videos found")
        return
    vp.progress.update(90, "[CR]Loading video page[CR]")
    if "mango" in videourl:
        vp.play_from_direct_link(videourl)
    else:
        vp.play_from_link_to_resolve(videourl)


def _add_next_page(soup):
    next_link = soup.select_one("a.next.page-numbers[href]")
    if not next_link:
        return

    next_url = utils.safe_get_attr(next_link, "href")
    next_url = utils.fix_url(next_url.replace("&#038;", "&"), site.url)
    if not next_url:
        return

    current_page = ""
    last_page = ""

    for pager in soup.select(".page-numbers"):
        text = utils.safe_get_text(pager)
        classes = pager.get("class", [])
        if "current" in classes and text:
            current_page = text
        if pager.name == "a" and text and text.isdigit():
            last_page = text

    if not last_page:
        last_page = current_page

    label = "Next Page..."
    if current_page or last_page:
        label = "Next Page... (Currently in Page {0} of {1})".format(
            current_page or "?", last_page or "?"
        )

    site.add_dir(label, next_url, "List", site.img_next)
