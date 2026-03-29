"""
Ultimate Whitecream
Copyright (C) 2020 Team Cumination

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

import json
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.sites.soup_spec import SoupSiteSpec

site = AdultSite(
    "xmoviesforyou",
    "[COLOR hotpink]Xmoviesforyou[/COLOR]",
    "https://xmoviesforyou.com/",
    "xmoviesforyou.png",
    "xmoviesforyou",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": [".grid-box-img", "article.group"],
        "url": {"selector": "a", "attr": "href"},
        "title": {
            "selector": ["a[title]", "h3 a", "a"],
            "attr": "title",
            "text": True,
            "clean": True,
        },
        "thumbnail": {
            "transform": lambda v, item: utils.get_thumbnail(item.select_one("img"))
        },
        "pagination": {
            "selector": "a.next.page-numbers, a[href*='?page='], a[href*='/page/']",
            "attr": "href",
            "text_matches": ["next"],
        },
    }
)


def _normalize_categories_url(url):
    current = (url or "").strip()
    if not current or current.rstrip("/") == site.url.rstrip("/"):
        return urllib_parse.urljoin(site.url, "categories")
    return current


def _normalize_search_url(url):
    current = (url or "").strip()
    if not current:
        return site.url + "search?q="
    if "search?q=" in current or "?s=" in current:
        return current
    if current.rstrip("/") == site.url.rstrip("/"):
        return site.url + "search?q="
    return current


def _add_category_dir(name, count, href):
    if not name or not href:
        return
    label = name
    if count:
        label = "{} ([COLOR hotpink]{}[/COLOR])".format(name, count)
    site.add_dir(label, urllib_parse.urljoin(site.url, href), "List", "")


def _categories_from_html(cathtml):
    soup = utils.parse_html(cathtml)
    if not soup:
        return False

    added = 0
    for item in soup.select("main a[href*='/category/']"):
        href = utils.safe_get_attr(item, "href")
        name = utils.safe_get_text(item.select_one("h3")) or utils.safe_get_text(item)
        count_text = utils.safe_get_text(item.select_one("span"))
        count = ""
        if count_text:
            digits = "".join(ch for ch in count_text if ch.isdigit())
            count = digits
        if not name or not href:
            continue
        _add_category_dir(name, count, href)
        added += 1

    return added > 0


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "wp-json/wp/v2/categories?page=1",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search?q=",
        "Search",
        site.img_search,
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)

    def context_menu_builder(item_url, item_title):
        contexturl = (
            utils.addon_sys
            + "?mode=xmoviesforyou.Lookupinfo&url="
            + urllib_parse.quote_plus(item_url)
        )
        return [
            ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + contexturl + ")")
        ]

    # Custom title formatting from original site
    # name = name.replace("[", "[COLOR pink]").replace("] ", "[/COLOR] ")
    def title_transform(title, item):
        if title:
            return title.replace("[", "[COLOR pink]").replace("] ", "[/COLOR] ")
        return title

    # Update selectors for this run to include the transform
    selectors = VIDEO_LIST_SPEC.selectors.copy()
    selectors["title"] = selectors["title"].copy()
    selectors["title"]["transform"] = title_transform

    VIDEO_LIST_SPEC.run(site, soup, selectors=selectors, contextm=context_menu_builder)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.play_from_site_link(url, url)


@site.register()
def Search(url, keyword=None):
    searchUrl = _normalize_search_url(url)
    if not keyword:
        site.search_dir(searchUrl, "Search")
    else:
        title = keyword.replace(" ", "+")
        searchUrl = searchUrl + title
        List(searchUrl)


@site.register()
def Categories(url):
    url = _normalize_categories_url(url)
    cathtml = utils.getHtml(url, "")
    if not cathtml:
        utils.eod()
        return
    try:
        catjson = json.loads(cathtml)
    except (TypeError, ValueError):
        if not _categories_from_html(cathtml):
            utils.eod()
            return
        utils.eod()
        return

    jdata = []
    i = 0
    # The original loop seems to try to fetch multiple pages of categories
    while i < 10 and len(catjson) > 0:
        i += 1
        jdata += catjson
        parsed_url = urllib_parse.urlparse(url)
        params = urllib_parse.parse_qs(parsed_url.query)
        current_page = int(params.get("page", [1])[0])
        next_page = current_page + 1

        query = params.copy()
        query["page"] = [str(next_page)]
        new_query = urllib_parse.urlencode(query, doseq=True)
        url = urllib_parse.urlunparse(parsed_url._replace(query=new_query))

        cathtml = utils.getHtml(url, "")
        if not cathtml:
            break
        try:
            catjson = json.loads(cathtml)
        except (TypeError, ValueError):
            break

    for category in jdata:
        _add_category_dir(category.get("name"), category.get("count"), category.get("link"))
    utils.eod()


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Cat", '(category/[^"]+)" rel="tag">([^<]+)', ""),
        ("Tag", '(tag/[^"]+)" rel="tag">([^<]+)', ""),
    ]

    lookupinfo = utils.LookupInfo(site.url, url, "xmoviesforyou.List", lookup_list)
    lookupinfo.getinfo()
