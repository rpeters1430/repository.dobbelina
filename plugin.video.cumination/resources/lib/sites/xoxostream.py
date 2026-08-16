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

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "xoxo",
    "[COLOR hotpink]XOXOstream[/COLOR]",
    "https://xoxostream.com/",
    "xoxostream.png",
    "xoxo",
    category="Amateur & Social",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Models[/COLOR]",
        site.url + "models/",
        "Models",
        utils.cum_image("cum-models.png"),
    )
    site.add_dir(
        "[COLOR hotpink]Tags[/COLOR]",
        site.url + "tags/",
        "Tags",
        utils.cum_image("cum-tags.png"),
    )

    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/{}/1/", "Search", site.img_search
    )
    List(site.url + "1/")


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.notify("XOXOstream", "No video found!")
        return

    soup = utils.parse_html(listhtml)
    items = soup.select("ul.videos_list > li, li[id]")
    if not items:
        utils.notify("XOXOstream", "No video found!")
        return

    found = False
    for item in items:
        a_tag = item.select_one("a")
        if not a_tag:
            continue
        videopage = utils.safe_get_attr(a_tag, "href")
        if not videopage:
            continue
        if videopage.startswith("//"):
            videopage = "https:" + videopage
        elif videopage.startswith("/"):
            videopage = site.url.rstrip("/") + videopage

        name = utils.safe_get_attr(a_tag, "title") or utils.safe_get_text(a_tag)
        name = utils.cleantext(name)

        img_tag = item.select_one("img")
        img = utils.get_thumbnail(img_tag) if img_tag else ""

        duration_el = item.select_one(".duration, span.duration")
        duration = utils.safe_get_text(duration_el) if duration_el else ""
        if duration and ";" in duration:
            duration = duration.split(";")[-1].strip()

        site.add_download_link(name, videopage, "Playvid", img, name, duration=duration)
        found = True

    if not found:
        utils.notify("XOXOstream", "No video found!")
        return

    next_page = soup.select_one('a.next, a.next-page, a.page-numbers.next, a[class*="next"]')
    if next_page:
        href = utils.safe_get_attr(next_page, "href")
        m = re.search(r"(\d+)/?$", href)
        if m:
            np = m.group(1)
            parts = url.rstrip("/").split("/")
            base = "/".join(parts[:-1]) + "/" + np + "/"
            site.add_dir(f"Next Page... ({np})", base, "List", site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = url.format(keyword.replace(" ", "_"))
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    html = utils.getHtml(url, site.url)

    m = re.search(r'<p id="description" class="([^"]+)"', html)
    if not m:
        raise ValueError("No videolink found!")

    class_data = m.group(1).split()

    m_val = class_data[0]
    d_val = class_data[1]
    q_val = class_data[2]
    tid = class_data[3]
    quality = class_data[4]
    secure_token = class_data[5]
    timestamp = class_data[6]

    video_url = (
        f"https://vdownload-{m_val}.sb-cd.com/"
        f"{d_val}/{q_val}/{tid}-{quality}.mp4"
        f"?secure={secure_token},{timestamp}"
        f"&m={m_val}&d={d_val}&_tid={tid}"
    )

    vp.play_from_direct_link(video_url)


@site.register()
def Tags(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    tags = soup.select("ul.tags_list a, ul.tags a")
    if not tags:
        raise ValueError("No Tags found!")

    for tag in tags:
        tag_url = utils.safe_get_attr(tag, "href")
        tag_name = utils.safe_get_text(tag)
        if not tag_url or not tag_name:
            continue
        site.add_dir(f"[COLOR hotpink]{tag_name}[/COLOR]", site.url + "tags/" + tag_url.lstrip("/"), "List", site.img_search)
    utils.eod()


@site.register()
def Models(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    items = soup.select("ul.models_list li, ul.models li, li:has(img)")
    if not items:
        raise ValueError("No Models found!")

    for item in items:
        a_tag = item.select_one("a")
        img_tag = item.select_one("img")
        if not a_tag:
            continue
        tag_url = utils.safe_get_attr(a_tag, "href")
        tag_name = utils.safe_get_text(a_tag) or utils.safe_get_text(item)
        if "AKA" in tag_name:
            tag_name = tag_name.split("AKA")[0].strip()
        img_src = utils.get_thumbnail(img_tag) if img_tag else ""
        if "/models/" not in img_src:
            continue
        if img_src.startswith("../"):
            img_src = site.url + img_src.lstrip("../")
        site.add_dir(f"[COLOR hotpink]{tag_name}[/COLOR]", site.url + "tags/" + tag_url.lstrip("/"), "List", img_src)
    utils.eod()
