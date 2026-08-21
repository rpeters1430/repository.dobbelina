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

import json
import re
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.jsunpack import unpack

site = AdultSite(
    "xtapesla",
    "[COLOR hotpink]XTapes.la[/COLOR]",
    "https://xtapes.la/",
    "xtapes.png",
    "xtapesla",
    category="Video Tubes",
)

xtapes_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://xtapes.la/",
}


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "?s=",
        "Search",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Networks[/COLOR]",
        site.url,
        "Networks",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Full Movies[/COLOR]",
        site.url + "tag/full-movie/",
        "List",
        site.img_cat,
    )
    List(site.url + "?display=tube&filtre=date")


@site.register()
def List(url, page=1):
    html = utils.getHtml(url, site.url, headers=xtapes_headers)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    items = soup.select("li.border-radius-5, li.border-radius, .content-widget li")

    found = False
    for item in items:
        link = item.select_one("a[href]")
        if not link:
            continue
        v_url = utils.safe_get_attr(link, "href")
        if not v_url or v_url.rstrip("/") == site.url.rstrip("/"):
            continue
        v_url = urllib_parse.urljoin(site.url, v_url)

        title = (
            utils.safe_get_attr(link, "title")
            or utils.safe_get_attr(item.select_one("img"), "title")
            or utils.safe_get_attr(item.select_one("img"), "alt")
            or utils.safe_get_text(link)
            or "Video"
        )
        title = utils.cleantext(title)

        img_tag = item.select_one("img")
        v_thumb = (
            utils.safe_get_attr(img_tag, "src", ["data-src", "data-lazy"])
            if img_tag
            else site.img_cat
        )

        time_tag = item.select_one(".time-infos, [class*='time']")
        duration = utils.safe_get_text(time_tag) or ""

        site.add_download_link(
            title, v_url, "Playvid", v_thumb, title, duration=duration
        )
        found = True

    if not found:
        utils.eod()
        return

    next_link = soup.select_one(
        "a.next.page-numbers, .pagination a.next, a[rel='next'], a.next"
    )
    if next_link:
        np_url = utils.safe_get_attr(next_link, "href")
        if np_url:
            np_url = urllib_parse.urljoin(site.url, np_url)
            site.add_dir(
                "[COLOR hotpink]Next Page >>[/COLOR]",
                np_url,
                "List",
                site.img_next,
            )

    utils.eod()


@site.register()
def Networks(url):
    html = utils.getHtml(url, site.url, headers=xtapes_headers)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    seen = set()

    for item in soup.select("li.menu-item-has-children ul.sub-menu li a, ul.sub-menu li a, .networks a"):
        href = utils.safe_get_attr(item, "href")
        name = utils.safe_get_text(item) or utils.safe_get_attr(item, "title")
        if not href or not name or href in seen:
            continue
        seen.add(href)
        full_url = urllib_parse.urljoin(site.url, href)
        site.add_dir("[COLOR hotpink]" + utils.cleantext(name) + "[/COLOR]", full_url, "List", site.img_cat)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = site.url + "?s=" + urllib_parse.quote_plus(keyword)
        List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    video_html = utils.getHtml(url, site.url, headers=xtapes_headers)
    if not video_html:
        vp.progress.close()
        utils.notify("XTapes", "Video page not found")
        return

    soup = utils.parse_html(video_html)
    iframe = soup.select_one("iframe[src], IFRAME[SRC]")
    if not iframe:
        match = re.search(r'iframe\s+src=["\']([^"\']+)["\']', video_html, re.IGNORECASE)
        iframe_src = match.group(1) if match else None
    else:
        iframe_src = utils.safe_get_attr(iframe, "src")

    if not iframe_src:
        vp.progress.close()
        utils.notify("XTapes", "Player iframe not found")
        return

    if iframe_src.startswith("//"):
        iframe_src = "https:" + iframe_src

    vp.progress.update(50, "[CR]Extracting player stream[CR]")
    iframe_html = utils.getHtml(
        iframe_src,
        url,
        headers={"User-Agent": xtapes_headers["User-Agent"], "Referer": url},
    )
    if not iframe_html:
        vp.progress.close()
        utils.notify("XTapes", "Failed to load player iframe")
        return

    eval_match = re.search(
        r"(eval\(function\(p,a,c,k,e,d\).+?)(?:<\/script>|$)",
        iframe_html,
        re.DOTALL,
    )
    if not eval_match:
        vp.progress.close()
        utils.notify("XTapes", "Player script not found")
        return

    try:
        unpacked = unpack(eval_match.group(1))
    except Exception as e:
        vp.progress.close()
        utils.notify("XTapes", "Unpack failed: {}".format(e))
        return

    links_match = re.search(r"var\s+links\s*=\s*(\{.*?\});", unpacked, re.DOTALL)
    if not links_match:
        vp.progress.close()
        utils.notify("XTapes", "Stream links not found")
        return

    try:
        links = json.loads(links_match.group(1))
    except Exception:
        vp.progress.close()
        utils.notify("XTapes", "Error parsing stream links")
        return

    master = links.get("hls2") or links.get("hls") or links.get("file")
    if not master:
        vp.progress.close()
        utils.notify("XTapes", "No HLS link available")
        return

    master_data = utils.getHtml(
        master,
        iframe_src,
        headers={"User-Agent": xtapes_headers["User-Agent"], "Referer": iframe_src},
    )

    sources = {}
    if master_data:
        base = master.rsplit("/", 1)[0] + "/"
        for block in re.findall(
            r"(#EXT-X-STREAM-INF[^\n]+)\n([^\n]+\.m3u8[^\n]*)", master_data
        ):
            inf_line, url_line = block
            rez = re.search(r"RESOLUTION=\d+x(\d+)", inf_line)
            height = rez.group(1) if rez else "Default"
            variant_url = urllib_parse.urljoin(base, url_line.strip())
            sources[height] = variant_url

    selected_url = None
    if sources:
        try:
            selected_url = utils.prefquality(
                sources,
                sort_by=lambda x: int(re.sub(r"\D", "", x) or 0),
                reverse=True,
            )
        except Exception:
            selected_url = utils.selector("Select Quality", sources, reverse=True)

    if not selected_url:
        selected_url = master

    play_url = selected_url + "|User-Agent={0}&Referer={1}".format(
        urllib_parse.quote(xtapes_headers["User-Agent"], safe=""),
        urllib_parse.quote(iframe_src, safe=""),
    )

    vp.play_from_direct_link(play_url)
    vp.progress.close()
