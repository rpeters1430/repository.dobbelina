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
from resources.lib.decrypters.kvsplayer import kvs_decode
from resources.lib.sites.soup_spec import SoupSiteSpec

site = AdultSite(
    "camgirlfap",
    "[COLOR hotpink]CamGirlFap[/COLOR]",
    "https://camgirlfap.com/",
    "camgirlfap.png",
    "camgirlfap",
    category="Cams & Live",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": ".thumb_rel",
        "url": {"selector": "a[href]", "attr": "href"},
        "title": {"selector": "a", "attr": "title", "fallback_attrs": [], "text": False},
        "thumbnail": {
            "selector": "img",
            "attr": "data-original",
            "fallback_attrs": ["src"],
        },
        "duration": {"selector": ".time", "text": True},
    }
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url + "categories/?from=1", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Models[/COLOR]", site.url + "models/?sort_by=total_videos&from=1", "Models", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search)
    List(site.url + "latest-updates/?from=1")
    utils.eod()


def _next_page_url(url, soup):
    next_a = soup.select_one(".pagination a.next")
    if not next_a:
        return None, None
    params = dict(re.findall(r"([a-z_]+):([^;]+)", utils.safe_get_attr(next_a, "data-parameters", default="")))
    next_from = params.get("from")
    if not next_from:
        return None, None
    parsed = urllib_parse.urlsplit(url)
    query = dict(urllib_parse.parse_qsl(parsed.query))
    query["from"] = next_from
    if "from_videos" in query:
        query["from_videos"] = next_from
    if "from_albums" in query:
        query["from_albums"] = next_from
    if "sort_by" in params:
        query["sort_by"] = params["sort_by"]
    next_url = urllib_parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib_parse.urlencode(query), ""))
    return next_url, next_from


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.eod()
        return
    soup = utils.parse_html(listhtml)
    VIDEO_LIST_SPEC.run(site, soup, base_url=site.url)

    next_url, next_page = _next_page_url(url, soup)
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
    for anchor in soup.select(".thumb.item a[href*='/categories/']"):
        href = utils.safe_get_attr(anchor, "href")
        name = utils.safe_get_attr(anchor, "title") or utils.safe_get_text(anchor.select_one(".title"))
        if not href or not name:
            continue
        img_tag = anchor.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"]) if img_tag else ""
        videos = utils.safe_get_text(anchor.select_one(".thumb-item"), default="")
        label = "{} [COLOR hotpink][{}][/COLOR]".format(utils.cleantext(name), videos) if videos else utils.cleantext(name)
        cat_url = urllib_parse.urljoin(site.url, href) + "?sort_by=post_date&from=1"
        site.add_dir(label, cat_url, "List", img)

    next_url, next_page = _next_page_url(url, soup)
    if next_url:
        site.add_dir("Next Page ({})".format(next_page), next_url, "Categories", site.img_next)
    utils.eod()


@site.register()
def Models(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return
    soup = utils.parse_html(html)
    for anchor in soup.select(".thumb.item a[href*='/models/']"):
        href = utils.safe_get_attr(anchor, "href")
        name = utils.safe_get_attr(anchor, "title") or utils.safe_get_text(anchor.select_one(".title"))
        if not href or not name:
            continue
        img_tag = anchor.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"]) if img_tag else ""
        videos = utils.safe_get_text(anchor.select_one(".thumb-item"), default="")
        label = "{} [COLOR hotpink][{}][/COLOR]".format(utils.cleantext(name), videos) if videos else utils.cleantext(name)
        model_url = urllib_parse.urljoin(site.url, href) + "?sort_by=post_date&from=1"
        site.add_dir(label, model_url, "List", img)

    next_url, next_page = _next_page_url(url, soup)
    if next_url:
        site.add_dir("Next Page ({})".format(next_page), next_url, "Models", site.img_next)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        kw_path = urllib_parse.quote_plus(keyword.replace(" ", "-"))
        kw_q = urllib_parse.quote_plus(keyword)
        search_url = "{}search/{}/".format(site.url, kw_path) + "?q={}&from_videos=1&from_albums=1".format(kw_q)
        List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    license_match = re.search(r"license_code:\s*'([^']+)'", html, re.IGNORECASE)
    license_code = license_match.group(1) if license_match else ""

    sources = {}
    for url_key, label_key, default_label in (
        ("video_url", "video_url_text", "480p"),
        ("video_alt_url", "video_alt_url_text", "720p"),
        ("video_alt_url2", "video_alt_url2_text", "1080p"),
    ):
        url_match = re.search(r"{}:\s*'([^']+)'".format(url_key), html, re.IGNORECASE)
        if not url_match:
            continue
        stream_url = url_match.group(1)
        label_match = re.search(r"{}:\s*'([^']+)'".format(label_key), html, re.IGNORECASE)
        label = label_match.group(1) if label_match else default_label
        if stream_url.startswith("function/"):
            if license_code:
                try:
                    stream_url = kvs_decode(stream_url, license_code)
                except Exception:
                    stream_url = re.sub(r"^function/\d+/", "", stream_url)
            else:
                stream_url = re.sub(r"^function/\d+/", "", stream_url)
        if stream_url and stream_url.startswith("http"):
            sources[label] = stream_url

    if sources:
        stream_url = (
            utils.selector(
                "Select quality",
                sources,
                sort_by=lambda x: int(re.sub(r"\D", "", x) or 0),
                reverse=True,
            )
            if len(sources) > 1
            else next(iter(sources.values()))
        )
        if stream_url:
            vp.play_from_direct_link(stream_url + "|Referer=" + url)
            return

    vp.play_from_link_to_resolve(url)
