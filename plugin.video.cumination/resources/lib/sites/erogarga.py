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
import json
import sys
import xbmc
import xbmcgui
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.sites.spankbang import Playvid

site = AdultSite(
    "erogarga",
    "[COLOR hotpink]EroGarga[/COLOR]",
    "https://www.erogarga.com/",
    "erogarga.png",
    "erogarga",
)
site1 = AdultSite(
    "fulltaboo",
    "[COLOR hotpink]FullTaboo[/COLOR]",
    "https://fulltaboo.tv/",
    "fulltaboo.png",
    "fulltaboo",
)
site2 = AdultSite(
    "koreanpm",
    "[COLOR hotpink]Korean PornMovie[/COLOR]",
    "https://koreanpornmovie.com/",
    "koreanpm.png",
    "koreanpm",
)


def getBaselink(url):
    if "erogarga.com" in url:
        siteurl = site.url
    elif "fulltaboo.tv" in url:
        siteurl = site1.url
    elif "koreanpornmovie.com" in url:
        siteurl = site2.url
    return siteurl


@site.register(default_mode=True)
@site1.register(default_mode=True)
@site2.register(default_mode=True)
def Main(url):
    siteurl = getBaselink(url)
    if "erogarga" in siteurl:
        site.add_dir("[COLOR hotpink]Categories[/COLOR]", siteurl, "Cat", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", siteurl + "?s=", "Search", site.img_search
    )
    List(siteurl + "?filter=latest")


@site.register()
def List(url):
    siteurl = getBaselink(url)
    listhtml = utils.getHtml(url, siteurl)
    html = listhtml.split(">SHOULD WATCH<")[0]
    if "There is no data in this list" in html.split("New Albums")[0]:
        utils.notify(msg="No data found")
        return

    soup = utils.parse_html(html)

    if not soup:
        utils.eod()
        return

    # Find all video articles (skip photo galleries)
    articles = soup.find_all("article", attrs={"data-video-id": True})

    for article in articles:
        # Skip photo galleries
        if "type-photos" in utils.safe_get_attr(article, "class", default=""):
            continue

        link = article.find("a", href=True, title=True)
        if not link:
            continue

        videourl = utils.safe_get_attr(link, "href")
        name = utils.safe_get_attr(link, "title")

        if not videourl or not name:
            continue

        name = utils.cleantext(name)

        # Get thumbnail
        img_tag = link.find("img")
        img = utils.safe_get_attr(img_tag, "src")

        # Get duration
        duration_div = article.find("div", class_="duration")
        duration = ""
        if duration_div:
            duration = (
                utils.safe_get_text(duration_div, default="").replace("\n", "").strip()
            )

        # Check for HD quality
        hd_badge = article.find("span", class_="hd-video")
        quality = "HD" if hd_badge else ""

        # Create context menu
        cm = []
        cm_lookupinfo = (
            utils.addon_sys
            + "?mode=erogarga.Lookupinfo&url="
            + urllib_parse.quote_plus(videourl)
        )
        cm.append(
            ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + cm_lookupinfo + ")")
        )
        cm_related = (
            utils.addon_sys
            + "?mode=erogarga.Related&url="
            + urllib_parse.quote_plus(videourl)
        )
        cm.append(
            ("[COLOR deeppink]Related videos[/COLOR]", "RunPlugin(" + cm_related + ")")
        )

        site.add_download_link(
            name,
            videourl,
            "Play",
            img,
            name,
            contextm=cm,
            duration=duration,
            quality=quality,
        )

    # Handle pagination
    pagination = soup.find("div", class_="pagination")
    if pagination:
        # Check if there's a "Next" link
        next_link = pagination.find("a", string=re.compile("Next", re.IGNORECASE))
        if not next_link:
            # Alternative: find link after current page
            current_span = pagination.find("span", class_="current")
            if current_span:
                next_link = current_span.find_next_sibling("a")

        if next_link:
            next_url = utils.safe_get_attr(next_link, "href")
            if next_url:
                # Extract page number
                page_match = re.search(r"/page/(\d+)", next_url)
                page_num = page_match.group(1) if page_match else ""

                # Find last page
                last_link = pagination.find(
                    "a", string=re.compile("Last", re.IGNORECASE)
                )
                last_page = ""
                if last_link:
                    last_url = utils.safe_get_attr(last_link, "href")
                    last_match = re.search(r"/page/(\d+)", last_url)
                    last_page = last_match.group(1) if last_match else ""
                else:
                    # Find all pagination links and get the highest number
                    all_links = pagination.find_all("a", href=True)
                    max_page = 0
                    for link in all_links:
                        href = utils.safe_get_attr(link, "href")
                        match = re.search(r"/page/(\d+)", href)
                        if match:
                            max_page = max(max_page, int(match.group(1)))
                    last_page = str(max_page) if max_page > 0 else ""

                # Add next page with goto context menu
                contextmenu = []
                if page_num and last_page:
                    contexturl = (
                        utils.addon_sys
                        + "?mode=erogarga.GotoPage"
                        + "&list_mode=erogarga.List"
                        + "&url="
                        + urllib_parse.quote_plus(url)
                        + "&np="
                        + page_num
                        + "&lp="
                        + last_page
                    )
                    contextmenu.append(
                        (
                            "[COLOR violet]Goto Page[/COLOR]",
                            "RunPlugin(" + contexturl + ")",
                        )
                    )

                site.add_dir(
                    "[COLOR hotpink]Next Page...[/COLOR]",
                    next_url,
                    "List",
                    site.img_next,
                    contextm=contextmenu,
                )

    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp=0):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, "Enter Page number")
    if pg:
        url = url.replace("/page/{}".format(np), "/page/{}".format(pg))
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg="Out of range!")
            return
        contexturl = (
            utils.addon_sys
            + "?mode="
            + str(list_mode)
            + "&url="
            + urllib_parse.quote_plus(url)
        )
        xbmc.executebuiltin("Container.Update(" + contexturl + ")")


