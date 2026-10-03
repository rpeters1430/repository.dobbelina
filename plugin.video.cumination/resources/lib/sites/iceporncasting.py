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

import re
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "iceporncasting",
    "[COLOR hotpink]IcePornCasting[/COLOR]",
    "https://iceporncasting.net/",
    "iceporncasting.png",
    "iceporncasting",
    category="Video Tubes",
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", site.url + "1f/channels/", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Pornstars[/COLOR]", site.url + "pornstars/", "Pornstars", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search)
    List(site.url + "latest-casting-videos/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml or "Nothing found" in listhtml or "search-no-results" in listhtml:
        utils.notify("Search", "No results found")
        utils.eod()
        return

    soup = utils.parse_html(listhtml)

    spec = {
        "items": "article.thumb-block, article",
        "url": {"selector": "a[href]", "attr": "href"},
        "title": {
            "selector": "a[title]",
            "attr": "title",
            "fallback_selectors": [".video-title", "h2", "h3"],
            "clean": True,
        },
        "thumbnail": {
            "selector": "img",
            "attr": "src",
            "fallback_attrs": ["data-src", "data-original"],
        },
        "duration": {"selector": ".duration", "text": True},
        "pagination": {
            "selector": "link[rel='next'], a[rel='next']",
            "text_matches": ["next"],
            "attr": "href",
        },
    }

    utils.soup_videos_list(site, soup, spec)
    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    articles = soup.select("article.thumb-block, article")
    seen = set()
    for art in articles:
        link = art.select_one("a[href]")
        if not link:
            continue
        href = utils.safe_get_attr(link, "href")
        href = urllib_parse.urljoin(site.url, href)
        if href in seen:
            continue
        seen.add(href)
        title_el = art.select_one(".cat-title") or link
        name = utils.cleantext(utils.safe_get_text(title_el) or utils.safe_get_attr(link, "title"))
        if not name or len(name) < 2:
            continue
        site.add_dir(name, href, "List", site.img_cat)

    next_el = soup.select_one("link[rel='next'], a[rel='next']")
    if not next_el:
        for a in soup.find_all("a"):
            if "next" in utils.safe_get_text(a).lower():
                next_el = a
                break
    if next_el:
        next_url = urllib_parse.urljoin(site.url, utils.safe_get_attr(next_el, "href"))
        site.add_dir("Next Page...", next_url, "Categories", site.img_next)

    utils.eod()


@site.register()
def Pornstars(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    articles = soup.select("article.thumb-block, article")
    seen = set()
    for art in articles:
        link = art.select_one("a[href]")
        if not link:
            continue
        href = utils.safe_get_attr(link, "href")
        href = urllib_parse.urljoin(site.url, href)
        if href in seen:
            continue
        seen.add(href)
        name_el = art.select_one(".cat-title") or link
        name = utils.cleantext(utils.safe_get_text(name_el) or utils.safe_get_attr(link, "title"))
        if not name or len(name) < 2:
            continue
        img = art.select_one("img")
        thumb = utils.safe_get_attr(img, "src") if img else site.img_cat
        site.add_dir(name, href, "List", thumb or site.img_cat)

    next_el = soup.select_one("link[rel='next'], a[rel='next']")
    if not next_el:
        for a in soup.find_all("a"):
            if "next" in utils.safe_get_text(a).lower():
                next_el = a
                break
    if next_el:
        next_url = urllib_parse.urljoin(site.url, utils.safe_get_attr(next_el, "href"))
        site.add_dir("Next Page...", next_url, "Pornstars", site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        List(url + urllib_parse.quote_plus(keyword))


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    videohtml = utils.getHtml(url, site.url)
    if not videohtml:
        utils.notify("Oh oh", "Could not load video page")
        return

    soup = utils.parse_html(videohtml)
    mirrors = []
    for ifr in soup.select("iframe[src]"):
        src = utils.safe_get_attr(ifr, "src")
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = urllib_parse.urljoin(site.url, src)
        if src and src not in mirrors:
            mirrors.append(src)

    embed_meta = soup.select_one("meta[itemprop='embedUrl'][content], meta[property='og:video'][content]")
    if embed_meta:
        content = utils.safe_get_attr(embed_meta, "content")
        if content.startswith("//"):
            content = "https:" + content
        elif content.startswith("/"):
            content = urllib_parse.urljoin(site.url, content)
        if content and content not in mirrors:
            mirrors.append(content)

    if not mirrors:
        utils.notify("Oh oh", "No video found")
        return

    # 1. XVideos extraction
    for mirror in mirrors:
        if "xvideos.com" in mirror:
            try:
                headers = {
                    "User-Agent": utils.USER_AGENT,
                    "Referer": "https://www.xvideos.com/",
                }
                embed_html = utils.getHtml(mirror, url, headers=headers)
                if not embed_html:
                    continue

                hls_match = re.search(r"html5player\.setVideoHLS\(['\"]([^'\"]+)['\"]\)", embed_html)
                if hls_match:
                    stream_url = hls_match.group(1)
                    vp.play_from_direct_link(f"{stream_url}|Referer=https://www.xvideos.com/")
                    return

                quality_matches = re.findall(
                    r'(https?://[^"\']+\.xvideos-cdn\.com[^"\']+video_(\d+)p\.mp4[^"\']*)',
                    embed_html,
                    re.IGNORECASE,
                )
                if quality_matches:
                    quality_matches.sort(key=lambda x: int(x[1]), reverse=True)
                    best_url = quality_matches[0][0]
                    vp.play_from_direct_link(f"{best_url}|Referer=https://www.xvideos.com/")
                    return
            except Exception as e:
                utils.kodilog(f"IcePornCasting: XVideos extraction error - {e}")

    # 2. Lulustream extraction
    for mirror in mirrors:
        if any(h in mirror for h in ("lulust.com", "lulustream", "luluvdo")):
            try:
                headers = {
                    "User-Agent": utils.USER_AGENT,
                    "Referer": url,
                }
                embed_html = utils.getHtml(mirror, url, headers=headers)
                if not embed_html:
                    continue

                target_html = embed_html
                packed = re.findall(r"(eval\(function\(p,a,c,k,e,d\).+?\))\s*</script>", embed_html, re.DOTALL)
                if packed:
                    from resources.lib import jsunpack
                    for p in packed:
                        try:
                            unpacked = jsunpack.unpack(p)
                            if unpacked:
                                target_html += "\n" + unpacked
                        except Exception:
                            pass

                m3u8_match = re.search(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', target_html)
                if m3u8_match:
                    stream_url = m3u8_match.group(1)
                    header_str = urllib_parse.urlencode({"User-Agent": utils.USER_AGENT, "Referer": "https://lulust.com/"})
                    vp.play_from_direct_link(f"{stream_url}|{header_str}")
                    return

                mp4_matches = re.findall(r'sources:\s*\[\s*\{[^}]*file:\s*["\']([^"\']+)["\']', target_html)
                if not mp4_matches:
                    mp4_matches = re.findall(r'["\'](https?://[^"\']+\.mp4[^"\']*)["\']', target_html)
                if mp4_matches:
                    stream_url = mp4_matches[0]
                    header_str = urllib_parse.urlencode({"User-Agent": utils.USER_AGENT, "Referer": "https://lulust.com/"})
                    vp.play_from_direct_link(f"{stream_url}|{header_str}")
                    return
            except Exception as e:
                utils.kodilog(f"IcePornCasting: Lulustream extraction error - {e}")

    vp.play_from_link_list(mirrors)


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Cat", r'<a[^>]+href="([^"]+/casting-channel/[^"]+)"[^>]*>([^<]+)<', ""),
        ("Tag", r'<a[^>]+href="([^"]+/tag/[^"]+)"[^>]*>([^<]+)<', ""),
    ]
    lookupinfo = utils.LookupInfo(site.url, url, "iceporncasting.List", lookup_list)
    lookupinfo.getinfo()
