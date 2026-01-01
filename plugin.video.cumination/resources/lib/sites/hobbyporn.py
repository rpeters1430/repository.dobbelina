"""
Cumination
Copyright (C) 2022 Team Cumination

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

import re
import xbmcplugin
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "hobbyporn",
    "[COLOR hotpink]Hobby Porn[/COLOR]",
    "https://hobby.porn/",
    "hobbyporn.png",
    "hobbyporn",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Cat",
        site.img_cat,
    )
    site.add_dir("[COLOR hotpink]Tags[/COLOR]", site.url + "tags/", "Cat", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Models[/COLOR]", site.url + "models/", "Models", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    List(site.url)


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)
    thumbnails = utils.Thumbnails(site.name)
    for item in soup.select(".item-video, .item, .video-item"):
        link = item.select_one("a[href]")
        videourl = utils.safe_get_attr(link, "href", default="")
        if not videourl:
            continue
        name = utils.cleantext(
            utils.safe_get_attr(link, "title", default=utils.safe_get_text(link))
        )
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
        img = thumbnails.fix_img(img) if img else ""
        duration = utils.safe_get_text(item.select_one(".duration"), default="")
        site.add_download_link(name, videourl, "Playvid", img, name, duration=duration)

    next_link = soup.select_one(".pagination .active + li a[href]")
    if next_link:
        nextp = utils.safe_get_attr(next_link, "href", default="")
        if nextp:
            nextp = urllib_parse.urljoin(site.url, nextp)
            site.add_dir(
                "[COLOR hotpink]Next Page...[/COLOR] ({0})".format(
                    nextp.split("/")[-2]
                ),
                nextp,
                "List",
                site.img_next,
            )

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, site.url)
    sources = re.compile(
        r"video(?:_alt)?_url:\s*'([^']+).+?video(?:_alt)?_url_text:\s*'([^']+)",
        re.DOTALL | re.IGNORECASE,
    ).findall(videopage)
    if sources:
        sources = {qual: surl for surl, qual in sources}
        source = utils.prefquality(sources, sort_by=lambda x: int(x[:-1]), reverse=True)
        if source:
            source = utils.getVideoLink(source)
            vp.play_from_direct_link(source)
        else:
            vp.progress.close()
            return
    else:
        source = re.compile(
            r'<iframe.+?src="([^"]+)', re.DOTALL | re.IGNORECASE
        ).findall(videopage)
        if source:
            if vp.resolveurl.HostedMediaFile(source[0]):
                vp.play_from_link_to_resolve(source[0])
            else:
                vp.progress.close()
                utils.notify("Oh Oh", "No playable Videos found")
                return
        else:
            vp.progress.close()
            utils.notify("Oh Oh", "No Videos found")
            return


@site.register()
def Cat(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    for item in soup.select(".item"):
        link = item.select_one("a[href]")
        caturl = utils.safe_get_attr(link, "href", default="")
        name = utils.safe_get_text(item.select_one(".title, span, a"), default="")
        count = utils.safe_get_text(item.select_one(".count, span"), default="")
        if not caturl or not name:
            continue
        name = name + " [COLOR deeppink]" + count + " videos[/COLOR]"
        site.add_dir(name, caturl, "List", "", "")
    xbmcplugin.addSortMethod(utils.addon_handle, xbmcplugin.SORT_METHOD_TITLE)
    utils.eod()


@site.register()
def Models(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    for item in soup.select(".item-model, .item"):
        link = item.select_one("a[href]")
        caturl = utils.safe_get_attr(link, "href", default="")
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
        name = utils.cleantext(
            utils.safe_get_text(item.select_one(".title, a"), default="")
        )
        count = utils.safe_get_text(item.select_one("span"), default="")
        if not caturl or not name:
            continue
        name = name + " [COLOR hotpink]({0} videos)[/COLOR]".format(count)
        site.add_dir(name, caturl, "List", img)

    next_link = soup.select_one(".pagination .active + li a[href]")
    if next_link:
        nextp = urllib_parse.urljoin(site.url, utils.safe_get_attr(next_link, "href", default=""))
        site.add_dir(
            "[COLOR hotpink]Next Page...[/COLOR] ({0})".format(nextp.split("/")[-2]),
            nextp,
            "Models",
            site.img_next,
        )

    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "-")
        searchUrl = searchUrl + title + "/"
        List(searchUrl)
