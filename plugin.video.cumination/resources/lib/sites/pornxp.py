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

from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.sites.soup_spec import SoupSiteSpec

site = AdultSite(
    "pornxp",
    "[COLOR hotpink]PornXP[/COLOR]",
    "https://pornxp.com-mirror.com/",
    "pornxp.png",
    "pornxp",
)

VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": ".item_cont",
        "url": {"selector": 'a[href*="/videos/"]', "attr": "href"},
        "title": {"selector": ".item_title", "text": True},
        "thumbnail": {
            "selector": "img.item_img",
            "attr": "data-src",
            "fallback_attrs": ["src"],
        },
        "duration": {"selector": ".item_dur", "text": True},
        "pagination": {
            "selector": '#pages span:has(a.chosen) + span a, #pages a:-soup-contains(">")',
            "attr": "href",
        },
    }
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]New releases[/COLOR]",
        site.url + "released/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]HD[/COLOR]", site.url + "hd/?sort=new", "List", site.img_cat
    )
    site.add_dir("[COLOR hotpink]Tags[/COLOR]", site.url, "Tags", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "tags/", "Search", site.img_search
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
            + "?mode=pornxp.Lookupinfo&url="
            + urllib_parse.quote_plus(item_url)
        )
        return [("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + contexturl + ")")]

    VIDEO_LIST_SPEC.run(site, soup, contextm=context_menu_builder)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    videopage = utils.getHtml(url, site.url, ignoreCertificateErrors=True)
    if not videopage:
        vp.progress.close()
        return

    soup = utils.parse_html(videopage)
    sources = {}
    for source in soup.select("video source"):
        src = utils.safe_get_attr(source, "src")
        quality = utils.safe_get_attr(source, "title")
        if src and quality:
            sources[quality] = src

    videourl = utils.prefquality(
        sources,
        sort_by=lambda x: int("".join([y for y in x if y.isdigit() or "0"]))
        if any(c.isdigit() for c in x)
        else 0,
        reverse=True,
    )

    if not videourl:
        vp.progress.close()
        return

    videourl = urllib_parse.urljoin(site.url, videourl)
    vp.progress.update(75, "[CR]Video found[CR]")
    vp.play_from_direct_link(videourl)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}".format(url, keyword.replace(" ", "%20"))
        List(url)


@site.register()
def Tags(url):
    listhtml = utils.getHtml(url)
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    for tag_container in soup.select(".tags"):
        for anchor in tag_container.select("a"):
            name = utils.cleantext(utils.safe_get_text(anchor))
            href = utils.safe_get_attr(anchor, "href")
            if name and href:
                site.add_dir(name, site.url + href.lstrip("/") + "?sort=new", "List", "")

    utils.eod()


@site.register()
def Lookupinfo(url):
    class PornxpLookup(utils.LookupInfo):
        def url_constructor(self, url):
            return site.url + url + "?sort=new"

    lookup_list = [("Tag", ['class="tags">(.*?)class', '/(tags/[^"]+)">([^<]+)<'], "")]

    lookupinfo = PornxpLookup(site.url, url, "pornxp.List", lookup_list)
    lookupinfo.getinfo()