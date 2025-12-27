"""
Cumination
Copyright (C) 2021 Team Cumination

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
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "perverzija",
    "[COLOR hotpink]Perverzija[/COLOR]",
    "https://tube.perverzija.com/",
    "https://tube.perverzija.com/wp-content/uploads/2018/12/favico2.ico",
    "perverzija",
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Tags[/COLOR]", site.url + "tags/", "Tag", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Studios[/COLOR]", site.url + "studios/", "Studios", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Stars[/COLOR]", site.url + "stars/", "Stars", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Full Movies[/COLOR]",
        site.url + "full-movie/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url + "page/1/")


@site.register()
def List(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return

    container = soup.select_one(".video-listing-filter") or soup
    videos = container.select("div.item-thumbnail")

    for video in videos:
        link = video.select_one("a[href][title]")
        if not link:
            continue

        videourl = urllib_parse.urljoin(
            site.url, utils.safe_get_attr(link, "href", default="")
        )
        name = utils.cleantext(
            utils.safe_get_attr(
                link, "title", default=utils.safe_get_text(link, default="")
            )
        )
        if not videourl or not name:
            continue

        img_tag = video.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src"])
        duration = utils.safe_get_text(video.select_one(".time_dur"), default="")

        contextmenu = []
        contexturl = (
            utils.addon_sys
            + "?mode="
            + str("perverzija.Lookupinfo")
            + "&url="
            + urllib_parse.quote_plus(videourl)
        )
        contextmenu.append(
            ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + contexturl + ")")
        )

        site.add_download_link(
            name,
            videourl,
            "Play",
            img,
            name,
            noDownload=True,
            contextm=contextmenu,
            duration=duration,
        )

    pagination = soup.find(
        "a", attrs={"label": re.compile(r"Next", re.IGNORECASE)}
    ) or soup.select_one('a[rel="next"]')
    if pagination:
        pgtxt_elem = soup.find(class_=re.compile(r"\bpages\b"))
        pgtxt = utils.cleantext(utils.safe_get_text(pgtxt_elem, default=""))
        label = "Next Page..."
        if pgtxt:
            label += f" (Currently in {pgtxt})"
        next_url = urllib_parse.urljoin(
            site.url, utils.safe_get_attr(pagination, "href", default="")
        )
        site.add_dir(label, next_url, "List", site.img_next)
    utils.eod()


def _taxonomy(url, fragment):
    html = utils.getHtml(url)
    soup = utils.parse_html(html)
    if not soup:
        utils.eod()
        return

    seen = set()
    for link in soup.select(f'a[href*="{fragment}"]'):
        href = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(utils.safe_get_text(link, default=""))
        if not href or not name or fragment not in href:
            continue

        key = (href, name)
        if key in seen:
            continue
        seen.add(key)

        caturl = (
            href if href.startswith("http") else urllib_parse.urljoin(site.url, href)
        )
        site.add_dir(name, caturl, "List", "")
    utils.eod()


@site.register()
def Tag(url):
    _taxonomy(url, "tag/")


@site.register()
def Studios(url):
    _taxonomy(url, "studio/")


@site.register()
def Stars(url):
    _taxonomy(url, "stars/")


@site.register()
def Lookupinfo(url):
    class PerverzijaLookup(utils.LookupInfo):
        def url_constructor(self, url):
            if "studio/" in url:
                return url
            if any(x in url for x in ["stars/", "tag/"]):
                return site.url + url

    lookup_list = [
        ("Studio", 'href="([^"]+)" rel="category tag">([^<]+)', ""),
        ("Tag", '(tag/[^"]+)" rel="tag">([^<]+)', ""),
        ("Actor", '(stars/[^"]+)" rel="tag">([^<]+)', ""),
    ]

    lookupinfo = PerverzijaLookup(site.url, url, "perverzija.List", lookup_list)
    lookupinfo.getinfo()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}".format(url, keyword.replace(" ", "%20"))
        List(url)


@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download=download, IA_check="skip")
    videohtml = utils.getHtml(url)
    match = re.compile(
        r'"player-embed"\s*>\s*?<iframe.*?src="([^"]+)"', re.IGNORECASE | re.DOTALL
    ).search(videohtml)
    if match:
        iframeurl = match.group(1)
        if "xtremestream" in iframeurl:
            vp.progress.update(25, "[CR]Loading video page[CR]")
            iframehtml = utils.getHtml(iframeurl, url)
            videoid = re.compile(
                r"""var\s*video_id\s*=\s*[`'"]([^`'"]+).+?var\s*m3u8_loader_url\s=\s[`'"]([^`'"]+)""",
                re.IGNORECASE | re.DOTALL,
            ).findall(iframehtml)[0]
            vp.progress.update(50, "[CR]Looking for qualities[CR]")
            m3u8html = utils.getHtml(videoid[1] + videoid[0], iframeurl)
            links = re.compile(
                r"resolution=\d+x(\d+)[^\n]*\n([^\s]+)", re.IGNORECASE | re.DOTALL
            ).findall(m3u8html)
            links = dict(links)
            videourl = utils.prefquality(links, sort_by=lambda x: int(x), reverse=True)
            vp.progress.update(75, "[CR]Loading selected quality[CR]")
            m3u8html = utils.getHtml(videourl, iframeurl)
            myplaylist = utils.TRANSLATEPATH("special://temp/myPlaylist.m3u8")
            with open(myplaylist, "w") as f:
                f.write(m3u8html)
            myparent = (
                "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-STREAM-INF:PROGRAM-ID=1\n{0}".format(
                    myplaylist
                )
            )
            videourl = utils.TRANSLATEPATH("special://temp/myParent.mp4")
            with open(videourl, "w") as f:
                f.write(myparent)
            vp.play_from_direct_link(videourl)
        elif vp.resolveurl.HostedMediaFile(iframeurl).valid_url():
            vp.play_from_link_to_resolve(iframeurl)
        else:
            utils.notify("Oh oh", "No other video hosts supported yet")
    else:
        utils.notify("Oh oh", "No video found")
