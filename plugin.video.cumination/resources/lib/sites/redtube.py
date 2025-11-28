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
    listhtml = utils.getHtml(url, site.url, cookiehdr)

    if not listhtml or 'Error Page Not Found' in listhtml:
        utils.eod()
        return

    # Parse HTML with BeautifulSoup
    soup = utils.parse_html(listhtml)

    # Extract video items - RedTube uses class="videoblock_list" or "thumbnail-card"
    video_items = soup.select('.videoblock_list, li.thumbnail-card')

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

    # RedTube categories are in list items with links
    categories = soup.select('.category_wrapper a, .category-item a, a[href*="/category/"]')

    entries = []
    for category in categories:
        try:
            catpage = utils.safe_get_attr(category, 'href')
            if not catpage or '/category/' not in catpage:
                continue

            if catpage.startswith('/'):
                catpage = site.url[:-1] + catpage

            # Extract category name
            name = utils.safe_get_text(category)
            if not name:
                name = utils.safe_get_attr(category, 'title')
            if not name:
                name = utils.safe_get_attr(category, 'alt')

            if not name:
                continue

            # Extract thumbnail
            img_tag = category.select_one('img')
            img = utils.safe_get_attr(img_tag, 'data-src', ['src'])

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
    html = utils.getHtml(url, site.url, cookiehdr)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    src = _extract_best_source(html)
    if src:
        vp.play_from_direct_link(f"{src}|Referer={site.url}")
    else:
        vp.play_from_link_to_resolve(url)


def _extract_best_source(html):
    match = re.search(r'mediaDefinition\"?\\s*:\\s*(\\[.*?\\])', html, re.DOTALL)
    candidates = []
    if match:
        try:
            items = json.loads(match.group(1).replace('\\/', '/'))
            for item in items:
                url = item.get('videoUrl') or item.get('videoUrlMain')
                if not url:
                    continue
                quality = item.get('quality') or item.get('defaultQuality') or ''
                candidates.append((str(quality), url))
        except Exception:
            pass

    if not candidates:
        for src in re.findall(r'<source[^>]+src=[\"\\\']([^\"\\\']+)', html, re.IGNORECASE):
            if any(ext in src for ext in ('.mp4', '.m3u8')):
                candidates.append(('', src.replace('\\/', '/')))

    if not candidates:
        return ''

    def score(item):
        label = item[0]
        digits = ''.join(ch for ch in label if ch.isdigit())
        return int(digits) if digits else 0

    best = sorted(candidates, key=score, reverse=True)[0][1]
    if best.startswith('//'):
        best = 'https:' + best
    return best
