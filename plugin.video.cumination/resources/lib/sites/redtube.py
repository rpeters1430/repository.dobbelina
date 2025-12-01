'''
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
'''

import re
import json
from resources.lib import utils
from resources.lib.adultsite import AdultSite

try:
    from html import unescape as html_unescape
except ImportError:
    # Python 2 compatibility
    from six.moves import html_parser
    html_unescape = html_parser.HTMLParser().unescape

site = AdultSite('redtube', '[COLOR hotpink]RedTube[/COLOR]', 'https://www.redtube.com/', 'redtube.png', 'redtube')
cookiehdr = {'Cookie': 'age_verified=1'}


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + '?search=', 'Search', site.img_search)
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'categories', 'Categories', site.img_cat)
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    utils.kodilog("RedTube List: Fetching URL: {}".format(url))
    listhtml = utils.getHtml(url, site.url, cookiehdr)

    if not listhtml:
        utils.kodilog("RedTube List: No HTML received")
        utils.eod()
        return

    if 'Error Page Not Found' in listhtml:
        utils.kodilog("RedTube List: Page not found error in HTML")
        utils.eod()
        return

    utils.kodilog("RedTube List: Received {} bytes of HTML".format(len(listhtml)))

    # Parse HTML with BeautifulSoup
    soup = utils.parse_html(listhtml)

    # Extract video items - RedTube uses class="videoblock_list" or "thumbnail-card"
    video_items = soup.select('.videoblock_list, li.thumbnail-card')
    utils.kodilog("RedTube List: Found {} video items".format(len(video_items)))

    for item in video_items:
        try:
            # Get the link element
            link = item.select_one('a.video_link, a.video-title-text')
            if not link:
                continue

            # Extract video URL
            video_url = utils.safe_get_attr(link, 'href')
            if not video_url:
                continue

            # Make absolute URL if needed
            if video_url.startswith('/'):
                video_url = site.url[:-1] + video_url

            # Extract title from the title link
            title_link = item.select_one('.video-title-text')
            title = utils.safe_get_text(title_link) if title_link else ''
            if not title:
                # Fallback to image alt attribute
                img_tag = item.select_one('img')
                title = utils.safe_get_attr(img_tag, 'alt') if img_tag else 'Video'

            # Extract thumbnail image
            img_tag = item.select_one('img')
            img = utils.safe_get_attr(img_tag, 'data-src', ['data-srcset', 'src'])
            # If we get srcset, extract first URL
            if img and ' ' in img:
                img = img.split()[0]

            # Extract duration
            duration_tag = item.select_one('.duration span, .video-properties')
            duration = utils.safe_get_text(duration_tag)

            # Add video to list
            site.add_download_link(title, video_url, 'Playvid', img, '', duration=duration)

        except Exception as e:
            # Log error but continue processing other videos
            utils.kodilog("RedTube: Error parsing video item: " + str(e))
            continue

    # Extract pagination (Next Page link)
    # RedTube uses id="wp_navNext" or ".w_pagination_next.active a"
    next_page = soup.select_one('#wp_navNext, .w_pagination_next.active a')
    if next_page:
        next_url = utils.safe_get_attr(next_page, 'href')
        if next_url and next_url != 'javascript:void(0)':
            # Extract page number for display
            page_match = re.search(r'page=(\d+)', next_url)
            page_num = page_match.group(1) if page_match else ''

            # Build next page URL
            if next_url.startswith('/'):
                next_url = site.url[:-1] + next_url

            site.add_dir('Next Page ({})'.format(page_num), next_url, 'List', site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        from six.moves import urllib_parse
        title = urllib_parse.quote_plus(keyword)
        searchUrl = searchUrl + title
        List(searchUrl)


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url, cookiehdr)

    if not cathtml:
        utils.eod()
        return

    soup = utils.parse_html(cathtml)

    # RedTube categories are in .tm_cat_wrapper elements
    category_wrappers = soup.select('.tm_cat_wrapper')

    entries = []
    for wrapper in category_wrappers:
        try:
            # Get the category link (first <a> tag)
            link = wrapper.select_one('a[href*="/redtube/"]')
            if not link:
                continue

            catpage = utils.safe_get_attr(link, 'href')
            if not catpage or '/redtube/' not in catpage:
                continue

            # Make absolute URL if needed
            if catpage.startswith('/'):
                catpage = site.url[:-1] + catpage

            # Extract category name from <strong> tag
            strong_tag = wrapper.select_one('strong')
            name = utils.safe_get_text(strong_tag) if strong_tag else ''

            # Fallback to link text or title
            if not name:
                name = utils.safe_get_text(link)
            if not name:
                name = utils.safe_get_attr(link, 'title')

            if not name:
                continue

            # Extract thumbnail image
            img_tag = wrapper.select_one('img')
            img = utils.safe_get_attr(img_tag, 'src', ['data-src'])

            entries.append((name, catpage, img, name.lower()))

        except Exception as e:
            utils.kodilog("RedTube: Error parsing category: " + str(e))
            continue

    # Sort alphabetically
    entries.sort(key=lambda item: item[3])

    for display_name, catpage, img, _ in entries:
        site.add_dir(display_name, catpage, 'List', img, '')

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    utils.kodilog("RedTube Playvid: Fetching URL: {}".format(url))
    html = utils.getHtml(url, site.url, cookiehdr)

    if not html:
        utils.kodilog("RedTube Playvid: No HTML received")
        utils.notify('Error', 'Could not load page')
        return

    utils.kodilog("RedTube Playvid: Received {} bytes of HTML".format(len(html)))

    # Use the enhanced extraction function that handles API-based URLs
    video_url = _extract_best_source(html)

    if not video_url:
        utils.notify('Error', 'No video found')
        return

    utils.kodilog("RedTube: Playing URL: " + video_url[:150])
    vp.play_from_direct_link("{0}|Referer={1}".format(video_url, url))


