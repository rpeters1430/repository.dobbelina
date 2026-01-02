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

import re
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "naughtyblog",
    "[COLOR hotpink]NaughtyBlog[/COLOR]  [COLOR red][Debrid only][/COLOR]",
    "https://www.naughtyblog.org/",
    "naughtyblog.png",
    "naughtyblog",
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
        "[COLOR hotpink]Sites[/COLOR]",
        site.url + "sites/?letter=",
        "SitesABC",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Popular pornstars[/COLOR]",
        site.url + "popular-pornstars/",
        "PornstarsAndSites",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Movies[/COLOR]",
        site.url + "category/movies/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url + "category/clips/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, "")
    soup = utils.parse_html(listhtml)
    posts = soup.select("article, .post, .post-content")
    if not posts:
        return
    for post in posts:
        tags_text = utils.safe_get_text(post.select_one(".post-author"), default="").lower()
        if any(tag in tags_text for tag in ["siterip", "onlyfans-leak"]):
            continue
        link = post.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href", default="")
        img_tag = post.select_one("img")
        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])
        name = utils.cleantext(
            utils.safe_get_attr(img_tag, "title", default=utils.safe_get_text(link))
        )
        title = utils.safe_get_text(post.select_one("strong"), default="")
        release = utils.safe_get_text(post.select_one("em"), default="")
        plot = utils.safe_get_text(post.select_one("p"), default="")
        plot = "{}\n{}\n{}".format(
            utils.cleantext(title), utils.cleantext(release), utils.cleantext(plot)
        )

        contextmenu = []
        contexturl = (
            utils.addon_sys
            + "?mode=naughtyblog.Lookupinfo"
            + "&url="
            + urllib_parse.quote_plus(videopage)
        )
        contextmenu.append(
            ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + contexturl + ")")
        )

        site.add_download_link(
            name, videopage, "Playvid", img, plot, contextm=contextmenu
        )

    next_link = soup.select_one('a[aria-label="Next Page"][href], a.next[href]')
    if next_link:
        next_url = utils.safe_get_attr(next_link, "href", default="")
        page_number = next_url.split("/")[-2] if next_url else ""
        site.add_dir(
            "Next Page (" + page_number + ")", next_url, "List", site.img_next
        )
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    sitehtml = utils.getHtml(url, site.url)
    downloads = re.compile(
        'id="download">(.*?)</div>', re.DOTALL | re.IGNORECASE
    ).findall(sitehtml)[0]
    sources = re.compile(
        r'href="([^"]+)"\s+?title="([^\s]+)\s', re.DOTALL | re.IGNORECASE
    ).findall(downloads)
    links = {}
    for link, hoster in sources:
        if utils.addon.getSetting("filter_hosters"):
            bypasslist = utils.addon.getSetting("filter_hosters").split(";")
            if any(x.lower() in link.lower() for x in bypasslist):
                continue
        if vp.resolveurl.HostedMediaFile(link).valid_url():
            linkparts = link.split("/")
            # quality = linkparts[-3] if link.endswith('.html') else linkparts[-2]
            hoster = "{0} {1}".format(hoster, linkparts[-1])
            links[hoster] = link
    videourl = utils.selector("Select link", links)
    if not videourl:
        vp.progress.close()
        return
    vp.play_from_link_to_resolve(videourl)


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(searchUrl, "Search")
    else:
        title = keyword.replace(" ", "+")
        searchUrl = searchUrl + title
        List(searchUrl)


@site.register()
def Categories(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    for item in soup.select(".pocetvideicat"):
        link = item.find_previous("a")
        catpage = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(utils.safe_get_text(link, default="").strip())
        videos = utils.safe_get_text(item, default="").strip()
        if not catpage or not name:
            continue
        name = "{0} - {1} videos".format(name, videos)
        site.add_dir(name, catpage, "List", "")
    utils.eod()


@site.register()
def SitesABC(url):
    letters = [
        "#",
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
    ]
    for letter in letters:
        sitepage = "{}{}".format(url, letter.lower() if letter != "#" else "0")
        site.add_dir(letter, sitepage, "PornstarsAndSites", "")
    utils.eod()


@site.register()
def PornstarsAndSites(url):
    listhtml = utils.getHtml(url)
    match = re.compile(
        '<li><a href="([^"]+)"[^>]+>([^<]+)<span[^>]+>([^<]+)<',
        re.DOTALL | re.IGNORECASE,
    ).findall(listhtml)
    for listpage, name, videos in match:
        name = utils.cleantext(name.strip())
        name = "{0} - {1} videos".format(name, videos.strip())
        if listpage.startswith("/"):
            listpage = site.url + listpage[1:]
        site.add_dir(name, listpage, "List", "")
    np = re.compile(
        'class="next page-numbers" href="([^"]+)">Next', re.DOTALL | re.IGNORECASE
    ).search(listhtml)
    if np:
        page_number = np.group(1).split("/")[-2]
        site.add_dir(
            "Next Page (" + page_number + ")",
            np.group(1),
            "PornstarsAndSites",
            site.img_next,
        )
    utils.eod()


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Cat", r'/((?:category|tag)/[^"]+)"\s*?rel="(?:category )*?tag">([^<]+)<', ""),
        ("Site", r'(site/[^"]+)"\s*?rel="tag">([^<]+)', ""),
        ("Model", r'/(pornstar/[^"]+)"\s*?rel="tag">([^<]+)<', ""),
    ]

    lookupinfo = utils.LookupInfo(site.url, url, "naughtyblog.List", lookup_list)
    lookupinfo.getinfo()
