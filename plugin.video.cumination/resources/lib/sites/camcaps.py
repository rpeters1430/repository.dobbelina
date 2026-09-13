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

import re
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.sites.soup_spec import SoupSiteSpec

site = AdultSite(
    "camcaps",
    "[COLOR hotpink]CamCaps[/COLOR]",
    "https://camcaps.tv/",
    "camcaps.png",
    "camcaps",
    category="Cams & Live",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": "article.thumb",
        "url": {"selector": "a[href]", "attr": "href"},
        "title": {"selector": "h3", "text": True, "fallback_selectors": ["a"]},
        "thumbnail": {
            "selector": "img",
            "attr": "src",
            "fallback_attrs": ["data-src"],
        },
        "duration": {"selector": ".dur-icon", "text": True},
    }
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url + "categories", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Tags[/COLOR]", site.url + "tags", "Tags", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/videos/", "Search", site.img_search)
    List(site.url + "videos")
    utils.eod()


def _next_page_url(soup):
    next_a = soup.select_one("a.next[href]")
    if not next_a:
        return None, None
    href = utils.safe_get_attr(next_a, "href")
    if not href:
        return None, None
    next_url = urllib_parse.urljoin(site.url, href)
    match = re.search(r"[?&]page=(\d+)", next_url)
    next_page = match.group(1) if match else "Next"
    return next_url, next_page


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.eod()
        return
    soup = utils.parse_html(listhtml)
    VIDEO_LIST_SPEC.run(site, soup, base_url=site.url)

    next_url, next_page = _next_page_url(soup)
    if next_url:
        site.add_dir("Next Page ({})".format(next_page), next_url, "List", site.img_next)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return
    soup = utils.parse_html(html)
    seen = set()
    for a in soup.find_all("a", href=True):
        href = utils.safe_get_attr(a, "href")
        if not href or "/search/videos/" not in href:
            continue
        text = a.get_text(strip=True)
        cleaned_name = re.sub(r"^\d+\s*", "", text).strip().title()
        if not cleaned_name or cleaned_name.lower() in seen:
            continue
        seen.add(cleaned_name.lower())
        cat_url = urllib_parse.urljoin(site.url, href)
        site.add_dir(cleaned_name, cat_url, "List", site.img_cat)

    utils.eod()


@site.register()
def Tags(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return
    soup = utils.parse_html(html)
    seen = set()
    for a in soup.find_all("a", href=True):
        href = utils.safe_get_attr(a, "href")
        if not href or ("/search/videos/" not in href and "/tag/" not in href):
            continue
        text = a.get_text(strip=True)
        cleaned_name = re.sub(r"^\d+\s*", "", text).strip().title()
        if not cleaned_name or cleaned_name.lower() in seen:
            continue
        seen.add(cleaned_name.lower())
        tag_url = urllib_parse.urljoin(site.url, href)
        site.add_dir(cleaned_name, tag_url, "List", site.img_cat)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        keyword = utils._get_keyboard(heading=utils.i18n("search"))
    if not keyword:
        return
    search_url = urllib_parse.urljoin(site.url, "search/videos/{}".format(urllib_parse.quote(keyword)))
    List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        return

    soup = utils.parse_html(html)
    for iframe in soup.find_all("iframe"):
        src = utils.safe_get_attr(iframe, "src")
        if not src or "xhadapt" in src:
            continue
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = urllib_parse.urljoin(site.url, src)

        if any(d in src.lower() for d in utils.DOODSTREAM_DOMAINS):
            stream_url = vp._solve_doodstream(src)
            if stream_url:
                vp.play_from_direct_link(stream_url)
                return
        if vp.play_from_link_to_resolve(src):
            return

    for video in soup.find_all(["video", "source"]):
        src = utils.safe_get_attr(video, "src")
        if src:
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = urllib_parse.urljoin(site.url, src)
            vp.play_from_direct_link(src + "|Referer=" + url)
            return

    for a in soup.find_all("a", href=True):
        href = utils.safe_get_attr(a, "href")
        if href and not any(h in href.lower() for h in ("camcaps.tv", "google", "traffic", "banner", "javascript:")):
            if vp.play_from_link_to_resolve(href):
                return