@site.register()
def Cat(url):
    siteurl = getBaselink(url)
    cathtml = utils.getHtml(url, siteurl)

    # Extract the tag cloud section
    cathtml = cathtml.split('class="wp-block-tag-cloud"')[-1].split("/section>")[0]

    soup = utils.parse_html(cathtml)

    if not soup:
        utils.eod()
        return

    # Find all category links with aria-label
    links = soup.find_all("a", href=True, attrs={"aria-label": True})

    for link in links:
        caturl = utils.safe_get_attr(link, "href")
        aria_label = utils.safe_get_attr(link, "aria-label")

        if not caturl or not aria_label:
            continue

        name = utils.cleantext(aria_label)
        site.add_dir(name, caturl, "List", "")

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}".format(url, keyword.replace(" ", "%20"))
        List(url)


@site.register()
def Play(url, name, download=None):
    siteurl = getBaselink(url)

    videohtml = utils.getHtml(url, siteurl)

    if "koreanporn" in url:
        vp = utils.VideoPlayer(name, download=download)
        soup = utils.parse_html(videohtml)
        iframe = soup.select_one("iframe[src]")
        if iframe:
            iframe_url = utils.safe_get_attr(iframe, "src")
            if iframe_url:
                videohtml = utils.getHtml(iframe_url, url)
                soup = utils.parse_html(videohtml)
        source = soup.select_one("source[src]")
        if source:
            source_url = utils.safe_get_attr(source, "src")
            if source_url:
                vp.play_from_direct_link(source_url + "|referer=" + url)
        return

    vp = utils.VideoPlayer(
        name, download=download, regex='"file":"([^"]+)"', direct_regex='file:"([^"]+)"'
    )

    # Parse HTML with BeautifulSoup to find iframe
    soup = utils.parse_html(videohtml)
    iframe = soup.select_one('iframe[src^="h"]')

    if not iframe:
        return

    playerurl = utils.safe_get_attr(iframe, "src")
    if not playerurl:
        return

    if vp.resolveurl.HostedMediaFile(playerurl).valid_url():
        vp.play_from_link_to_resolve(playerurl)
        return
    elif "/player-x.php?q=" in playerurl:
        vurl = playerurl.split("?q=")[-1]
        vurl = utils._bdecode(vurl)
        vurl = urllib_parse.unquote_plus(vurl)
        videolink = vurl.split('source src="')[-1].split('"')[0] + "|referer=" + siteurl
    elif "klcams.com" in playerurl:
        videohtml = utils.getHtml(playerurl, url)

        soup = utils.parse_html(videohtml)
        iframe = soup.select_one("iframe[src]")
        if not iframe:
            return

        videolink = utils.safe_get_attr(iframe, "src")
        if not videolink:
            return

        hdr = utils.base_hdrs.copy()
        hdr["Sec-Fetch-Dest"] = "iframe"
        klhtml = utils.getHtml(
            videolink, "https://klcams.com/", headers=hdr, error=True
        )
        packed = utils.get_packed_data(klhtml)

        vp.play_from_html(packed, videolink)
        return
    elif "phixxx.cc/player/play.php?vid=" in playerurl:
        vid = playerurl.split("?vid=")[-1]
        posturl = "https://phixxx.cc/player/ajax_sources.php"
        formdata = {"vid": vid, "alternative": "spankbang", "ord": "0"}
        data = utils.postHtml(posturl, form_data=formdata)
        data = data.replace(r"\/", "/")
        jsondata = json.loads(data)
        src = jsondata["source"]
        if len(src) > 0:
            videolink = src[0]["file"]
        else:
            formdata = {"vid": vid, "alternative": "mp4", "ord": "0"}
            data = utils.postHtml(posturl, form_data=formdata)
            data = data.replace(r"\/", "/")
            jsondata = json.loads(data)
            videolink = jsondata["source"][0]["file"]
    elif "pornflip.com" in playerurl:
        playerhtml = utils.getHtml(playerurl, url)
        soup = utils.parse_html(playerhtml)

        # Find all elements with data-*src* attributes
        src = {}
        for elem in soup.find_all(
            attrs=lambda x: x
            and any(k.startswith("data-") and "src" in k for k in x.keys())
        ):
            for attr in elem.attrs:
                if attr.startswith("data-") and "src" in attr:
                    src[attr] = elem[attr]

        if not src:
            return

        videolink = utils.selector("Select video", src)
        videolink = (
            videolink.replace("&amp;", "&") + "|referer=https://www.pornflip.com/"
        )
    elif "watcherotic.com" in playerurl:
        embedhtml = utils.getHtml(playerurl, url)
        # Keep regex for JavaScript variable extraction
        match = re.compile(
            r"video_url:\s*'([^']+)'", re.DOTALL | re.IGNORECASE
        ).findall(embedhtml)
        if match:
            videolink = match[0] + "|referer=" + siteurl
            vp.play_from_direct_link(videolink)
    else:
        playerhtml = utils.getHtml(playerurl, url)
        # Keep regex for JavaScript variable extraction (complex multi-variable pattern)
        match = re.compile(
            r"""var hash = '([^']+)'.+?var baseURL = '([^']+)'.+?getPhiPlayer\(hash,'([^']+)',"(\d+)"\);""",
            re.DOTALL | re.IGNORECASE,
        ).findall(playerhtml)
        if match:
            hash, baseurl, alternative, order = match[0]
            formdata = {"vid": hash, "alternative": alternative, "ord": order}
            data = utils.postHtml(baseurl + "ajax_sources.php", form_data=formdata)
            data = data.replace(r"\/", "/")
            jsondata = json.loads(data)
            videolink = jsondata["source"][0]["file"]
            if "blogger.com" in videolink:
                vp.direct_regex = '"play_url":"([^"]+)"'
                vp.play_from_site_link(videolink, url)
                return
        else:
            # Use BeautifulSoup for itemprop extraction
            soup = utils.parse_html(videohtml)
            itemprop_elem = soup.select_one('[itemprop="contentURL"][content]')
            videolink = utils.safe_get_attr(itemprop_elem, "content", default=playerurl)

    if "spankbang" in videolink:
        videolink = videolink.replace("/embed/", "/video/")
        Playvid(videolink, name, download=download)
    else:
        vp.play_from_direct_link(videolink)


