"""
Cumination
Copyright (C) 2024 Team Cumination

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

try:
    from html import unescape
except ImportError:
    from six.moves.html_parser import HTMLParser

    unescape = HTMLParser().unescape
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "tube8",
    "[COLOR hotpink]Tube8[/COLOR]",
    "https://www.tube8.com/",
    "tube8.png",
    "tube8",
)
cookiehdr = {"Cookie": "age_verified=1"}


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "search/", "Search", site.img_search
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories.html",
        "Categories",
        site.img_cat,
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url, cookiehdr)

    if not listhtml or "Error Page Not Found" in listhtml:
        utils.eod()
        return

    # Parse HTML with BeautifulSoup
    soup = utils.parse_html(listhtml)

    # Extract video items - Tube8 uses class="video-box thumbnail-card"
    video_items = soup.select(".video-box.thumbnail-card")
    seen = set()

    for item in video_items:
        try:
            # Get the link element
            link = item.select_one("a.video-box-image")
            if not link:
                continue

            # Extract video URL
            video_url = utils.safe_get_attr(link, "href")
            if not video_url:
                continue

            # Make absolute URL if needed
            if video_url.startswith("/"):
                video_url = site.url[:-1] + video_url

            # Deduplicate videos - normalize URL and skip if already seen
            normalized = urllib_parse.urlsplit(video_url)
            normalized_url = urllib_parse.urlunsplit(
                (normalized.scheme, normalized.netloc, normalized.path, "", "")
            )
            if normalized_url in seen:
                continue
            seen.add(normalized_url)

            # Extract title from the title link
            title_link = item.select_one(".video-title-text")
            title = utils.safe_get_text(title_link) if title_link else ""
            if not title:
                # Fallback to image alt attribute
                img_tag = item.select_one("img.thumb-image")
                title = utils.safe_get_attr(img_tag, "alt") if img_tag else "Video"

            # Extract thumbnail image
            img_tag = item.select_one("img.thumb-image")
            img = utils.safe_get_attr(img_tag, "data-src", ["src", "data-poster"])

            # Extract duration
            duration_tag = item.select_one(".video-duration span")
            duration = utils.safe_get_text(duration_tag)

            # Add video to list
            site.add_download_link(
                title, video_url, "Playvid", img, "", duration=duration
            )

        except Exception as e:
            # Log error but continue processing other videos
            utils.kodilog("Tube8: Error parsing video item: " + str(e))
            continue

    # Extract pagination (Next Page link)
    # Tube8 uses numbered pagination links
    current_page = soup.select_one(".pagination_pages_list a.current")
    if current_page:
        # Get the next page number
        current_num = utils.safe_get_text(current_page)
        try:
            next_num = int(current_num) + 1
            # Look for the next page link
            next_page = soup.select_one(
                f'.pagination_pages_list a[href*="page/{next_num}"]'
            )
            if next_page:
                next_url = utils.safe_get_attr(next_page, "href")
                if next_url:
                    # Build next page URL
                    if next_url.startswith("/"):
                        next_url = site.url[:-1] + next_url

                    site.add_dir(
                        "Next Page ({})".format(next_num),
                        next_url,
                        "List",
                        site.img_next,
                    )
        except (ValueError, TypeError):
            pass

    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = urllib_parse.quote_plus(keyword)
        searchUrl = searchUrl + title + "/"
        List(searchUrl)


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url, cookiehdr)

    if not cathtml:
        utils.eod()
        return

    soup = utils.parse_html(cathtml)

    # Tube8 uses class="categoryBox" for category items
    categories = soup.select(".categoryBox")

    entries = []
    for category in categories:
        try:
            catpage = utils.safe_get_attr(category, "href")
            if not catpage:
                continue

            if catpage.startswith("/"):
                catpage = site.url[:-1] + catpage

            # Extract category name from the title section
            name_tag = category.select_one(".categoryTitle p")
            if name_tag:
                # Get only the first text node (category name, not "Category" subtitle)
                name_parts = list(name_tag.stripped_strings)
                name = name_parts[0] if name_parts else ""
            else:
                name = utils.safe_get_attr(category, "alt")

            if not name:
                continue

            # Extract thumbnail
            img_tag = category.select_one("img")
            img = utils.safe_get_attr(img_tag, "src", ["data-src"])

            entries.append((name, catpage, img, name.lower()))

        except Exception as e:
            utils.kodilog("Tube8: Error parsing category: " + str(e))
            continue

    # Sort alphabetically
    entries.sort(key=lambda item: item[3])

    for display_name, catpage, img, _ in entries:
        site.add_dir(display_name, catpage, "List", img, "")

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url, cookiehdr)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    src = _extract_best_source(html)
    if src:
        # Use the page URL as referer to satisfy CDN checks
        vp.play_from_direct_link("{0}|Referer={1}".format(src, url))
    else:
        vp.play_from_link_to_resolve(url)


def _extract_best_source(html):
    # Tube8 is an Aylo site - extract mediaDefinition with manifest endpoints
    match = re.search(r'mediaDefinition["\']?\s*:\s*(\[.*?\])', html, re.DOTALL)
    candidates = []
    if match:
        try:
            items = json.loads(match.group(1).replace("\\/", "/"))
            for item in items:
                url = item.get("videoUrl") or item.get("videoUrlMain")
                if not url:
                    continue

                # If URL is a manifest endpoint, fetch it to get actual video URLs
                if "/media/mp4/" in url or "/media/hls/" in url:
                    try:
                        manifest_data = utils.getHtml(url, site.url)
                        if manifest_data:
                            manifest_json = json.loads(manifest_data)
                            # Extract video URLs from manifest
                            for video in manifest_json:
                                video_url = video.get("videoUrl", "")
                                video_quality = video.get("quality", "")
                                if video_url:
                                    # Decode HTML entities (e.g., &amp; to &)
                                    video_url = unescape(video_url)
                                    candidates.append((str(video_quality), video_url))
                    except Exception as e:
                        utils.kodilog("Tube8: Error fetching manifest: " + str(e))
                        # Continue with the manifest URL itself as fallback
                        quality = (
                            item.get("quality") or item.get("defaultQuality") or ""
                        )
                        candidates.append((str(quality), unescape(url)))
                else:
                    quality = item.get("quality") or item.get("defaultQuality") or ""
                    candidates.append((str(quality), unescape(url)))
        except Exception as e:
            utils.kodilog("Tube8: Error parsing mediaDefinition: " + str(e))

    if not candidates:
        # Fallback: look for quality/url pairs used by Aylo inline JSON
        for quality, src in re.findall(
            r'"(?:quality|label)"\s*:\s*"?(\d{3,4})p?"?.*?"(?:videoUrl|src|url)"\s*:\s*"([^"]+)',
            html,
            re.IGNORECASE | re.DOTALL,
        ):
            candidates.append((quality, unescape(src.replace("\\/", "/"))))

    if not candidates:
        for src in re.findall(
            r"<source[^>]+src=[\"\\\']([^\"\\\']+)", html, re.IGNORECASE
        ):
            if any(ext in src for ext in (".mp4", ".m3u8")):
                candidates.append(("", unescape(src.replace("\\/", "/"))))
        for src in re.findall(
            r'https?://[^"\\\']+\.(?:mp4|m3u8)[^"\\\']*', html, re.IGNORECASE
        ):
            candidates.append(("", unescape(src.replace("\\/", "/"))))

    if not candidates:
        return ""

    def score(item):
        label = item[0]
        digits = "".join(ch for ch in label if ch.isdigit())
        return int(digits) if digits else 0

    best = sorted(candidates, key=score, reverse=True)[0][1]
    if best.startswith("//"):
        best = "https:" + best
    return best
