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
    "camhub",
    "[COLOR hotpink]CamHub[/COLOR]",
    "https://www.camhub.cc/",
    "camhub.png",
    "camhub",
    category="Cams & Live",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": ".item",
        "url": {"selector": "a[href]", "attr": "href"},
        "title": {
            "selector": "a[title]",
            "attr": "title",
            "fallback_selectors": ["a"],
            "fallback_attrs": ["title"],
        },
        "thumbnail": {
            "selector": "img",
            "attr": "data-original",
            "fallback_attrs": ["data-webp", "src"],
        },
        "duration": {"selector": ".duration, .time", "text": True},
    }
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url + "categories/", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Top Rated[/COLOR]", site.url + "top-rated/", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search)
    List(site.url + "latest-updates/")
    utils.eod()


def _extract_next_page(soup, current_url):
    pag = soup.find(class_="pagination")
    if not pag:
        return None, None

    active = pag.find(class_="active")
    if active:
        next_a = active.find_next_sibling("a")
        if next_a:
            text = next_a.get_text(strip=True)
            params = utils.safe_get_attr(next_a, "data-parameters")
            match = re.search(r"from:(\d+)", params or "") if params else None
            next_num = match.group(1) if match else text

            base_clean = current_url.rstrip("/")
            if re.search(r"/\d+$", base_clean):
                next_url = re.sub(r"/\d+$", "/{}/".format(next_num), base_clean)
            else:
                next_url = "{}/{}/".format(base_clean, next_num)
            return next_url, next_num or "Next"

    return None, None


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    VIDEO_LIST_SPEC.run(site, soup, base_url=site.url)

    next_url, next_page = _extract_next_page(soup, url)
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
        if not href or "/categories/" not in href or href.rstrip("/") == site.url.rstrip("/") + "/categories":
            continue
        title_el = a.find(class_="title") or a.find("b") or a
        name = title_el.get_text(strip=True) if title_el else ""
        if not name:
            slug = href.rstrip("/").split("/")[-1]
            name = " ".join(slug.split("-")).title()
        if name.lower() in seen:
            continue
        seen.add(name.lower())

        img = a.find("img")
        thumb = ""
        if img:
            thumb = (
                utils.safe_get_attr(img, "data-original")
                or utils.safe_get_attr(img, "src")
                or ""
            )

        cat_url = urllib_parse.urljoin(site.url, href)
        site.add_dir(name, cat_url, "List", thumb or site.img_cat)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        keyword = utils._get_keyboard(heading=utils.i18n("search"))
    if not keyword:
        return
    search_url = urllib_parse.urljoin(site.url, "search/{}/".format(urllib_parse.quote(keyword)))
    List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    video_id_match = re.search(r"/videos?/(\d+)/", url)
    embed_url = "https://www.camhub.cc/embed/{}".format(video_id_match.group(1)) if video_id_match else url

    embed_html = utils.getHtml(embed_url, url)
    if embed_html:
        if vp.play_from_kt_player(embed_html, embed_url):
            return
        if vp.play_from_html(embed_html, embed_url):
            return

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
        if href and not any(h in href.lower() for h in ("camhub.cc", "google", "traffic", "banner", "javascript:")):
            if vp.play_from_link_to_resolve(href):
                return
