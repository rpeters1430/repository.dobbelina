"""
Cumination
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

from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.sites.soup_spec import SoupSiteSpec

site = AdultSite(
    "youcrazyx",
    "[COLOR hotpink]YouCrazyX[/COLOR]",
    "https://www.youcrazyx.com/",
    "youcrazyx.png",
    "youcrazyx",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": "a.video-link",
        "url": {"selector": ":self", "attr": "href"},
        "title": {"selector": ":self", "attr": "title", "clean": True},
        "thumbnail": {
            "selector": "img",
            "attr": "data-original",
            "fallback_attrs": ["data-src", "src"],
        },
        "duration": {"selector": ".duration", "text": True},
        "pagination": {
            "selector": 'ul.pagination li.active + li a, link[rel="next"]',
            "attr": "href",
        },
    }
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search.php?q=",
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
            + "?mode=youcrazyx.Related&url="
            + urllib_parse.quote_plus(item_url)
        )
        return [("[COLOR deeppink]Related videos[/COLOR]", "RunPlugin(" + contexturl + ")")]

    VIDEO_LIST_SPEC.run(site, soup, contextm=context_menu_builder)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.play_from_site_link(url)


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url)
    if not cathtml:
        utils.eod()
        return

    soup = utils.parse_html(cathtml)
    for anchor in soup.select('a[href*="/category/"]'):
        name = utils.cleantext(utils.safe_get_text(anchor))
        href = utils.safe_get_attr(anchor, "href")
        img_tag = anchor.find("img")
        img = utils.safe_get_attr(img_tag, "src") if img_tag else ""
        if name and href:
            site.add_dir(name, href, "List", img)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}".format(url, keyword.replace(" ", "+"))
        List(url)


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode=youcrazyx.List&url="
        + urllib_parse.quote_plus(url)
    )
    import xbmc
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")