"""
Cumination
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

from urllib.parse import quote_plus, urljoin

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "xhuzz",
    "[COLOR hotpink]xHuzz[/COLOR]",
    "https://xhuzz.com/",
    "xhuzz.png",
    "xhuzz",
    category="Video Tubes",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search?q={0}",
        "Search",
        site.img_search,
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    # The home page repeats videos across its carousel and grid sections.
    seen = set()
    for link in soup.select("a[href*='/video/']"):
        href = utils.safe_get_attr(link, "href")
        if not href or href in seen:
            continue
        seen.add(href)
        img = link.select_one("img")
        name = utils.safe_get_attr(img, "alt")
        if not name:
            name = utils.safe_get_attr(link, "aria-label")
            if name.startswith("Watch "):
                name = name[6:]
        if not name:
            continue
        thumb = utils.safe_get_attr(img, "src", ["data-src"])
        site.add_download_link(
            utils.cleantext(name),
            urljoin(site.url, href),
            "Playvid",
            urljoin(site.url, thumb) if thumb else "",
        )

    next_link = soup.select_one("a[aria-label='Next page'][href]")
    if next_link:
        site.add_dir(
            "Next Page", urljoin(url, next_link["href"]), "List", site.img_next
        )
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)

    seen = set()
    for link in soup.select("a[href*='/category/']"):
        href = urljoin(site.url, link.get("href", ""))
        if href in seen:
            continue
        img = link.find("img")
        thumb = utils.safe_get_attr(img, "src", ["data-src"])
        title = utils.safe_get_attr(img, "alt") or link.get_text(strip=True)
        if title:
            seen.add(href)
            site.add_dir(
                utils.cleantext(title),
                href,
                "List",
                urljoin(site.url, thumb) if thumb else site.img_cat,
            )

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    vpage = utils.getHtml(url, site.url)
    soup = utils.parse_html(vpage)

    # The player iframe is filled in by JS from the hoster buttons.
    sources = [
        urljoin(url, b["data-src"])
        for b in soup.select(".source-btn[data-src]")
        if b.get("data-src")
    ]
    if not sources:
        iframe = soup.find("iframe", src=True)
        if iframe:
            sources.append(urljoin(url, iframe["src"]))

    if not sources:
        vp.progress.close()
        utils.notify("No playable stream found", "xHuzz")
        return

    vp.progress.update(60, "[CR]Resolving stream[CR]")
    vp.play_from_link_list(sources)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = url.format(quote_plus(keyword))
        List(search_url)
