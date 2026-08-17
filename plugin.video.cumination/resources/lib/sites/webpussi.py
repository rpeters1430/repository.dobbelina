"""
Cumination
Copyright (C) 2026 Team Cumination

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import annotations

from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "webpussi",
    "[COLOR hotpink]Webpussi[/COLOR]",
    "https://www.webpussi.com/",
    "webpussi.png",
    category="Cams & Live",
    is_new=True,
)


def _absolute_url(url):
    if not url:
        return ""
    return urllib_parse.urljoin(site.url, url)


def _clean_title(value):
    title = utils.cleantext(value or "")
    return title.strip()


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Latest Videos[/COLOR]", site.url + "latest-updates/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Top Rated[/COLOR]", site.url + "top-rated/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Most Popular[/COLOR]", site.url + "most-popular/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url + "categories/", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Models[/COLOR]", site.url + "models/", "Models", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search)
    List(site.url)


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    seen = set()
    for item in soup.select(".item"):
        a = item.select_one("a[href*='/videos/']") or item.select_one("a")
        if not a:
            continue

        video_url = _absolute_url(utils.safe_get_attr(a, "href"))
        if not video_url or "/videos/" not in video_url or video_url in seen:
            continue
        seen.add(video_url)

        img = item.select_one("img")
        thumb = utils.safe_get_attr(img, "data-original", ["data-src", "src"])
        title = (
            _clean_title(utils.safe_get_attr(a, "title"))
            or _clean_title(utils.safe_get_attr(img, "alt"))
            or _clean_title(utils.safe_get_text(a))
        )
        duration = utils.safe_get_text(item.select_one(".duration, .time, .wrap .time"))
        duration = duration.replace("\n", " ").strip()

        if title:
            site.add_download_link(
                title, video_url, "Playvid", thumb, title, duration=duration
            )

    next_page = soup.select_one(".pagination a.next[href], .pagination li.next a[href], .pagination-holder li.next a[href]")
    if not next_page:
        for a_tag in soup.select(".pagination a[href], .pagination-holder a[href]"):
            if "next" in utils.safe_get_text(a_tag).lower():
                next_page = a_tag
                break
    if next_page:
        next_url = _absolute_url(utils.safe_get_attr(next_page, "href"))
        if next_url and next_url != url:
            site.add_dir("Next Page", next_url, "List", site.img_next)

    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    seen = set()
    for item in soup.select(".item, a.item, a[href*='/categories/']"):
        if item.find_parent(class_=["pagination", "pagination-holder"]):
            continue
        link = item if item.name == "a" else item.select_one("a")
        if not link:
            continue

        cat_url = _absolute_url(utils.safe_get_attr(link, "href"))
        if not cat_url or "/categories/" not in cat_url or cat_url.rstrip("/") == site.url.rstrip("/") + "/categories" or cat_url in seen:
            continue
        seen.add(cat_url)

        img = item.select_one("img")
        thumb = utils.safe_get_attr(img, "data-original", ["data-src", "src"])
        title = (
            _clean_title(utils.safe_get_attr(link, "title"))
            or _clean_title(utils.safe_get_text(item.select_one(".title, strong.title")))
            or _clean_title(utils.safe_get_attr(img, "alt"))
            or _clean_title(utils.safe_get_text(link))
        )
        if title:
            site.add_dir(title, cat_url, "List", thumb or site.img_cat)

    next_page = soup.select_one(".pagination a.next[href], .pagination li.next a[href], .pagination-holder li.next a[href]")
    if next_page:
        next_url = _absolute_url(utils.safe_get_attr(next_page, "href"))
        if next_url and next_url != url:
            site.add_dir("Next Page", next_url, "Categories", site.img_next)

    utils.eod()


@site.register()
def Models(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    seen = set()
    for item in soup.select(".item, a.item, a[href*='/models/']"):
        if item.find_parent(class_=["pagination", "pagination-holder"]):
            continue
        link = item if item.name == "a" else item.select_one("a")
        if not link:
            continue

        model_url = _absolute_url(utils.safe_get_attr(link, "href"))
        if not model_url or "/models/" not in model_url or model_url.rstrip("/") == site.url.rstrip("/") + "/models" or model_url in seen:
            continue
        seen.add(model_url)

        img = item.select_one("img")
        thumb = utils.safe_get_attr(img, "data-original", ["data-src", "src"])
        title = (
            _clean_title(utils.safe_get_attr(link, "title"))
            or _clean_title(utils.safe_get_text(item.select_one(".title, strong.title")))
            or _clean_title(utils.safe_get_attr(img, "alt"))
            or _clean_title(utils.safe_get_text(link))
        )
        if title:
            site.add_dir(title, model_url, "List", thumb or site.img_cat)

    next_page = soup.select_one(".pagination a.next[href], .pagination li.next a[href], .pagination-holder li.next a[href]")
    if next_page:
        next_url = _absolute_url(utils.safe_get_attr(next_page, "href"))
        if next_url and next_url != url:
            site.add_dir("Next Page", next_url, "Models", site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
        return
    search_url = site.url + "search/" + urllib_parse.quote_plus(keyword) + "/"
    List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    vp.play_from_kt_player(html, url)
