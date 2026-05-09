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
import base64
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "hpjav", "[COLOR hotpink]HPJav[/COLOR]", "https://hpjav.in/", "hpjav.png", "hpjav",
    category="JAV & Asian",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Censored[/COLOR]",
        site.url + "censored/",
        "List",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Unensored[/COLOR]",
        site.url + "uncensored/",
        "List",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Amateur[/COLOR]", site.url + "amature/", "List", site.img_search
    )
    site.add_dir(
        "[COLOR hotpink]FC2 PPV[/COLOR]", site.url + "fc2ppv/", "List", site.img_search
    )
    site.add_dir("[COLOR hotpink]VR[/COLOR]", site.url + "vr/", "List", site.img_search)
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )

    List(site.url + "trend/")


@site.register()
def List(url):
    try:
        listhtml, _ = utils.get_html_with_cloudflare_retry(
            url, referer=site.url
        )
    except Exception as e:
        utils.kodilog("hpjav List error: {}".format(str(e)))
        utils.eod()
        return

    if not listhtml or len(listhtml.strip()) < 32:
        utils.notify("HPJav", "Access blocked/challenged")
        utils.eod()
        return

    soup = utils.parse_html(listhtml)

    # Find all video links on listing cards.
    # Video pages usually have a slug after the category, e.g. /censored/video-slug/
    # Category pages are just /censored/, /uncensored/, etc.
    all_links = soup.select(
        'a[href*="/censored/"], a[href*="/uncensored/"], a[href*="/amature/"], a[href*="/fc2ppv/"], a[href*="/vr/"]'
    )
    
    video_links = []
    for link in all_links:
        href = utils.safe_get_attr(link, "href")
        if not href:
            continue
        
        # Check if it looks like a video page (more than just the category part)
        path = urllib_parse.urlparse(href).path.strip("/")
        parts = path.split("/")
        if len(parts) >= 2:
            video_links.append(link)

    for link in video_links:
        videopage = utils.safe_get_attr(link, "href")
        if not videopage:
            continue

        # Get image
        img_tag = link.select_one("img")
        img = utils.safe_get_attr(img_tag, "src")

        # Get duration
        duration_tag = link.select_one(".post-list-duration")
        duration = utils.safe_get_text(duration_tag, "")
        # Clean duration (remove "min." suffix)
        if duration and duration.endswith("min."):
            duration = duration[:-4].strip()

        # Get title from span/alt/text
        title_tag = link.select_one("span")
        name = utils.safe_get_text(title_tag, "")
        if not name:
            name = utils.safe_get_attr(img_tag, "alt", default="")
        if not name:
            name = utils.safe_get_text(link, "")
        name = utils.cleantext(name)

        if name and videopage:
            site.add_download_link(
                name, videopage, "Playvid", img, name, duration=duration
            )

    # Handle pagination
    pagenavi = soup.select_one("div.wp-pagenavi")
    if pagenavi:
        next_link = pagenavi.select_one('a[title="Next Page"]')
        if next_link:
            pgurl = utils.safe_get_attr(next_link, "href")
            # Get current page text
            pages_span = pagenavi.select_one("span.pages")
            pgtxt = utils.safe_get_text(pages_span, "")
            if pgurl:
                site.add_dir(
                    "Next Page.. (Currently in Page {0})".format(pgtxt),
                    pgurl,
                    "List",
                    site.img_next,
                )

    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "+")
        searchUrl = searchUrl + title
        List(searchUrl)


@site.register()
def Cat(url):
    cathtml = utils.getHtml(url, site.url)
    match = re.compile(
        r'title="[^"]+"\s*href="([^"]+)">([^<]+).+?(\([^<]+)', re.DOTALL | re.IGNORECASE
    ).findall(cathtml)
    for catpage, name, videos in match:
        name = name + " [COLOR deeppink]" + videos + "[/COLOR]"
        if catpage.startswith("/"):
            catpage = urllib_parse.urljoin(site.url, catpage)
        site.add_dir(name, catpage, "List", "")
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, site.url)
    
    # Extract packed data
    packed_data = utils.get_packed_data(videopage)
    all_data = videopage + packed_data
    
    # Look for common embed patterns
    # 1. Direct URLs in scripts or attributes
    eurls = re.findall(r'https?://[^"\'\s>]+/(?:embed|e|v|f)/[a-zA-Z0-9]+', all_data)
    
    # 2. URLs in iframe src
    iframes = re.findall(r'<iframe.+?src="([^"]+)"', all_data)
    eurls.extend(iframes)

    sources = {}
    for eurl in eurls:
        if eurl.startswith("//"):
            eurl = "https:" + eurl
        
        # Basic cleanup
        eurl = eurl.split('"')[0].split("'")[0]
        
        parsed = urllib_parse.urlparse(eurl)
        hoster = parsed.netloc
        if not hoster:
            continue
            
        if vp.resolveurl.HostedMediaFile(eurl):
            # Use hoster as label, or part of the URL if hoster is repeated
            label = hoster
            if label in sources and sources[label] != eurl:
                label = "{0} ({1})".format(hoster, parsed.path.split('/')[1])
            sources[label] = eurl

    if sources:
        videourl = utils.selector("Select Hoster", sources)
        if videourl:
            vp.play_from_link_to_resolve(videourl)
            return

    vp.progress.close()
    utils.notify("Oh Oh", "No playable Videos found")


def hpjav_decode(a1):
    def c(c1, c4, c5):
        c6 = ""
        for i, item in enumerate(c1):
            k = i % c4
            c6 += chr(ord(item) ^ ord(c5[k]))
        return c6

    a1 = base64.b64decode(a1).decode()
    a5 = "f41g(*^opPklaPk6w3*K5q1la&"
    a6 = c(a1, len(a5), a5)
    return a6
