"""
Cumination
Copyright (C) 2015 Whitecream

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
    "anybunny",
    "[COLOR hotpink]Anybunny[/COLOR]",
    "https://anybunny.tv/",
    "anybunny.png",
    "anybunny",
    category="Video Tubes",
    requires_flaresolverr=True,
)
DEFAULT_LIST_URL = site.url + "latest/"


def _extract_video_stream_url(html_content):
    """Extract direct playable video URL from anybunny HTML page."""
    if not html_content:
        return None

    soup = utils.parse_html(html_content)

    # 1. Check HTML5 <video><source src="..."> elements
    for source in soup.select("video source[src], source[src]"):
        src = source.get("src")
        if src and (".mp4" in src.lower() or ".m3u8" in src.lower() or "mov.anybunny.tv" in src):
            return src

    # 2. Check Playerjs file parameter (legacy format: prefer mp4 over m3u8 for compatibility)
    file_match = re.search(r'file\s*:\s*["\']([^"\']+)["\']', html_content, re.IGNORECASE)
    if file_match:
        file_val = file_match.group(1)
        quality_options = re.findall(r'\[(\d+)\](https?://[^,\[\s"\']+)', file_val)
        if quality_options:
            quality_options.sort(key=lambda x: int(x[0]), reverse=True)
            return quality_options[0][1]

        mp4_url = None
        m3u8_url = None
        for part in re.split(r'\s+or\s+', file_val):
            primary = part.split(':cast:')[0].strip()
            if '.mp4' in primary.lower() and not mp4_url:
                mp4_url = primary
            elif ('.m3u8' in primary.lower() or '/hls/' in primary.lower()) and not m3u8_url:
                m3u8_url = primary
        if mp4_url or m3u8_url:
            return mp4_url or m3u8_url

    # 3. Regex for direct media URLs on mov.anybunny.tv
    mov_match = re.search(r'["\'](https?://mov\.anybunny\.tv/[^"\']+)["\']', html_content)
    if mov_match:
        return mov_match.group(1)

    # 4. Fallback pattern search
    for pattern in [
        r'(https?://[^\s"\'\\,\]]+\.mp4(?:[^\s"\'\\,\]]*)?)',
        r'(https?://[^\s"\'\\,\]]+\.m3u8(?:[^\s"\'\\,\]]*)?)',
    ]:
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            return match.group(1).split(':cast:')[0].strip()

    return None


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Latest Videos[/COLOR]", site.url + "latest/", "List", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Top Rated[/COLOR]", site.url + "top-rated/", "List", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]", site.url, "Categories2", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url, "Search", site.img_search
    )
    List(DEFAULT_LIST_URL)
    utils.eod()


@site.register()
def List(url):
    try:
        listhtml, _ = utils.get_html_with_cloudflare_retry(url, referer=site.url)
    except Exception as exc:
        utils.kodilog("anybunny List: Fetch failed - {}".format(exc))
        listhtml = ""

    if not listhtml:
        utils.kodilog("anybunny List: Failed to fetch page")
        utils.eod()
        return

    soup = utils.parse_html(listhtml)

    # 1. Primary format: <li class="thumb">
    items = soup.select("li.thumb")
    for item in items:
        anchor = item.select_one("a.thumb_img_wrap") or item.find("a", href=re.compile(r"/movie/"))
        if not anchor:
            continue
        href = utils.safe_get_attr(anchor, "href")
        if not href:
            continue

        video_url = urllib_parse.urljoin(site.url, href)

        title_el = item.select_one(".thumb_title")
        title = utils.cleantext(title_el.get_text().strip()) if title_el else ""
        if not title:
            title = utils.cleantext(utils.safe_get_attr(anchor, "title") or "")
        if not title:
            slug = href.rstrip("/").split("/")[-1].replace(".html", "").replace("-", " ")
            title = utils.cleantext(slug.title())

        thumb = ""
        thumb_div = item.select_one(".thumb_img")
        if thumb_div and thumb_div.has_attr("style"):
            bg_match = re.search(r"url\(['\"]?([^'\")]+)['\"]?\)", thumb_div["style"])
            if bg_match:
                thumb = bg_match.group(1)

        if not thumb:
            img_tag = item.find("img")
            thumb = utils.get_thumbnail(img_tag) if img_tag else ""

        if thumb:
            thumb = urllib_parse.urljoin(site.url, thumb)
        else:
            thumb = site.image

        site.add_download_link(title, video_url, "Playvid", thumb, title)

    # 2. Legacy fallback: a.nuyrfe with /too/ hrefs
    if not items:
        for anchor in soup.select("a.nuyrfe[href*='/too/']"):
            href = utils.safe_get_attr(anchor, "href")
            if not href:
                continue
            video_url = urllib_parse.urljoin(site.url, href)
            img_tag = anchor.find("img")
            thumb = utils.get_thumbnail(img_tag) if img_tag else site.image
            title = utils.cleantext(utils.safe_get_attr(img_tag, "alt") if img_tag else "")
            if not title:
                title = utils.cleantext(video_url.split("-", 1)[-1].replace("_", " ").title())
            site.add_download_link(title, video_url, "Playvid", thumb, title)

    # Pagination: support ?page=N / &page=N and legacy a.topbtmsel2r
    next_link = soup.select_one("a.topbtmsel2r")
    if next_link and next_link.has_attr("href"):
        text = next_link.get_text().strip().lower()
        if not text or "next" in text or text in ("»", ">", "→"):
            next_url = urllib_parse.urljoin(site.url, next_link["href"])
            site.add_dir("Next Page", next_url, "List")
    elif len(items) >= 20:
        if "page=" in url:
            next_url = re.sub(r'([?&]page=)(\d+)', lambda m: "{}{}".format(m.group(1), int(m.group(2)) + 1), url)
            page_match = re.search(r'[?&]page=(\d+)', url)
            page_num = int(page_match.group(1)) + 1 if page_match else 2
        else:
            sep = "&" if "?" in url else "?"
            next_url = "{}{}page=2".format(url, sep)
            page_num = 2
        site.add_dir("[COLOR hotpink]Next Page...[/COLOR] ({})".format(page_num), next_url, "List", site.img_next)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(50, "[CR]Fetching video page...[CR]")
    pagehtml, _ = utils.get_html_with_cloudflare_retry(url, referer=site.url)

    if not pagehtml:
        utils.kodilog("anybunny Playvid: Failed to fetch page")
        utils.notify("Error", "Could not load video page")
        return

    video_url = _extract_video_stream_url(pagehtml)
    if not video_url:
        iframe_match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', pagehtml, re.IGNORECASE)
        if iframe_match:
            iframe_url = iframe_match.group(1)
            if not iframe_url.startswith("http"):
                iframe_url = urllib_parse.urljoin(site.url, iframe_url)
            iframe_html, _ = utils.get_html_with_cloudflare_retry(iframe_url, referer=url)
            if iframe_html:
                video_url = _extract_video_stream_url(iframe_html)

    if video_url:
        if "|" not in video_url:
            ua = urllib_parse.quote(utils.USER_AGENT, safe="")
            video_url += "|User-Agent={}&Referer={}".format(ua, site.url)
        vp.progress.update(85, "[CR]Playing video...[CR]")
        vp.play_from_direct_link(video_url)
    else:
        utils.kodilog("anybunny Playvid: No playable video URL found")
        utils.notify("Error", "Could not extract video URL")


@site.register()
def Categories2(url):
    try:
        cathtml, _ = utils.get_html_with_cloudflare_retry(url, referer=site.url)
    except Exception as exc:
        utils.kodilog("anybunny Categories2: Fetch failed - {}".format(exc))
        cathtml = ""

    if not cathtml:
        utils.kodilog("anybunny Categories2: Failed to fetch page")
        utils.eod()
        return
    soup = utils.parse_html(cathtml)

    entries = []
    # 1. Search tags / category links: /search/*.html
    for anchor in soup.select("a[href*='/search/']"):
        href = utils.safe_get_attr(anchor, "href") or ""
        if not href.endswith(".html"):
            continue
        slug = href.split("/search/", 1)[-1].replace(".html", "").replace("-", " ")
        name = utils.cleantext(utils.safe_get_text(anchor)) or utils.cleantext(slug.title())
        if not name or any(x in name.lower() for x in ["dmca", "abuse", "2257", "login"]):
            continue
        catpage = urllib_parse.urljoin(site.url, href)
        entries.append((name.lower(), name, catpage, site.image))

    # 2. Legacy fallback: a.nuyrfe
    if not entries:
        for anchor in soup.select("a.nuyrfe"):
            href = utils.safe_get_attr(anchor, "href") or ""
            if "/top/" not in href or "/too/" in href:
                continue

            stripped = href.rstrip("/")
            if stripped.endswith("/top"):
                continue

            try:
                catid = href.split("/top/", 1)[1].strip("/")
            except IndexError:
                continue

            if not catid or any(x in catid.lower() for x in ["dmca", "abuse", "2257", "login"]):
                continue

            img_tag = anchor.find("img")
            name = utils.cleantext(utils.safe_get_attr(img_tag, "alt") if img_tag else "")
            if not name:
                name = utils.cleantext(utils.safe_get_text(anchor))
            if not name:
                name = utils.cleantext(catid.replace("_", " ").title())
            if not name:
                continue

            img = utils.get_thumbnail(img_tag) if img_tag else ""
            if img:
                img = urllib_parse.urljoin(site.url, img)
            catpage = urllib_parse.urljoin(site.url, "top/" + catid)
            entries.append((name.lower(), name, catpage, img))

    seen = set()
    for _, display_name, catpage, img in sorted(entries):
        if catpage in seen:
            continue
        seen.add(catpage)
        site.add_dir(display_name, catpage, "List", img)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", keyword.strip()).strip("-").lower()
        search_slug = slug if "-" in slug else "{}-video".format(slug)
        search_url = urllib_parse.urljoin(site.url, "search/{}.html".format(search_slug))
        List(search_url)