@site.register()
def Lookupinfo(url):
    siteurl = getBaselink(url)
    html = utils.getHtml(url, siteurl)
    soup = utils.parse_html(html)

    if not soup:
        return

    # Extract tags
    tag_links = soup.select('a.label[href^="{}"][title]'.format(siteurl))
    tags = []
    for link in tag_links:
        tag_url = utils.safe_get_attr(link, "href")
        tag_name = utils.safe_get_attr(link, "title")
        if tag_url and tag_name:
            tags.append((tag_url, tag_name))

    # Extract actors
    actor_links = soup.select('a[href*="/actor"][title]')
    actors = []
    for link in actor_links:
        actor_url = utils.safe_get_attr(link, "href")
        actor_name = utils.safe_get_attr(link, "title")
        if actor_url and actor_name and "/actor" in actor_url:
            actors.append((actor_url, actor_name))

    # Build lookup list in LookupInfo format
    lookup_results = []
    if tags:
        lookup_results.append(("Tag", tags))
    if actors:
        lookup_results.append(("Actor", actors))

    # Display results using LookupInfo's display method
    if lookup_results:
        lookupinfo = utils.LookupInfo(
            siteurl, url, "{}.List".format(site.module_name), []
        )
        for category, items in lookup_results:
            for item_url, item_name in items:
                lookupinfo.additem(category, item_name, item_url)


@site.register()
def Related(url):
    contexturl = (
        utils.addon_sys
        + "?mode="
        + str("erogarga.List")
        + "&url="
        + urllib_parse.quote_plus(url)
    )
    sys.modules.get("xbmc", xbmc).executebuiltin("Container.Update(" + contexturl + ")")
