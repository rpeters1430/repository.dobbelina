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
import requests
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "pornhoarder",
    "[COLOR hotpink]PornHoarder[/COLOR]",
    "https://pornhoarder.io/",
    "pornhoarder.png",
    "pornhoarder",
)

ph_headers = {
    "Origin": site.url[:-1],
    "User-Agent": utils.USER_AGENT,
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": "pornhoarder_settings=0---0---1---0",
}


def _extract_srcset_url(value):
    if not value:
        return ""
    first = value.split(",")[0].strip()
    return first.split(" ")[0].strip()


def _extract_search_term(url):
    match = re.search(r"[?&]search=([^&]+)", url)
    if not match:
        return ""
    return urllib_parse.unquote(match.group(1))


def Createdata(page=1, search=""):
    return [
        ("search", search),
        ("sort", "0"),
        ("date", "0"),
        ("servers[]", "21"),
        ("servers[]", "40"),
        ("servers[]", "12"),
        ("servers[]", "35"),
        ("servers[]", "25"),
        ("servers[]", "41"),
        ("servers[]", "46"),
        ("servers[]", "17"),
        ("servers[]", "44"),
        ("servers[]", "42"),
        ("servers[]", "43"),
        ("servers[]", "29"),
        ("author", "0"),
        ("page", page),
    ]


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories/",
        "Categories",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Studios[/COLOR]",
        site.url + "porn-studios/",
        "Studios",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Pornstars[/COLOR]",
        site.url + "porn-stars/",
        "Pornstars",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/?search={0}",
        "Search",
        site.img_search,
    )
    List(site.url + "ajax_search.php", page=1)
    utils.eod()


@site.register()
def List(url, page=1, section=None):
    search = "" if isinstance(url, str) and url.startswith("https://") else url
    siteurl = section if section else site.url

    if isinstance(url, str) and url.startswith("https://"):
        if "ajax_search.php" in url:
            ajax_url = url
            referer = siteurl
        else:
            ajax_url = siteurl + "ajax_search.php"
            referer = url
            search = _extract_search_term(url)
    else:
        ajax_url = siteurl + "ajax_search.php"
        referer = siteurl

    headers = dict(ph_headers)
    headers["Referer"] = referer

    listhtml = utils.postHtml(ajax_url, form_data=Createdata(page, search), headers=headers)
    if not listhtml:
        fallback_url = url
        if not isinstance(url, str) or not url.startswith("https://"):
            fallback_url = siteurl + "search/?search={}".format(urllib_parse.quote(search))
        listhtml = utils.getHtml(fallback_url)

    soup = utils.parse_html(listhtml)
    links = soup.select("article a[href], a[href]")
    for link in links:
        videourl = utils.safe_get_attr(link, "href", default="")
        if not videourl or not any(
            marker in videourl
            for marker in ("/watch/", "/pornvideo/", "/videos/", "/video/")
        ):
            continue

        videourl = urllib_parse.urljoin(siteurl, videourl)
        img = ""
        for img_tag in link.select("img"):
            src = utils.safe_get_attr(
                img_tag,
                "data-src",
                ["data-original", "data-lazy", "data-srcset", "srcset", "src"],
            )
            src = _extract_srcset_url(src)
            alt = utils.safe_get_attr(img_tag, "alt", default="").lower()
            if "logo" in src.lower() or "logo" in alt:
                continue
            img = src
            if img:
                break
        if img and img.startswith("/"):
            img = urllib_parse.urljoin(siteurl, img)

        name = utils.cleantext(utils.safe_get_text(link.select_one("h1"), default=""))
        if not name:
            name = utils.cleantext(utils.safe_get_attr(link, "title", default=""))
        if not name:
            h2 = link.select_one("h2")
            name = utils.cleantext(h2.get_text()) if h2 else ""
        if not name:
            name = utils.cleantext(utils.safe_get_text(link))
        if not name:
            continue

        duration = utils.safe_get_text(link.select_one(".length"), default="")
        if not duration:
            duration = utils.safe_get_text(link.select_one(".video-length"), default="")

        site.add_download_link(
            name, videourl, "Playvid", img, name, duration=duration
        )

    next_page = ""
    next_button = soup.select_one(".next .pagination-button[data-page]")
    if next_button:
        next_page = utils.safe_get_attr(next_button, "data-page", default="")
    if not next_page:
        next_link = soup.select_one(".pagination .next a[href]")
        if next_link:
            next_page = utils.safe_get_attr(next_link, "data-page", default="").strip()
            if not next_page:
                next_page = utils.safe_get_text(next_link, default="").strip()
            if not next_page:
                href = utils.safe_get_attr(next_link, "href", default="")
                match = re.search(r"/page/(\d+)/", href)
                if match:
                    next_page = match.group(1)

    if next_page:
        site.add_dir(
            "Next Page ({})".format(next_page),
            url,
            "List",
            site.img_next,
            page=int(next_page),
            section=siteurl,
        )

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download=download)
    html = utils.getHtml(url, site.url)
    
    # Extract embed URL from json-ld or iframe
    embed_url = "".join(re.findall(r'"embedUrl":\s*"([^"]+)"', html))
    if not embed_url:
        embed_url = utils.safe_get_attr(utils.parse_html(html).select_one("iframe[src]"), "src", default="")
        
    if not embed_url:
        # Try to find any player.php link
        embed_url = "".join(re.findall(r'https?://pornhoarder\.net/player\.php\?video=[^"\'\s>]+', html))

    if not embed_url:
        vp.progress.close()
        return

    if embed_url.startswith("//"):
        embed_url = "https:" + embed_url
    elif embed_url.startswith("/"):
        embed_url = urllib_parse.urljoin(site.url, embed_url)

    # New player endpoints require a POST to resolve the final host iframe.
    if "pornhoarder.net/player" in embed_url:
        headers = dict(ph_headers)
        headers["Referer"] = url
        player_html = utils.postHtml(embed_url, headers=headers, form_data={"play": ""})
        if not player_html:
            player_html = utils.getHtml(embed_url, url)

        iframe_match = re.findall(
            r"""<iframe.+?src\s*=\s*["']([^'"]+)""",
            player_html,
            re.DOTALL | re.IGNORECASE,
        )
        if iframe_match:
            embed_url = iframe_match[0]
            if embed_url.startswith("//"):
                embed_url = "https:" + embed_url
            elif embed_url.startswith("/"):
                embed_url = urllib_parse.urljoin(site.url, embed_url)

    vp.play_from_link_to_resolve(embed_url)


