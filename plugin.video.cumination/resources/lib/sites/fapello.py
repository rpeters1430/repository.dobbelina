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

import re
from urllib.parse import quote, urljoin

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "fapello",
    "[COLOR hotpink]Fapello[/COLOR]",
    "https://fapello.com/",
    "fapello.png",
    "fapello",
    category="Amateur & Social",
    requires_flaresolverr=True,
)

POPULAR_PERIODS = (
    ("Last Hour", "last_hour"),
    ("Last 12 Hours", "twelve_hours"),
    ("Today", "day"),
    ("This Week", "week"),
    ("This Month", "month"),
    ("All Time", "all_time"),
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Popular Videos[/COLOR]",
        site.url + "popular_videos/",
        "Popular",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search Models[/COLOR]",
        site.url + "search/{0}/",
        "Search",
        site.img_search,
    )
    List(site.url + "videos/")
    utils.eod()


@site.register()
def Popular(url):
    for label, slug in POPULAR_PERIODS:
        site.add_dir(label, "{}{}/".format(url, slug), "List", site.img_cat)
    utils.eod()


def _add_next_page(soup, current_url, mode):
    next_link = soup.select_one("#next_page a[href]")
    if next_link:
        site.add_dir(
            "Next Page", urljoin(current_url, next_link["href"]), mode, site.img_next
        )


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    # Cards have no title of their own: name them after the model and post
    # number. Cards without a /video/ link are sponsored profiles.
    seen = set()
    for card in soup.select("div.uk-transition-toggle"):
        link = card.select_one("a[href*='/video/']")
        href = utils.safe_get_attr(link, "href")
        if not href or href in seen:
            continue
        seen.add(href)
        name = utils.safe_get_text(card.select_one(".custom-overly1 a"))
        post = utils.safe_get_attr(card.select_one("a.tag-corner-link"), "href")
        post_id = re.search(r"/(\d+)/?$", post)
        if post_id:
            name = "{} #{}".format(name, post_id.group(1)).strip()
        if not name:
            continue
        thumb = utils.safe_get_attr(link.select_one("img"), "src", ["data-src"])
        site.add_download_link(
            utils.cleantext(name), urljoin(site.url, href), "Playvid", thumb
        )

    _add_next_page(soup, url, "List")
    utils.eod()


@site.register()
def Models(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    seen = set()
    for card in soup.select("#content div.uk-transition-toggle"):
        link = card.select_one(".custom-overly1 a[href]")
        href = utils.safe_get_attr(link, "href")
        if not href or not href.startswith(site.url) or href in seen:
            continue
        seen.add(href)
        name = utils.safe_get_text(link)
        if not name:
            continue
        thumb = utils.safe_get_attr(card.select_one("img"), "src", ["data-src"])
        site.add_dir(utils.cleantext(name), href, "Model", thumb or site.img_cat)

    _add_next_page(soup, url, "Models")
    utils.eod()


@site.register()
def Model(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    model = utils.safe_get_text(soup.select_one("h2")) or "Video"
    # Model pages mix photos and videos; only video posts carry a play icon.
    for link in soup.select("#content a[href]"):
        if not link.select_one("img[src*='icon-play']"):
            continue
        post_id = re.search(r"/(\d+)/?$", link["href"])
        if not post_id:
            continue
        thumb = utils.safe_get_attr(link.select_one("img"), "src", ["data-src"])
        site.add_download_link(
            utils.cleantext("{} #{}".format(model, post_id.group(1))),
            urljoin(site.url, link["href"]),
            "Playvid",
            thumb,
        )

    _add_next_page(soup, url, "Model")
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    vpage = utils.getHtml(url, site.url)
    soup = utils.parse_html(vpage)

    # /video/ pages are a swipe feed whose first entry is the requested clip.
    video_url = utils.safe_get_attr(
        soup.select_one("meta[property='og:video']"), "content"
    ) or utils.safe_get_attr(soup.select_one("video source[src], video[src]"), "src")
    if not video_url:
        match = re.search(r'"video_url"\s*:\s*"([^"]+)"', vpage)
        if match:
            video_url = match.group(1).replace("\\/", "/")

    if video_url:
        vp.progress.update(75, "[CR]Playing video[CR]")
        vp.play_from_direct_link(
            "{}|Referer={}".format(urljoin(url, video_url), site.url)
        )
    else:
        vp.progress.close()
        utils.notify("No playable stream found", "Fapello")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        # The site only searches model names; spaces are dashes in its URLs.
        Models(url.format(quote(keyword.strip().replace(" ", "-"))))
