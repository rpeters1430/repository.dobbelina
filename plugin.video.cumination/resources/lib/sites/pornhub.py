"""
Cumination
Copyright (C) 2015 Whitecream
Copyright (C) 2015 anton40
Copyright (C) 2015 Team Cumination

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
import six
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "pornhub",
    "[COLOR hotpink]PornHub[/COLOR]",
    "https://www.pornhub.com/",
    "pornhub.png",
    "pornhub",
    category="Video Tubes",
)
cookiehdr = {"Cookie": "accessAgeDisclaimerPH=1; accessAgeDisclaimerUK=1"}


def _is_text(value):
    return isinstance(value, six.string_types)


def _log_non_text_response(context, value):
    utils.kodilog(
        "pornhub: Expected HTML string while {}, got {}".format(
            context, type(value).__name__
        )
    )


def _decode_js_string_literal(raw_value):
    raw_value = raw_value.lstrip()
    if not raw_value or raw_value[0] not in ("'", '"'):
        return None

    quote = raw_value[0]
    decoded = []
    index = 1
    length = len(raw_value)
    while index < length:
        char = raw_value[index]
        if char == quote:
            return "".join(decoded)
        if char != "\\":
            decoded.append(char)
            index += 1
            continue

        index += 1
        if index >= length:
            return None
        escaped = raw_value[index]
        escapes = {
            "\\": "\\",
            "/": "/",
            '"': '"',
            "'": "'",
            "b": "\b",
            "f": "\f",
            "n": "\n",
            "r": "\r",
            "t": "\t",
        }
        if escaped == "u" and index + 4 < length:
            hex_value = raw_value[index + 1:index + 5]
            try:
                decoded.append(six.unichr(int(hex_value, 16)))
                index += 5
                continue
            except ValueError:
                return None
        decoded.append(escapes.get(escaped, escaped))
        index += 1
    return None


def _extract_json_assignment(html, name_pattern):
    if not _is_text(html):
        return None
    match = re.search(
        r"{0}\s*=\s*".format(name_pattern),
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return None
    decoder = json.JSONDecoder()
    raw_value = html[match.end():].lstrip()
    if raw_value.startswith("JSON.parse"):
        parse_match = re.match(r"JSON\.parse\(\s*", raw_value, re.IGNORECASE)
        if parse_match:
            try:
                parsed_string = _decode_js_string_literal(raw_value[parse_match.end():])
                if parsed_string is None:
                    return None
                return json.loads(parsed_string)
            except (TypeError, ValueError):
                return None
    try:
        value, _ = decoder.raw_decode(raw_value)
        return value
    except ValueError:
        return None


def _extract_json_value_after(html, pattern):
    if not _is_text(html):
        return None
    decoder = json.JSONDecoder()
    match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    try:
        value, _ = decoder.raw_decode(html[match.end():].lstrip())
        return value
    except ValueError:
        return None


def _source_quality_value(source):
    label = str(source[0] or "")
    if "4k" in label.lower() or "uhd" in label.lower():
        return 2160
    digits = "".join(ch for ch in label if ch.isdigit())
    return int(digits) if digits else 0


def _extract_media_sources(html):
    if not _is_text(html):
        _log_non_text_response("resolving video", html)
        return []

    sources = []

    quality_items = _extract_json_assignment(html, r"(?:var\s+)?qualityItems_\d+")
    if isinstance(quality_items, list):
        sources.extend(
            (src.get("text"), src.get("url"))
            for src in quality_items
            if isinstance(src, dict) and src.get("url")
        )

    flashvars = _extract_json_assignment(html, r"flashvars_\d+")
    if isinstance(flashvars, dict):
        for src in flashvars.get("mediaDefinitions", []):
            if not isinstance(src, dict):
                continue
            quality = src.get("quality")
            video_url = src.get("videoUrl")
            if isinstance(quality, list) or not video_url:
                continue
            sources.append((quality, video_url))

    media_definitions = _extract_json_value_after(
        html,
        r'["\']mediaDefinitions["\']\s*:\s*',
    )
    if isinstance(media_definitions, list):
        for src in media_definitions:
            if not isinstance(src, dict):
                continue
            quality = src.get("quality") or src.get("defaultQuality") or src.get("format")
            video_url = src.get("videoUrl") or src.get("url")
            if isinstance(quality, list) or not video_url:
                continue
            sources.append((quality, video_url))

    cleaned = []
    seen_urls = set()
    for quality, video_url in sources:
        if video_url in seen_urls:
            continue
        seen_urls.add(video_url)
        cleaned.append((quality, video_url))
    return cleaned


def _select_media_source(sources):
    if not sources:
        return ""
    return sorted(sources, key=_source_quality_value)[-1][1]


def _fallback_title_from_url(video_url):
    match = re.search(r"[?&]viewkey=([a-zA-Z0-9]+)", video_url or "")
    if match:
        return "PornHub Video {}".format(match.group(1))
    return "PornHub Video"


def _headers_suffix(video_page_url):
    cookie_str = cookiehdr["Cookie"]
    try:
        cookies = []
        for cookie in utils.cj:
            if cookie.domain and ("pornhub.com" in cookie.domain or "phncdn.com" in cookie.domain):
                cookies.append("{}={}".format(cookie.name, cookie.value))
        if cookies:
            cookie_str = "; ".join(cookies)
    except Exception:
        pass

    headers = {
        "User-Agent": utils.USER_AGENT,
        "Referer": site.url,
        "Cookie": cookie_str,
        "Origin": site.url.rstrip("/"),
    }
    return "|" + urllib_parse.urlencode(headers)


def add_img_headers(img_url):
    if not img_url:
        return img_url
    if "|" in img_url:
        return img_url
    if img_url.startswith("//"):
        img_url = "https:" + img_url
    if not img_url.startswith("http"):
        return img_url
    if any(domain in img_url for domain in ("phncdn.com", "ttcache.com")):
        return "{}|Referer={}&User-Agent={}".format(
            img_url, site.url, utils.USER_AGENT
        )
    return img_url


def _resolve_video_url(url):
    html = utils._getHtml(url, site.url, cookiehdr)
    video_url = _select_media_source(_extract_media_sources(html))
    if video_url:
        return video_url + _headers_suffix(url)
    return ""


def _is_media_preview_url(value):
    if not value:
        return False
    clean_value = value.split("?", 1)[0].lower()
    return clean_value.endswith(".mp4") or clean_value.endswith(".webm")


def _thumb_from_data_path(img_tag, fallback_url=""):
    path = utils.safe_get_attr(img_tag, "data-path")
    if not path:
        return ""
    path = path.replace("{index}", "1")
    if path.startswith("//"):
        return "https:" + path
    if path.startswith("http"):
        return path

    fallback_match = re.match(r"(https?://[^/]+)", fallback_url or "")
    host = fallback_match.group(1) if fallback_match else "https://pix-fl.phncdn.com"
    return host + path


def _extract_thumbnail(item, link):
    img_tag = item.select_one("img")
    attr_names = [
        "data-mediumthumb",
        "data-thumb-url",
        "data-thumb_url",
        "data-image",
        "data-src",
        "data-lazy-src",
        "data-img",
        "data-poster",
        "poster",
        "src",
    ]
    # Check BeautifulSoup sources first
    for source in (img_tag, item, link):
        if not source:
            continue
        for attr in attr_names:
            img = utils.safe_get_attr(source, attr)
            if img and not _is_media_preview_url(img) and "phncdn.com" in img:
                return add_img_headers(img)

    # Fallback: Regex extraction from item HTML to handle poisoned tags (rogue '>')
    # PornHub sometimes injects a '>' in the middle of img attributes to break parsers.
    item_html = str(item)
    for attr in attr_names:
        match = re.search(r'%s=["\']\s*([^"\']+)["\']' % attr, item_html)
        if match:
            img = match.group(1)
            if img and not _is_media_preview_url(img) and "phncdn.com" in img:
                return add_img_headers(img)

    fallback = utils.safe_get_attr(img_tag, "data-image", ["src"]) if img_tag else ""
    img = _thumb_from_data_path(img_tag, fallback) if img_tag else ""
    if img and not _is_media_preview_url(img):
        return add_img_headers(img)
    return ""


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        site.url + "video/search?search=",
        "Search",
        site.img_search,
    )
    categories_url = site.url.rstrip("/") + "/categories"
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]", categories_url, "Categories", site.img_cat
    )
    List(site.url + "video?o=cm")
    utils.eod()


@site.register()
def List(url):
    url = update_url(url)

    def collect_video_items(scope_obj):
        selectors = (
            "li.pcVideoListItem, div.pcVideoListItem, li.js-pop.videoBox, div.js-pop.videoBox"
        )
        nodes = list(scope_obj.select(selectors))
        filtered = []
        for node in nodes:
            # Check if we already found this node's parent (to avoid nesting duplicates)
            if any(p in nodes for p in node.parents):
                continue
            link = node.select_one('a[href*="/view_video.php?viewkey="]')
            if link:
                filtered.append(node)
        if filtered:
            return filtered

        # Fallback: locate anchors directly when container classes change.
        anchors = scope_obj.select('a[href*="/view_video.php?viewkey="]')
        wrapped = []
        seen_parents = set()
        for anchor in anchors:
            parent = anchor.find_parent(["li", "div", "article"])
            item = parent if parent is not None else anchor
            item_id = id(item)
            if item_id not in seen_parents:
                wrapped.append(item)
                seen_parents.add(item_id)
        return wrapped

    def dedupe_video_items(items):
        deduped = []
        seen_keys = set()
        for item in items:
            link = item.select_one('a[href*="/view_video.php?viewkey="]')
            # Fix for when item itself is the link
            if not link and item.name == 'a' and '/view_video.php?viewkey=' in item.get('href', ''):
                link = item

            href = utils.safe_get_attr(link, "href") if link else ""
            if not href:
                continue

            # Extract viewkey for robust deduplication
            key_match = re.search(r"viewkey=([a-zA-Z0-9]+)", href)
            key = key_match.group(1) if key_match else href

            if key in seen_keys:
                continue
            seen_keys.add(key)
            deduped.append(item)
        return deduped

    def collect_search_video_items(soup_obj):
        # Only use broad containers as search scopes to avoid redundancy.
        search_scopes = soup_obj.select(
            "#searchPageVideoList, #videoSearchResult, #videoSearchWrapper, "
            ".search-video-thumbs, ul.videos, div.videos"
        )
        scoped_items = []
        for scope in search_scopes:
            # Check if this scope is already inside another scope to avoid duplication
            if any(p in search_scopes for p in scope.parents):
                continue
            scoped_items.extend(collect_video_items(scope))

        if scoped_items:
            return dedupe_video_items(scoped_items)
        return dedupe_video_items(collect_video_items(soup_obj))

    cm_production = utils.addon_sys + "?mode=" + str("pornhub.ContextProduction")
    cm_min_length = utils.addon_sys + "?mode=" + str("pornhub.ContextMinLength")
    cm_max_length = utils.addon_sys + "?mode=" + str("pornhub.ContextMaxLength")
    cm_quality = utils.addon_sys + "?mode=" + str("pornhub.ContextQuality")
    cm_country = utils.addon_sys + "?mode=" + str("pornhub.ContextCountry")
    cm_sortby = utils.addon_sys + "?mode=" + str("pornhub.ContextSortby")
    cm_time = utils.addon_sys + "?mode=" + str("pornhub.ContextTime")
    cm_filter = [
        (
            "[COLOR violet]Production[/COLOR] [COLOR orange]{}[/COLOR]".format(
                get_setting("production")
            ),
            "RunPlugin(" + cm_production + ")",
        ),
        (
            "[COLOR violet]Min Length[/COLOR] [COLOR orange]{}[/COLOR]".format(
                get_setting("minlength")
            ),
            "RunPlugin(" + cm_min_length + ")",
        ),
        (
            "[COLOR violet]Max Length[/COLOR] [COLOR orange]{}[/COLOR]".format(
                get_setting("maxlength")
            ),
            "RunPlugin(" + cm_max_length + ")",
        ),
        (
            "[COLOR violet]Quality[/COLOR] [COLOR orange]{}[/COLOR]".format(
                get_setting("quality")
            ),
            "RunPlugin(" + cm_quality + ")",
        ),
        (
            "[COLOR violet]Country[/COLOR] [COLOR orange]{}[/COLOR]".format(
                get_setting("country")
            ),
            "RunPlugin(" + cm_country + ")",
        ),
        (
            "[COLOR violet]Sort By[/COLOR] [COLOR orange]{}[/COLOR]".format(
                get_setting("sortby")
            ),
            "RunPlugin(" + cm_sortby + ")",
        ),
        (
            "[COLOR violet]Time[/COLOR] [COLOR orange]{}[/COLOR]".format(
                get_setting("time")
            ),
            "RunPlugin(" + cm_time + ")",
        ),
    ]

    listhtml = utils.getHtml(url, site.url, cookiehdr)
    if not _is_text(listhtml):
        _log_non_text_response("loading listing", listhtml)
        listhtml = ""
    if not listhtml or "Error Page Not Found" in listhtml:
        site.add_dir(
            "No videos found. [COLOR hotpink]Clear all filters.[/COLOR]",
            "",
            "ResetFilters",
            Folder=False,
            contextm=cm_filter,
        )
        utils.eod()
        return

    # Parse HTML with BeautifulSoup
    soup = utils.parse_html(listhtml)

    # Extract page title (if present)
    title_tag = soup.select_one("h1.searchPageTitle, h1")
    if title_tag:
        title = utils.cleantext(utils.safe_get_text(title_tag))
        site.add_dir(
            "[COLOR orange]" + title + " [COLOR hotpink]*** Clear all filters.[/COLOR]",
            "",
            "ResetFilters",
            Folder=False,
            contextm=cm_filter,
        )

    # Extract video items
    # PornHub uses class="pcVideoListItem" for video cards
    if "search?" in url:
        video_items = collect_search_video_items(soup)
    else:
        video_items = dedupe_video_items(collect_video_items(soup))

    for item in video_items:
        try:
            # Get the link element
            link = item.select_one('a[href*="/view_video.php?viewkey="]')
            if not link:
                continue

            # Extract video URL and title
            video_url = utils.safe_get_attr(link, "href")
            if not video_url:
                continue

            # Make absolute URL if needed
            if video_url.startswith("/"):
                video_url = site.url[:-1] + video_url

            title = utils.safe_get_attr(link, "title")
            if not title:
                title_tag = item.select_one(".title")
                title = utils.safe_get_text(title_tag)
            if not title:
                img_tag = item.select_one("img")
                title = utils.safe_get_attr(img_tag, "alt")
            if not title:
                title = _fallback_title_from_url(video_url)

            img = _extract_thumbnail(item, link)

            # Extract duration
            duration_tag = item.select_one('.duration, [data-title="Video Duration"]')
            duration = utils.safe_get_text(duration_tag)

            # Skip very short videos (likely previews/ads)
            if duration:
                # Convert duration to seconds for comparison
                # Format is usually MM:SS or H:MM:SS
                parts = duration.split(':')
                try:
                    seconds = 0
                    if len(parts) == 1:
                        seconds = int(parts[0])
                    elif len(parts) == 2:
                        seconds = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 3:
                        seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                    
                    if seconds > 0 and seconds < 60:
                        utils.kodilog("pornhub: Skipping short video '{}' ({}s)".format(title, seconds))
                        continue
                except (ValueError, TypeError):
                    pass

            # Add video to list
            site.add_download_link(
                title,
                video_url,
                "Playvid",
                img,
                "",
                duration=duration,
                contextm=cm_filter,
            )

        except Exception as e:
            # Log error but continue processing other videos
            utils.kodilog("Error parsing video item: " + str(e))
            continue

    # Extract pagination (Next Page link)
    next_page = soup.select_one("li.page_next a, .page_next a")
    if next_page:
        next_url = utils.safe_get_attr(next_page, "href")
        if next_url:
            # Extract page number for display
            page_match = re.search(r"page=(\d+)", next_url)
            page_num = page_match.group(1) if page_match else ""

            # Extract "Showing X-Y of Z" text for display
            showing_text = soup.select_one(".showingCounter")
            showing_info = (
                " [COLOR hotpink]... " + utils.safe_get_text(showing_text) + "[/COLOR]"
                if showing_text
                else ""
            )

            # Build next page URL
            if next_url.startswith("/"):
                next_url = site.url[:-1] + next_url
            next_url = next_url.replace("&amp;", "&")

            site.add_dir(
                "Next Page ({}){}".format(page_num, showing_info),
                next_url,
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
        from six.moves import urllib_parse

        title = urllib_parse.quote_plus(keyword)
        searchUrl = searchUrl + title
        List(searchUrl)


@site.register()
def Categories(url):
    utils.kodilog("PornHub Categories URL: " + url)
    cathtml = utils.getHtml(url, site.url, cookiehdr)
    if not _is_text(cathtml):
        _log_non_text_response("loading categories", cathtml)
        utils.eod()
        return

    soup = utils.parse_html(cathtml)
    categories = soup.select('.category-wrapper, div[class*="category"]')

    entries = []
    for category in categories:
        try:
            link = category.select_one("a")
            if not link:
                continue
            catpage = utils.safe_get_attr(link, "href")
            if not catpage:
                continue
            if catpage.startswith("/"):
                catpage = site.url[:-1] + catpage
            name = utils.safe_get_attr(link, "alt")
            if not name:
                name = utils.safe_get_attr(link, "title")
            if not name:
                name_tag = category.select_one(".title, .categoryName")
                name = utils.safe_get_text(name_tag) if name_tag else "Category"
            img_tag = category.select_one("img")
            img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-lazy-src"])
            img = add_img_headers(img)
            
            count_tag = category.select_one("var, .videoCount")
            video_count = utils.safe_get_text(count_tag)
            if video_count:
                display_name = name + " [COLOR orange]({} videos)[/COLOR]".format(
                    video_count
                )
            else:
                display_name = name
            entries.append((display_name, catpage, img, name.lower()))
        except Exception as e:
            utils.kodilog("Error parsing category: " + str(e))
            continue

    entries.sort(key=lambda item: item[3])
    for display_name, catpage, img, _ in entries:
        site.add_dir(display_name, catpage, "List", img, "")

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    direct_url = _resolve_video_url(url)
    if direct_url:
        if ".m3u8" in direct_url:
            vp.IA_check = "IA"
        vp.play_from_direct_link(direct_url)
        return
    vp.play_from_link_to_resolve(url)


def get_setting(x):
    dict = {
        "production": "All",
        "minlength": "0",
        "maxlength": "40+ Min",
        "quality": "All",
        "country": "World",
        "sortby": "Newest",
        "time": "All Time",
    }
    if x in dict:
        ret = (
            utils.addon.getSetting("pornhub" + x)
            if utils.addon.getSetting("pornhub" + x)
            else dict[x]
        )
    else:
        ret = ""
    return ret


@site.register()
def ContextProduction():
    filters = {"All": 1, "Professional": 2, "Homemade": 3}
    cat = utils.selector(
        "Select production", filters.keys(), sort_by=lambda x: filters[x]
    )
    if cat:
        utils.addon.setSetting("pornhubproduction", cat)
        utils.refresh()


@site.register()
def ContextMinLength():
    filters = {"0": 1, "10 min": 2, "20 min": 3, "30 min": 4}
    cat = utils.selector(
        "Select Min Legth", filters.keys(), sort_by=lambda x: filters[x]
    )
    if cat:
        utils.addon.setSetting("pornhubminlength", cat)
        utils.refresh()


@site.register()
def ContextMaxLength():
    filters = {"10 Min": 1, "20 Min": 2, "30 Min": 3, "40+ Min": 4}
    cat = utils.selector(
        "Select Max Legth", filters.keys(), sort_by=lambda x: filters[x]
    )
    if cat:
        utils.addon.setSetting("pornhubmaxlength", cat)
        utils.refresh()


@site.register()
def ContextQuality():
    filters = {"All": 1, "HD": 2}
    cat = utils.selector("Select Quality", filters.keys(), sort_by=lambda x: filters[x])
    if cat:
        utils.addon.setSetting("pornhubquality", cat)
        utils.refresh()


@site.register()
def ContextCountry():
    cc = {
        "World": "",
        "Argentina": "cc=ar",
        "Australia": "cc=au",
        "Austria": "cc=at",
        "Belgium": "cc=be",
        "Brazil": "cc=br",
        "Bulgaria": "cc=bg",
        "Canada": "cc=ca",
        "Chile": "cc=cl",
        "Croatia": "cc=hr",
        "Czech Republic": "cc=cz",
        "Denmark": "cc=dk",
        "Egypt": "cc=eg",
        "Finland": "cc=fi",
        "France": "cc=fr",
        "Germany": "cc=de",
        "Greece": "cc=gr",
        "Hungary": "cc=hu",
        "India": "cc=in",
        "Ireland": "cc=ie",
        "Israel": "cc=il",
        "Italy": "cc=it",
        "Japan": "cc=jp",
        "Mexico": "cc=mx",
        "Morocco": "cc=ma",
        "Netherlands": "cc=nl",
        "New Zealand": "cc=nz",
        "Norway": "cc=no",
        "Pakistan": "cc=pk",
        "Poland": "cc=pl",
        "Portugal": "cc=pt",
        "Romania": "cc=ro",
        "Russian Federation": "cc=ru",
        "Serbia": "cc=rs",
        "Slovakia": "cc=sk",
        "Korea => Republic of": "cc=kr",
        "Spain": "cc=es",
        "Sweden": "cc=se",
        "Switzerland": "cc=ch",
        "United Kingdom": "cc=gb",
        "Ukraine": "cc=ua",
        "United States": "cc=us",
    }
    cat = utils.selector("Select Country", cc.keys())
    if cat:
        utils.addon.setSetting("pornhubcountry", cat)
        utils.refresh()


@site.register()
def ContextSortby():
    filters = {
        "Newest": 1,
        "Hottest": 2,
        "Longest": 3,
        "Top Rated": 4,
        "Most Viewed": 5,
        "Featured Recently/Most Relevant": 6,
    }
    cat = utils.selector(
        "Select Sort Order", filters.keys(), sort_by=lambda x: filters[x]
    )
    if cat:
        utils.addon.setSetting("pornhubsortby", cat)
        utils.refresh()


@site.register()
def ContextTime():
    filters = {"All Time": 1, "Daily": 2, "Weekly": 3, "Monthly": 4, "Yearly": 5}
    cat = utils.selector("Select time", filters.keys(), sort_by=lambda x: filters[x])
    if cat:
        utils.addon.setSetting("pornhubtime", cat)
        utils.refresh()


def param(x):
    cc = {
        "World": "",
        "Argentina": "cc=ar",
        "Australia": "cc=au",
        "Austria": "cc=at",
        "Belgium": "cc=be",
        "Brazil": "cc=br",
        "Bulgaria": "cc=bg",
        "Canada": "cc=ca",
        "Chile": "cc=cl",
        "Croatia": "cc=hr",
        "Czech Republic": "cc=cz",
        "Denmark": "cc=dk",
        "Egypt": "cc=eg",
        "Finland": "cc=fi",
        "France": "cc=fr",
        "Germany": "cc=de",
        "Greece": "cc=gr",
        "Hungary": "cc=hu",
        "India": "cc=in",
        "Ireland": "cc=ie",
        "Israel": "cc=il",
        "Italy": "cc=it",
        "Japan": "cc=jp",
        "Mexico": "cc=mx",
        "Morocco": "cc=ma",
        "Netherlands": "cc=nl",
        "New Zealand": "cc=nz",
        "Norway": "cc=no",
        "Pakistan": "cc=pk",
        "Poland": "cc=pl",
        "Portugal": "cc=pt",
        "Romania": "cc=ro",
        "Russian Federation": "cc=ru",
        "Serbia": "cc=rs",
        "Slovakia": "cc=sk",
        "Korea => Republic of": "cc=kr",
        "Spain": "cc=es",
        "Sweden": "cc=se",
        "Switzerland": "cc=ch",
        "United Kingdom": "cc=gb",
        "Ukraine": "cc=ua",
        "United States": "cc=us",
    }
    dict = {
        "All": "",
        "Professional": "p=professional",
        "Homemade": "p=homemade",
        "0": "",
        "10 min": "min_duration=10",
        "20 min": "min_duration=20",
        "30 min": "min_duration=30",
        "10 Min": "max_duration=10",
        "20 Min": "max_duration=20",
        "30 Min": "max_duration=30",
        "40+ Min": "",
        "HD": "hd=1",
        "Newest": "o=cm",
        "Hottest": "o=ht",
        "Longest": "o=lg",
        "Top Rated": "o=tr",
        "Most Viewed": "o=mv",
        "Featured Recently/Most Relevant": "",
        "All Time": "t=a",
        "Daily": "t=t",
        "Weekly": "t=w",
        "Monthly": "",
        "Yearly": "t=y",
    }
    dict.update(cc)
    if x in dict:
        ret = dict[x]
    else:
        utils.kodilog("Key error: " + str(x))
        ret = ""
    return ret


def _query_value(query_pairs, name):
    for key, value in query_pairs:
        if key == name:
            return value
    return ""


def _param_pair(value):
    if not value:
        return None
    key, sep, param_value = value.partition("=")
    if not sep or not key:
        return None
    return key, param_value


def _remove_query_keys(query_pairs, keys):
    return [(key, value) for key, value in query_pairs if key not in keys]


def update_url(url):
    parts = urllib_parse.urlsplit(url)
    query_pairs = urllib_parse.parse_qsl(parts.query, keep_blank_values=True)

    if "/video/search" in parts.path:
        # Keep search queries simple and stable; aggressive filters often return empty results.
        search_value = _query_value(query_pairs, "search")
        page_value = _query_value(query_pairs, "page")
        clean_query = [("search", search_value)]
        if page_value:
            clean_query.append(("page", page_value))
        clean_query.append(("o", "mr"))
        return urllib_parse.urlunsplit(
            (
                parts.scheme or "https",
                parts.netloc or "www.pornhub.com",
                parts.path,
                urllib_parse.urlencode(clean_query),
                parts.fragment,
            )
        )

    filter_keys = {"p", "min_duration", "max_duration", "hd", "o", "t", "cc"}
    base_query = _remove_query_keys(query_pairs, filter_keys)
    new_query = list(base_query)

    for setting in (
        "production",
        "minlength",
        "maxlength",
        "quality",
        "country",
        "sortby",
        "time",
    ):
        pair = _param_pair(param(get_setting(setting)))
        if pair:
            new_query.append(pair)

    sort_order = _query_value(new_query, "o")
    if not sort_order or sort_order in ("lg", "cm", "mr"):
        new_query = _remove_query_keys(new_query, {"t", "cc"})
    elif sort_order == "tr":
        new_query = _remove_query_keys(new_query, {"cc"})
    elif sort_order == "ht":
        new_query = _remove_query_keys(new_query, {"t"})

    old_without_page = sorted(
        (key, value) for key, value in query_pairs if key != "page"
    )
    new_without_page = sorted(
        (key, value) for key, value in new_query if key != "page"
    )
    if new_without_page != old_without_page:
        new_query = _remove_query_keys(new_query, {"page"})

    return urllib_parse.urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urllib_parse.urlencode(new_query),
            parts.fragment,
        )
    )


@site.register()
def ResetFilters():
    dict = {
        "production": "All",
        "minlength": "0",
        "maxlength": "40+ Min",
        "quality": "All",
        "country": "World",
        "sortby": "Newest",
        "time": "All Time",
    }
    for x in dict:
        utils.addon.setSetting("pornhub" + x, dict[x])
    utils.refresh()
    return
