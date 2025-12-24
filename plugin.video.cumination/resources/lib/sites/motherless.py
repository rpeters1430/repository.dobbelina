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
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "motherless",
    "[COLOR hotpink]Motherless[/COLOR]",
    "https://motherless.com/",
    "motherless.png",
    "motherless",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "search/videos?term=",
        "Search",
        site.img_search,
    )
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]",
        site.url + "categories",
        "Categories",
        site.img_cat,
    )
    # Show Recent Videos by default and as an explicit folder
    site.add_dir(
        "[COLOR hotpink]Recent Videos[/COLOR]",
        site.url + "videos/recent",
        "List",
        site.img_cat,
    )
    List(site.url + "videos/recent")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)

    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    video_items = soup.select(".desktop-thumb.video, .thumb-container.video")
    seen = set()

    for item in video_items:
        try:
            # Get the link element
            link = item.select_one("a.img-container")
            if not link:
                # Try alternative selector
                link = item.select_one('a[href*="motherless.com/"]')
            if not link:
                continue

            # Extract video URL
            video_url = utils.safe_get_attr(link, "href")
            if not video_url:
                continue

            # Make absolute URL if needed
            if video_url.startswith("/"):
                video_url = site.url[:-1] + video_url
            elif not video_url.startswith("http"):
                video_url = site.url + video_url

            # Normalize URL to drop query params to prevent duplicates
            parsed = urllib_parse.urlsplit(video_url)
            canonical_url = urllib_parse.urlunsplit(
                (parsed.scheme, parsed.netloc, parsed.path, "", "")
            )
            if canonical_url in seen:
                continue
            seen.add(canonical_url)
            video_url = canonical_url

            # Extract title from the caption link
            title_link = item.select_one("a.caption.title")
            title = utils.safe_get_text(title_link) if title_link else ""
            if not title:
                # Fallback to title attribute
                title = utils.safe_get_attr(title_link, "title") if title_link else ""
            if not title:
                # Fallback to data-codename
                title = utils.safe_get_attr(item, "data-codename", default="Video")

            # Extract thumbnail image
            img_tag = item.select_one("img.static")
            img = utils.safe_get_attr(img_tag, "src", ["data-src"])
            if not img:
                # Try alternative image selector
                img_tag = item.select_one('img[src*="thumbs"]')
                img = utils.safe_get_attr(img_tag, "src")

            # Extract duration
            duration_tag = item.select_one("span.size")
            duration = utils.safe_get_text(duration_tag)

            # Add video to list
            site.add_download_link(
                title, video_url, "Playvid", img, "", duration=duration
            )

        except Exception as e:
            # Log error but continue processing other videos
            utils.kodilog("Motherless: Error parsing video item: " + str(e))
            continue

    # Extract pagination (Next Page link)
    # Motherless uses <link rel="next"> in header and also pagination div
    next_link = soup.select_one('link[rel="next"]')
    if next_link:
        next_url = utils.safe_get_attr(next_link, "href")
        if next_url:
            # Extract page number for display
            page_match = re.search(r"page=(\d+)", next_url)
            page_num = page_match.group(1) if page_match else ""

            # Make absolute URL if needed
            if next_url.startswith("/"):
                next_url = site.url[:-1] + next_url

            label = "Next Page ({})".format(page_num) if page_num else "Next Page"
            site.add_dir(label, next_url, "List", site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = urllib_parse.quote_plus(keyword)
        searchUrl = searchUrl + title
        List(searchUrl)


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)

    if not cathtml:
        utils.eod()
        return

    soup = utils.parse_html(cathtml)

    # Motherless categories are links with pattern /porn/[category]/videos
    category_links = soup.select('a[href*="/porn/"][href*="/videos"]')

    entries = []
    seen_categories = set()  # Prevent duplicates

    for cat_link in category_links:
        try:
            catpage = utils.safe_get_attr(cat_link, "href")
            if not catpage or catpage in seen_categories:
                continue

            seen_categories.add(catpage)

            # Make absolute URL if needed
            if catpage.startswith("/"):
                catpage = site.url[:-1] + catpage

            # Extract category name (text content of link)
            name = utils.safe_get_text(cat_link)

            # Skip empty names
            if not name or len(name) < 2:
                continue

            # Clean up the name
            name = name.strip()

            entries.append((name, catpage, "", name.lower()))

        except Exception as e:
            utils.kodilog("Motherless: Error parsing category: " + str(e))
            continue

    # Sort alphabetically
    entries.sort(key=lambda item: item[3])

    for display_name, catpage, img, _ in entries:
        site.add_dir(display_name, catpage, "List", "", "")

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    src = _extract_best_source(html)
    if src:
        # Use the page URL as referer for CDN checks
        vp.play_from_direct_link("{0}|Referer={1}".format(src, url))
    else:
        vp.play_from_link_to_resolve(url)


def _extract_best_source(html):
    # Motherless pages embed a file URL in JS variables or <source> tags
    candidates = []
    for src in re.findall(
        r"(?:file\"?:\\s*|source src=)[\"\\\']([^\"\\\']+)", html, re.IGNORECASE
    ):
        if any(ext in src for ext in (".mp4", ".m3u8")):
            candidates.append(src.replace("\\/", "/"))

    if not candidates:
        for src in re.findall(
            r'https?://[^"\\\']+\.(?:mp4|m3u8)[^"\\\']*', html, re.IGNORECASE
        ):
            candidates.append(src.replace("\\/", "/"))

    if not candidates:
        return ""

    def score(url):
        match = re.search(r"(\\d{3,4})p", url)
        return int(match.group(1)) if match else 0

    best = sorted(candidates, key=score, reverse=True)[0]
    if best.startswith("//"):
        best = "https:" + best
    return best
