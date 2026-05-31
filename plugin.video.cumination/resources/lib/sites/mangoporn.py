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
    "mangoporn",
    "[COLOR hotpink]MangoPorn[/COLOR]",
    "https://mangoporn.net/",
    "mangoporn.png",
    category="Specialty",
    is_new=True,
)


def _absolute_url(url):
    if not url:
        return ""
    return urllib_parse.urljoin(site.url, url)


def _clean_title(value):
    return utils.cleantext(value or "").replace("\xa0", " ").strip()


def _image_from_tag(img_tag):
    return utils.safe_get_attr(
        img_tag,
        "data-wpfc-original-src",
        ["data-src", "data-original", "src"],
    )


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]XXX Movies[/COLOR]", site.url + "genres/porn-movies/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]XXX Clips[/COLOR]", site.url + "xxxclips/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Trending[/COLOR]", site.url + "trending/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Ratings[/COLOR]", site.url + "ratings/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Genres[/COLOR]", site.url, "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search)
    List(site.url)


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    seen = set()
    for item in soup.select("article.item.movies, article.item.tvshows, article.item"):
        link = item.select_one(".data h3 a[href]") or item.select_one(".poster a[href]")
        if not link:
            continue

        video_url = _absolute_url(utils.safe_get_attr(link, "href"))
        if not video_url or video_url in seen or video_url.rstrip("/") == site.url.rstrip("/"):
            continue
        seen.add(video_url)

        title = (
            _clean_title(utils.safe_get_text(link))
            or _clean_title(utils.safe_get_attr(item.select_one("img"), "alt"))
        )
        if not title:
            continue

        thumb = _image_from_tag(item.select_one("img"))
        duration = _clean_title(utils.safe_get_text(item.select_one(".duration")))
        site.add_download_link(
            title,
            video_url,
            "Playvid",
            thumb,
            title,
            duration=duration,
        )

    next_link = soup.select_one(".pagination a.next[href], a.next.page-numbers[href], a[rel='next']")
    if next_link:
        next_url = _absolute_url(utils.safe_get_attr(next_link, "href"))
        if next_url:
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
    for link in soup.select("a[href*='/genre/']"):
        cat_url = _absolute_url(utils.safe_get_attr(link, "href"))
        title = _clean_title(utils.safe_get_text(link))
        if not cat_url or not title or cat_url in seen:
            continue
        seen.add(cat_url)
        site.add_dir(title, cat_url, "List", site.img_cat)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
        return
    List(site.url + "?s=" + urllib_parse.quote_plus(keyword))


def _host_links_from_html(html):
    soup = utils.parse_html(html)
    links = []
    seen = set()
    for item in soup.select("#playeroptionsul li, li.hosts-buttons-wpx"):
        for attr in ("data-fl-url", "data-fl-source"):
            link = utils.safe_get_attr(item, attr)
            if link and link not in seen:
                seen.add(link)
                links.append(link)
        anchor = item.select_one("a[href]")
        link = utils.safe_get_attr(anchor, "href")
        if link and link not in seen and not link.startswith("#"):
            seen.add(link)
            links.append(link)
    return links


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    links = _host_links_from_html(html)
    if links:
        vp.play_from_link_list(links)
        return

    vp.play_from_html(html, url)
