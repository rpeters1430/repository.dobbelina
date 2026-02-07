"""
Cumination
Copyright (C) 2023 Cumination

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
from resources.lib import utils
from resources.lib.decrypters.kvsplayer import kvs_decode
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse
import xbmc
import xbmcgui

site = AdultSite(
    "celebsroulette",
    "[COLOR hotpink]CelebsRoulette[/COLOR]",
    "https://celebsroulette.com/",
    "celebsroulette.png",
    "celebsroulette",
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
        "[COLOR hotpink]Models[/COLOR]", site.url + "models/1/", "Models", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Tags[/COLOR]", site.url + "tags/", "Tags", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Playlists[/COLOR]",
        site.url
        + "playlists/?mode=async&function=get_block&block_id=list_playlists_common_playlists_list&sort_by=&from=01",
        "Playlist",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url
        + "search/?mode=async&function=get_block&block_id=list_videos_videos_list_search_result&category_ids=&sort_by=&from_videos=01&q=",
        "Search",
        site.img_search,
    )
    List(site.url + "latest-updates/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url)
    if "/models/" in url or "/categories/" in url or "/tags/" in url:
        listhtml = listhtml.split("New Naked Celebs Scenes")[0]
    soup = utils.parse_html(listhtml)

    thumbnails = utils.Thumbnails(site.name)
    for item in soup.select(".item"):
        link = item.select_one("a[href]")
        videopage = utils.safe_get_attr(link, "href", default="")
        if not videopage:
            continue
        name = utils.cleantext(
            utils.safe_get_attr(link, "title", default=utils.safe_get_text(link))
        )
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "data-original", ["data-src", "src"])
        if img:
            img = thumbnails.fix_img(img)

        cm = []
        cm_lookupinfo = (
            utils.addon_sys
            + "?mode="
            + str("celebsroulette.Lookupinfo")
            + "&url="
            + urllib_parse.quote_plus(videopage)
        )
        cm.append(
            ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + cm_lookupinfo + ")")
        )
        cm_related = (
            utils.addon_sys
            + "?mode="
            + str("celebsroulette.Related")
            + "&url="
            + urllib_parse.quote_plus(videopage)
        )
        cm.append(
            ("[COLOR deeppink]Related videos[/COLOR]", "RunPlugin(" + cm_related + ")")
        )

        site.add_download_link(name, videopage, "Playvid", img, name, contextm=cm)

    nextp = ""
    for anchor in soup.select("a"):
        if "next" in utils.safe_get_text(anchor, "").lower():
            nextp = utils.safe_get_text(anchor, "").strip()
            next_href = utils.safe_get_attr(anchor, "href", default="")
            if next_href:
                match = re.search(r"(\d+)", next_href)
                if match:
                    nextp = match.group(1)
            break

    if not nextp:
        nextp = re.findall(r':(\d+)">Next', listhtml, re.DOTALL | re.IGNORECASE)
        nextp = nextp[0] if nextp else ""

    if nextp:
        np = nextp
        pg = int(np) - 1
        r = re.search(r"/\d+/", url)
        if r:
            next_page = re.sub(r"/\d+/", "/{0}/".format(np), url)
        elif "from_videos={0:02d}".format(pg) in url:
            next_page = url.replace(
                "from_videos={0:02d}".format(pg), "from_videos={0:02d}".format(int(np))
            )
        else:
            next_page = url + "{0}/".format(np)
        lp = re.findall(r':(\d+)">Last', listhtml, re.DOTALL | re.IGNORECASE)
        lp = lp[0] if lp else ""
        cm_page = (
            utils.addon_sys
            + "?mode=celebsroulette.GotoPage"
            + "&url="
            + urllib_parse.quote_plus(next_page)
            + "&np="
            + str(np)
            + "&lp="
            + str(lp)
        )
        cm = [("[COLOR violet]Goto Page #[/COLOR]", "RunPlugin(" + cm_page + ")")]
        lp = "/" + lp if lp else ""
        site.add_dir(
            "Next Page (" + np + lp + ")",
            next_page,
            "List",
            site.img_next,
            contextm=cm,
        )
    utils.eod()


@site.register()
def GotoPage(url, np, lp=None):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        utils.notify(msg="Going to page " + str(pg))
        url = url.replace("/" + np + "/", "/" + str(pg) + "/")
        url = re.sub(r"&from([^=]*)=\d+", r"&from\1={}".format(pg), url, re.IGNORECASE)
        utils.notify(msg="Loading page " + str(url))
        contexturl = (
            utils.addon_sys
            + "?mode="
            + "celebsroulette.List&url="
            + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def ListPL(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    thumbnails = utils.Thumbnails(site.name)
    for item in soup.select(".item"):
        try:
            video = utils.safe_get_attr(item, "item", default="")
            link = item.select_one("a[href]")
            if not video and link:
                video = utils.safe_get_attr(link, "href", default="")
            if not video:
                continue
            
            img_tag = item.select_one("img")
            img = utils.safe_get_attr(img_tag, "data-original", ["data-src", "src"])
            img = thumbnails.fix_img(img) if img else ""
            
            name_tag = item.select_one(".title")
            name = utils.safe_get_text(name_tag) or utils.safe_get_text(link)
            
            if name:
                name = utils.cleantext(name)
                site.add_download_link(name, video, "Playvid", img, name)
        except Exception as e:
            utils.kodilog("Error parsing video item in ListPL: " + str(e))
            continue

    next_tag = soup.select_one('.pagination a:-soup-contains("Next")')
    if next_tag:
        next_url = utils.safe_get_attr(next_tag, "href")
        if next_url:
            # Handle page numbers
            np = ""
            m = re.search(r":(\d+)", utils.safe_get_text(next_tag))
            if m: np = m.group(1)
            
            lp = ""
            last_tag = soup.select_one('.pagination a:-soup-contains("Last")')
            if last_tag:
                m_last = re.search(r":(\d+)", utils.safe_get_text(last_tag))
                if m_last: lp = "/" + m_last.group(1)
                
            site.add_dir("Next Page ({}{})".format(np, lp), next_url, "ListPL", site.img_next)

    utils.eod()


@site.register()
def Playlist(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    for item in soup.select(".item"):
        try:
            link = item.select_one("a[href]")
            if not link: continue
            
            lpage = utils.safe_get_attr(link, "href", default="")
            if not lpage:
                continue
            lpage = urllib_parse.urljoin(site.url, lpage)
            
            img_tag = item.select_one("img")
            img = utils.safe_get_attr(img_tag, "data-original", ["data-src", "src"])
            
            name_tag = item.select_one(".title")
            name = utils.safe_get_text(name_tag) or utils.safe_get_text(link)
            
            count_tag = item.select_one(".videos")
            count = utils.safe_get_text(count_tag)
            
            if name:
                name = utils.cleantext(name)
                if count:
                    name = name + "[COLOR deeppink] {0}[/COLOR]".format(count)
                lpage += "?mode=async&function=get_block&block_id=playlist_view_playlist_view&sort_by=&from=01"
                site.add_dir(name, lpage, "ListPL", img)
        except Exception as e:
            utils.kodilog("Error parsing playlist item: " + str(e))
            continue

    next_tag = soup.select_one('.pagination a:-soup-contains("Next")')
    if next_tag:
        next_url = utils.safe_get_attr(next_tag, "href")
        if next_url:
            np = ""
            m = re.search(r":(\d+)", utils.safe_get_text(next_tag))
            if m: np = m.group(1)
            
            lp = ""
            last_tag = soup.select_one('.pagination a:-soup-contains("Last")')
            if last_tag:
                m_last = re.search(r":(\d+)", utils.safe_get_text(last_tag))
                if m_last: lp = "/" + m_last.group(1)
                
            site.add_dir("Next Page ({}{})".format(np, lp), next_url, "Playlist", site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "-")
        searchUrl = searchUrl + title
        List(searchUrl)


@site.register()
def Tags(url):
    html = utils.getHtml(url)
    soup = utils.parse_html(html)
    for link in soup.select('li a[href*="/tags/"]'):
        tagpage = utils.safe_get_attr(link, "href")
        name = utils.safe_get_text(link)
        if name and tagpage:
            name = utils.cleantext(name)
            site.add_dir(name, tagpage, "List")
    utils.eod()


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)
    for item in soup.select('a.item[href*="/categories/"]'):
        catpage = utils.safe_get_attr(item, "href")
        name = utils.safe_get_attr(item, "title")
        count_tag = item.select_one(".videos")
        videos = utils.safe_get_text(count_tag)
        
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src")
        
        if name and catpage:
            name = utils.cleantext(name) + " [COLOR deeppink]" + videos + "[/COLOR]"
            site.add_dir(name, catpage, "List", img)
    utils.eod()


@site.register()
def Models(url):
    html = utils.getHtml(url)
    soup = utils.parse_html(html)
    for item in soup.select('.item'):
        link = item if item.name == 'a' else item.select_one('a[href*="/models/"]')
        if not link: continue
        
        murl = utils.safe_get_attr(link, "href")
        name_tag = item.select_one(".title")
        name = utils.safe_get_text(name_tag)
        
        count_tag = item.select_one(".videos")
        videos = utils.safe_get_text(count_tag)
        
        img_tag = item.select_one("img")
        img = utils.safe_get_attr(img_tag, "src")
        
        if name and murl:
            name = utils.cleantext(name) + " [COLOR deeppink]" + videos + "[/COLOR]"
            site.add_dir(name, murl, "List", img)

    pagination = soup.select_one(".pagination")
    if pagination:
        next_tag = pagination.select_one(".next a")
        if next_tag:
            next_href = utils.safe_get_attr(next_tag, "href")
            np = ""
            m = re.search(r"/(\d+)/", next_href)
            if m: np = m.group(1)
            
            lp = ""
            last_tag = pagination.select_one(".last a")
            if last_tag:
                m_last = re.search(r"/(\d+)/", utils.safe_get_attr(last_tag, "href", ""))
                if m_last: lp = m_last.group(1)
                
            next_page = re.sub(r"/\d+/", "/{0}/".format(np), url) if np else next_href
            site.add_dir(
                "Next Page ( " + np + " / " + lp + " )", next_page, "Models", site.img_next
            )

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    html = utils.getHtml(url)
    surl = re.search(r"video_url:\s*'([^']+)'", html)
    referer = site.url
    if not surl:
        match = re.compile(
            r'<iframe[^>]+src="([^"]+/embed/[^"]+)"', re.DOTALL | re.IGNORECASE
        ).findall(html)
        if match:
            referer = match[0]
            html = utils.getHtml(match[0])
            surl = re.search(r"video_url:\s*'([^']+)'", html)
    if surl:
        surl = surl.group(1)
        if surl.startswith("function/"):
            license = re.findall(r"license_code:\s*'([^']+)", html)[0]
            surl = kvs_decode(surl, license)
        surl = utils.getVideoLink(surl)
        surl += "|Referer=" + referer
    else:
        vp.progress.close()
        return
    vp.progress.update(75, "[CR]Video found[CR]")
    vp.play_from_direct_link(surl)


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Model", '(models/[^"]+)">([^<]+)<', ""),
        ("Categorie", '(categories/[^"]+)">([^<]+)<', ""),
        ("Tag", '(tags/[^"]+)">([^<]+)<', ""),
    ]
    lookupinfo = utils.LookupInfo(site.url, url, "celebsroulette.List", lookup_list)
    lookupinfo.getinfo()


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("celebsroulette.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    xbmc.executebuiltin("Container.Update(" + contexturl + ")")
