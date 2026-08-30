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

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "asianviralhub",
    "[COLOR hotpink]AsianViralHub[/COLOR]",
    "https://asianviralhub.com/",
    "asianviralhub.png",
    "asianviralhub",
    category="JAV & Asian",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url + "latest-updates/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    spec = {
        "items": "div.item",
        "url": {"selector": "a[href]", "attr": "href"},
        "title": {"selector": "a[title]", "attr": "title"},
        "thumbnail": {
            "selector": "img",
            "attr": "data-original",
            "fallback_attrs": ["src"],
        },
        "duration": {"selector": ".duration"},
        "pagination": {"selector": "li.next a[href]", "attr": "href"},
    }

    utils.soup_videos_list(site, soup, spec)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    vpage = utils.getHtml(url, site.url)
    if "kt_player('kt_player'" in vpage:
        vp.progress.update(60, "[CR]{0}[CR]".format("kt_player detected"))
        vp.play_from_kt_player(vpage, url)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        List(url + keyword.replace(" ", "-") + "/")
