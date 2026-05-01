"""
Cumination
Copyright (C) 2023 Team Cumination

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
from resources.lib.sites.soup_spec import SoupSiteSpec

site = AdultSite(
    "freeuseporn",
    "[COLOR hotpink]Freeuse Porn[/COLOR]",
    "https://www.freeuseporn.com/",
    "freeuseporn.png",
    "freeuseporn",
    category="Specialty",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": "a[href*='/videos/']",
        "url": {"attr": "href"},
        "title": {"selector": "img", "attr": "title", "clean": True},
        "thumbnail": {"selector": "img", "attr": "src", "fallback_attrs": ["data-src"]},
        "duration": {"selector": ".duration, .transition-opacity", "text": True},
        "pagination": {
            "selector": "a.page-link",
            "text_matches": ["next", ">", "»", "Next"],
            "attr": "href",
            "mode": "List",
        },
    }
)


@site.register(default_mode=True)
def Main(url):
    # site.add_dir("[COLOR hotpink]Tags[/COLOR]", site.url + "tags/", "Tags", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/videos/",
        "Search",
        site.img_search,
    )
    List(site.url + "videos?o=mr&page=1")
    utils.eod()


@site.register()
def List(url):
    utils.kodilog("Listing URL: {}".format(url))
    listhtml = utils.getHtml(url, "")
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    VIDEO_LIST_SPEC.run(site, soup, base_url=url, play_mode="Playvid")
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.play_from_site_link(url, url)


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(searchUrl, "Search")
    else:
        title = keyword.replace(" ", "-")
        searchUrl = searchUrl + title + "?o=mr&page=1"
        List(searchUrl)


@site.register()
def Tags(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)
    tags = []
    # Match upstream: href="/search/videos/([^"]+)".+?</i> ([^<]+)<
    for link in soup.select('a[href*="/search/videos/"]'):
        tag_url = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(utils.safe_get_text(link, default=""))
        if not tag_url or not name:
            continue
        tag = tag_url.split("/search/videos/")[-1].strip("/")
        tags.append((tag, name))

    for tag, name in sorted(tags):
        site.add_dir(name, site.url + "search/videos/", "Search", "", keyword=tag)
    utils.eod()


@site.register()
def Lookupinfo(url):
    # Match upstream: ("Tag", r'href="/search/videos/([^"]+)".+?</i>([^<]+)<', '')
    lookup_list = [("Tag", r'href="/search/videos/([^"]+)".+?</i>([^<]+)<', "")]

    lookupinfo = utils.LookupInfo(site.url, url, "freeuseporn.List", lookup_list)
    lookupinfo.getinfo()
