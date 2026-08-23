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

from __future__ import annotations

from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "pornyteen",
    "[COLOR hotpink]Pornyteen[/COLOR]",
    "https://pornyteen.com/",
    "pornyteen.png",
    "pornyteen",
    category="Video Tubes",
)


def _clean_text(value):
    return utils.cleantext(value or "").strip()


def _absolute_url(path):
    if not path:
        return ""
    return urllib_parse.urljoin(site.url, path)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/",
        "Search",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Tags[/COLOR]",
        site.url + "tags/",
        "Tags",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Most Viewed[/COLOR]",
        site.url + "most-viewed/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Top Rated[/COLOR]",
        site.url + "top-rated/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Longest[/COLOR]",
        site.url + "longest/",
        "List",
        site.img_cat,
    )
    List(site.url + "videos/")
    utils.eod()


@site.register()
def List(url=None):
    if not url:
        url = site.url + "videos/"

    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    items = soup.select(".item.col, .item__inner, .item")
    seen_urls = set()

    for item in items:
        link = item.select_one("a.item__link[href], a[href*='/video/']")
        if not link:
            continue

        video_url = _absolute_url(utils.safe_get_attr(link, "href"))
        if not video_url or "/video/" not in video_url or video_url in seen_urls:
            continue
        seen_urls.add(video_url)

        img_tag = item.select_one("img.item__thumb-img, img[src], img[data-src]")
        thumb = ""
        if img_tag:
            thumb = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
            if thumb and thumb.startswith("data:"):
                thumb = ""
            thumb = _absolute_url(thumb)

        title = (
            _clean_text(utils.safe_get_text(item.select_one(".item__title-label, .item__title, .title")))
            or _clean_text(utils.safe_get_attr(link, "title"))
            or _clean_text(utils.safe_get_attr(img_tag, "alt") if img_tag else "")
            or "Pornyteen Video"
        )

        duration_tag = item.select_one(".item__stat.-duration .item__stat-label, .item__stat.-duration, .duration")
        duration = utils.safe_get_text(duration_tag) if duration_tag else ""
        if duration:
            duration = duration.strip()

        quality_tag = item.select_one(".item__stat.-quality .item__stat-label, .item__stat.-quality, .quality")
        quality = utils.safe_get_text(quality_tag) if quality_tag else ""
        if quality:
            title = f"{title} [{quality.strip()}]"

        site.add_download_link(
            title,
            video_url,
            "Playvid",
            thumb or site.img_cat,
            title,
            duration=duration,
        )

    next_link = soup.select_one("a[rel='next'], .pagination a.next, a.next")
    if next_link:
        next_href = utils.safe_get_attr(next_link, "href")
        if next_href:
            next_url = _absolute_url(next_href)
            if next_url and next_url != url and next_url != "#":
                site.add_dir(
                    "[COLOR hotpink]Next Page...[/COLOR]",
                    next_url,
                    "List",
                    site.img_next,
                )

    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    seen = set()

    for item in soup.select(".counter-list__li, .counter-list li, .categories-list li, a[href*='/categories/']"):
        a = item if item.name == "a" else item.select_one("a")
        if not a:
            continue

        cat_url = _absolute_url(utils.safe_get_attr(a, "href"))
        if (
            not cat_url
            or "/categories/" not in cat_url
            or cat_url.rstrip("/") == site.url.rstrip("/") + "/categories"
            or cat_url in seen
        ):
            continue
        seen.add(cat_url)

        title = _clean_text(utils.safe_get_attr(a, "title")) or _clean_text(utils.safe_get_text(a))
        count_tag = a.select_one(".counter, .count")
        count = utils.safe_get_text(count_tag) if count_tag else ""
        if count and count in title:
            title = title.replace(count, "").strip()

        display_name = f"[COLOR hotpink]{title}[/COLOR]"
        if count:
            display_name += f" [COLOR yellow]({count})[/COLOR]"

        img_tag = a.select_one("img") or item.select_one("img")
        thumb = utils.safe_get_attr(img_tag, "src", ["data-src"]) if img_tag else ""
        thumb = _absolute_url(thumb) if thumb else site.img_cat

        site.add_dir(display_name, cat_url, "List", thumb)

    utils.eod()


@site.register()
def Tags(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    seen = set()

    for item in soup.select(".counter-list__li, .counter-list a, .tags-list a, a[href*='/tags/']"):
        a = item if item.name == "a" else item.select_one("a")
        if not a:
            continue

        tag_url = _absolute_url(utils.safe_get_attr(a, "href"))
        if (
            not tag_url
            or "/tags/" not in tag_url
            or tag_url.rstrip("/") == site.url.rstrip("/") + "/tags"
            or tag_url in seen
        ):
            continue
        seen.add(tag_url)

        title = _clean_text(utils.safe_get_attr(a, "title")) or _clean_text(utils.safe_get_text(a))
        count_tag = a.select_one(".counter, .count")
        count = utils.safe_get_text(count_tag) if count_tag else ""
        if count and count in title:
            title = title.replace(count, "").strip()

        display_name = f"[COLOR hotpink]{title}[/COLOR]"
        if count:
            display_name += f" [COLOR yellow]({count})[/COLOR]"

        site.add_dir(display_name, tag_url, "List", site.img_cat)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = site.url + "search/" + urllib_parse.quote(keyword.replace(" ", "-")) + "/"
        List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_site_link(url, site.url)
        return

    soup = utils.parse_html(html)
    source = soup.select_one("video source[src], source[src]")
    if source:
        video_url = utils.safe_get_attr(source, "src")
        if video_url:
            video_url = _absolute_url(video_url)
            video_url += f"|Referer={urllib_parse.quote(url, safe='')}&User-Agent={urllib_parse.quote(utils.USER_AGENT, safe='')}"
            vp.play_from_direct_link(video_url)
            return

    vp.play_from_site_link(url, site.url)