@site.register()
def Categories(url):
    html = utils.getHtml(url)
    soup = utils.parse_html(html)
    for item in soup.select(".video.category, article"):
        link = item.select_one("a[href]")
        if not link:
            continue

        caturl = utils.safe_get_attr(link, "href", default="")
        search_term = _extract_search_term(caturl)
        if not search_term:
            continue

        name = utils.cleantext(utils.safe_get_text(item.select_one("h2")))
        img_tag = item.select_one("img")
        img = utils.get_thumbnail(img_tag)
        if img and img.startswith("/"):
            img = urllib_parse.urljoin(site.url, img)

        site.add_dir(name, search_term, "List", img)

    next_link = soup.select_one(".pagination .next a[href]")
    if next_link:
        page_number = utils.safe_get_text(next_link, default="").strip()
        if page_number:
            site.add_dir(
                "Next Page ({})".format(page_number),
                utils.safe_get_attr(next_link, "href", default=""),
                "Categories",
                site.img_next,
            )
    utils.eod()


@site.register()
def Studios(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    for item in soup.select(".video.category"):
        link = item.select_one("a.video-link")
        if not link: continue
        
        sturl = utils.safe_get_attr(link, "href", default="")
        sturl = urllib_parse.urljoin(site.url, sturl)
        
        name = utils.cleantext(utils.safe_get_text(item.select_one("h2")))
        site.add_dir(name, sturl, "List", "")
    utils.eod()


@site.register()
def Pornstars(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    for item in soup.select(".video.category"):
        link = item.select_one("a.video-link")
        if not link: continue
        
        psurl = utils.safe_get_attr(link, "href", default="")
        psurl = urllib_parse.urljoin(site.url, psurl)
        
        name = utils.cleantext(utils.safe_get_text(item.select_one("h2")))
        img_tag = item.select_one("img")
        img = utils.get_thumbnail(img_tag)
        if img and img.startswith("/"):
            img = urllib_parse.urljoin(site.url, img)
            
        site.add_dir(name, psurl, "List", img)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        if "{0}" in url:
            search_url = url.format(urllib_parse.quote(keyword))
            List(search_url)
        else:
            List(keyword, page=1)
