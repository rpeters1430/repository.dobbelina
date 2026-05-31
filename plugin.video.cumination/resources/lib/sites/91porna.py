"""
Cumination
Copyright (C) 2026 Team Cumination

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import annotations

import re
import time

from six.moves import urllib_parse

from resources.lib import jsunpack, utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "91porna",
    "[COLOR hotpink]91Porna[/COLOR]",
    "https://91porna.com/",
    "porna91.png",
    category="JAV & Asian",
    is_new=True,
)


def _absolute_url(url):
    if not url:
        return ""
    return urllib_parse.urljoin(site.url, url)


def _clean_title(value):
    return utils.cleantext(value or "").replace("\xa0", " ").strip()


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Latest[/COLOR]", site.url, "List", site.img_cat)
    site.add_dir("[COLOR hotpink]91 Videos[/COLOR]", site.url + "index/video?category=play", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Popular[/COLOR]", site.url + "index/video?category=now_month_hot", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url, "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "index/search?keyword=", "Search", site.img_search)
    List(site.url)


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    seen = set()
    for item in soup.select(".video-item"):
        link = item.select_one("a[href*='detail?video_key=']")
        if not link:
            continue

        video_url = _absolute_url(utils.safe_get_attr(link, "href"))
        if not video_url or video_url in seen:
            continue
        seen.add(video_url)

        img_tag = item.select_one("img")
        thumb = utils.safe_get_attr(img_tag, "data-src", ["src"])
        title = (
            _clean_title(utils.safe_get_attr(img_tag, "alt"))
            or _clean_title(utils.safe_get_text(item.select_one(".line-clamp-2")))
            or _clean_title(utils.safe_get_text(link))
        )
        if not title:
            continue
        duration = _clean_title(utils.safe_get_text(item.select_one(".poster .text-sm")))
        site.add_download_link(
            title,
            video_url,
            "Playvid",
            _absolute_url(thumb),
            title,
            duration=duration,
        )

    next_link = soup.select_one("a[rel='next'][href], .pagination a.next[href], a.next[href]")
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
    for link in soup.select("a[href*='/index/video'], a[href*='/av/relvideo']"):
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
    List(site.url + "index/search?keyword=" + urllib_parse.quote_plus(keyword))


def _unpack_first(html):
    match = re.search(r"eval\(function\(p,a,c,k,e,d\).*?</script>", html, re.DOTALL)
    if not match:
        return ""
    try:
        return jsunpack.unpack(match.group(0).replace("</script>", ""))
    except Exception:
        return ""


def _embed_script_url(embed_html):
    unpacked = _unpack_first(embed_html)
    token = re.search(r'encodeURIComponent\("([^"]+)"\)', unpacked)
    img = re.search(r"embed_play\.js\?img=([^&]+)&u=", unpacked)
    if not token or not img:
        return ""
    return _absolute_url(
        "/index/embed_play.js?img={0}&u={1}&t={2}".format(
            img.group(1),
            urllib_parse.quote(token.group(1)),
            int(time.time() / 1800),
        )
    )


def _hls_from_embed(embed_url, referrer):
    embed_html = utils.getHtml(embed_url, referrer)
    script_url = _embed_script_url(embed_html)
    if not script_url:
        return ""

    script_html = utils.getHtml(script_url, embed_url)
    unpacked = _unpack_first(script_html)
    source = re.search(r'<source[^>]+src=\\"([^"]+?\.m3u8[^"]*)\\"', unpacked)
    if not source:
        source = re.search(r'<source[^>]+src="([^"]+?\.m3u8[^"]*)"', unpacked)
    if source:
        return source.group(1).replace("\\", "")
    return ""


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    embed = re.search(r'property=["\']og:video["\']\s+content=["\']([^"\']+)', html)
    embed_url = embed.group(1) if embed else ""
    if embed_url:
        hls_url = _hls_from_embed(embed_url, url)
        if hls_url:
            vp.play_from_direct_link(
                hls_url + "|User-Agent={0}&Referer={1}".format(utils.USER_AGENT, embed_url)
            )
            return
        vp.play_from_site_link(embed_url, url)
        return

    vp.play_from_html(html, url)