def _extract_best_source(html):
    # First, try to get video URLs from the new API endpoint format
    candidates = []

    # Look for mediaDefinition/mediaDefinitions with API endpoints (both singular and plural)
    # Matches: "mediaDefinition": or "mediaDefinitions": in JSON
    # The ?: makes it non-capturing, and we look for the key followed by the array value
    match = re.search(r'mediaDefinitions?"\s*:\s*(\[.*?\])', html, re.DOTALL)
    utils.kodilog("RedTube: Regex match result: {}".format("FOUND" if match else "NOT FOUND"))

    # Debug: Check if mediaDefinitions is even in the HTML
    if not match and 'mediaDefinitions' in html:
        idx = html.find('mediaDefinitions')
        utils.kodilog("RedTube: mediaDefinitions found in HTML but regex didn't match")
        utils.kodilog("RedTube: Context: {}".format(html[max(0, idx-100):idx+200]))
    elif not match:
        utils.kodilog("RedTube: mediaDefinitions NOT in HTML - checking for clues")
        if '<title>' in html[:500]:
            title_match = re.search(r'<title>(.*?)</title>', html[:1000], re.IGNORECASE)
            if title_match:
                utils.kodilog("RedTube: Page title: {}".format(title_match.group(1)[:100]))

    if match:
        utils.kodilog("RedTube: Captured JSON: {}".format(match.group(1)[:200]))
        try:
            items = json.loads(match.group(1).replace('\\/', '/'))
            utils.kodilog("RedTube: Parsed {} items from mediaDefinitions".format(len(items)))
            for item in items:
                url = item.get('videoUrl') or item.get('videoUrlMain')
                if not url:
                    continue

                # Check if this is an API endpoint URL
                if url.startswith('/media/'):
                    # Make absolute URL
                    api_url = site.url.rstrip('/') + url
                    utils.kodilog("RedTube: Fetching qualities from API: " + api_url)

                    # Fetch video qualities from API
                    try:
                        api_response = utils.getHtml(api_url, site.url, cookiehdr)
                        if api_response:
                            api_data = json.loads(api_response)
                            # Process each quality option
                            for quality_item in api_data:
                                video_url = quality_item.get('videoUrl', '')
                                quality = quality_item.get('quality', '')
                                if video_url and quality:
                                    video_url = html_unescape(video_url)
                                    candidates.append((str(quality), video_url))
                                    utils.kodilog("RedTube: Found {}p: {}".format(quality, video_url[:100]))
                    except Exception as e:
                        utils.kodilog("RedTube: API error: " + str(e))
                else:
                    # Direct URL in old format
                    url = html_unescape(url)
                    quality = item.get('quality') or item.get('defaultQuality') or ''
                    candidates.append((str(quality), url))
        except Exception as e:
            utils.kodilog("RedTube: mediaDefinition parse error: " + str(e))

    if not candidates:
        # Fallback: look for quality/url pairs used by Aylo inline JSON
        for quality, src in re.findall(r'"(?:quality|label)"\s*:\s*"?(\d{3,4})p?"?.*?"(?:videoUrl|src|url)"\s*:\s*"([^"]+)', html, re.IGNORECASE | re.DOTALL):
            # Decode HTML entities
            src = html_unescape(src.replace('\\/', '/'))
            candidates.append((quality, src))

    if not candidates:
        for src in re.findall(r'<source[^>]+src=[\"\\\']([^\"\\\']+)', html, re.IGNORECASE):
            if any(ext in src for ext in ('.mp4', '.m3u8')):
                src = html_unescape(src.replace('\\/', '/'))
                # Skip preview/feedback videos (360P with _fb suffix)
                if '_fb.mp4' not in src:
                    candidates.append(('', src))
        for src in re.findall(r'https?://[^"\\\']+\.(?:mp4|m3u8)[^"\\\']*', html, re.IGNORECASE):
            src = html_unescape(src.replace('\\/', '/'))
            # Skip preview/feedback videos (360P with _fb suffix)
            if '_fb.mp4' not in src:
                candidates.append(('', src))

    if not candidates:
        utils.kodilog("RedTube: No video sources found")
        return ''

    def score(item):
        label = item[0]
        digits = ''.join(ch for ch in label if ch.isdigit())
        return int(digits) if digits else 0

    # Sort by quality (highest first)
    sorted_candidates = sorted(candidates, key=score, reverse=True)
    best = sorted_candidates[0][1]

    utils.kodilog("RedTube: Selected best quality: {}p - {}".format(
        sorted_candidates[0][0], best[:100]
    ))

    if best.startswith('//'):
        best = 'https:' + best
    return best
