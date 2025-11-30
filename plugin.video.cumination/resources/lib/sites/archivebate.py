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

import json
import re
from html import unescape
from uuid import uuid4

from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    'archivebate',
    '[COLOR hotpink]ArchiveBate[/COLOR]',
    'https://archivebate.com/',
    'archivebate.png',
    'archivebate'
)

LIVEWIRE_BASE = urllib_parse.urljoin(site.url, 'livewire/message/')
SEARCH_API = urllib_parse.urljoin(site.url, 'api/v1/search')
POSTS_API = urllib_parse.urljoin(site.url, 'wp-json/wp/v2/posts')
CATEGORIES_API = urllib_parse.urljoin(site.url, 'wp-json/wp/v2/categories')
POSTS_PER_PAGE = 30

LIVEWIRE_HEADERS = {
    'Content-Type': 'application/json',
    'X-Livewire': 'true',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}

SEARCH_HEADERS = {
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json, text/javascript, */*; q=0.01'
}


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url, 'Search', site.img_search)
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url, 'Categories', site.img_cat)
    ListVideos(site.url)


@site.register()
def ListVideos(url=None):
    """List videos using Livewire component."""
    page_url = url or site.url

    try:
        # Get Livewire snapshot from the page
        snapshot = _get_livewire_snapshot(page_url)
        if not snapshot:
            utils.kodilog('ArchiveBate: Failed to get Livewire snapshot from {0}'.format(page_url))
            utils.notify('Unable to load page data')
            utils.eod()
            return

        # Call Livewire to get video HTML
        html = _call_livewire(snapshot)
        if not html:
            utils.kodilog('ArchiveBate: Livewire API returned no HTML')
            utils.notify('Unable to load videos - try again later')
            utils.eod()
            return

        # Parse the video items
        soup = utils.parse_html(html)
        items = _parse_video_items(soup)

        if not items:
            utils.kodilog('ArchiveBate: No videos parsed from HTML')
            utils.notify('No videos found')
            utils.eod()
            return

        utils.kodilog('ArchiveBate: Found {0} videos'.format(len(items)))

        for item in items:
            site.add_download_link(
                item['title'],
                item['url'],
                'Playvid',
                item['thumb'],
                item['description'],
                duration=item.get('duration', '')
            )

        # Check for next page
        next_url = _find_next_page(soup, page_url)
        if next_url:
            page_num = _extract_page_number(next_url)
            label = '[COLOR hotpink]Next Page ({})[/COLOR]'.format(page_num)
            site.add_dir(label, next_url, 'ListVideos', site.img_next)

    except Exception as e:
        utils.kodilog('ArchiveBate: Unexpected error in ListVideos: {0}'.format(str(e)))
        utils.notify('Error loading videos')

    utils.eod()


@site.register()
def Search(url=None, keyword=None):
    """Search for videos."""
    if not keyword:
        site.search_dir(url or site.url, 'Search')
        return

    # Build search URL
    search_url = '{0}?query={1}'.format(site.url, urllib_parse.quote_plus(keyword))
    ListVideos(search_url)


@site.register()
def Categories(url=None):
    """List platform categories from homepage."""
    page_url = url or site.url
    html = utils.getHtml(page_url, site.url)
    if not html:
        utils.notify('Unable to load categories')
        utils.eod()
        return

    soup = utils.parse_html(html)

    # Find platform/category links (hashtags)
    category_links = soup.select('a[href*="/platform/"]')

    if not category_links:
        utils.notify('No categories found')
        utils.eod()
        return

    seen = set()
    for link in category_links:
        cat_url = _absolute_url(utils.safe_get_attr(link, 'href'))
        cat_name = utils.safe_get_text(link).strip()

        if cat_url and cat_url not in seen:
            seen.add(cat_url)
            # Clean up hashtag formatting
            display_name = cat_name.replace('#', '').title()
            site.add_dir('[COLOR hotpink]{0}[/COLOR]'.format(display_name), cat_url, 'ListVideos', site.img_cat)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.play_from_site_link(url, site.url)


def _get_nested(data, path, default=''):
    node = data
    for key in path:
        if not isinstance(node, dict):
            return default
        node = node.get(key, default)
    return node or default


def _select_thumb(post):
    thumb = post.get('jetpack_featured_media_url') or ''
    if thumb:
        return thumb

    embedded = post.get('_embedded') or {}
    media = embedded.get('wp:featuredmedia') or []
    if media:
        thumb = _get_nested(media[0], ['media_details', 'sizes', 'medium_large', 'source_url'])
        if not thumb:
            thumb = media[0].get('source_url', '')
    if thumb:
        return thumb

    better = post.get('better_featured_image') or {}
    thumb = better.get('source_url', '')
    return thumb


def _get_duration(post):
    acf = post.get('acf') or {}
    duration = acf.get('duration')
    if duration:
        return duration
    content = utils.cleantext(_get_nested(post, ['content', 'rendered']))
    match = re.search(r'(\d{1,2}:\d{2})', content)
    return match.group(1) if match else ''


def _get_livewire_snapshot(page_url):
    html = utils._getHtml(page_url, site.url)  # pylint: disable=protected-access
    if not html:
        return None

    soup = utils.parse_html(html)
    section = soup.find('section', attrs={'wire:init': True, 'wire:initial-data': True})
    if not section:
        return None

    try:
        initial = json.loads(unescape(section.get('wire:initial-data', '{}')))
    except ValueError:
        return None

    fingerprint = initial.get('fingerprint') or {}
    server_memo = initial.get('serverMemo') or {}
    component = fingerprint.get('name')
    csrf_tag = soup.find('meta', attrs={'name': 'csrf-token'})
    csrf_token = csrf_tag.get('content') if csrf_tag else ''
    method = section.get('wire:init') or 'loadVideos'

    if not component or not csrf_token:
        return None

    return {
        'page_url': page_url,
        'component': component,
        'fingerprint': fingerprint,
        'serverMemo': server_memo,
        'method': method,
        'csrf': csrf_token
    }


def _call_livewire(snapshot):
    post_url = urllib_parse.urljoin(LIVEWIRE_BASE, snapshot['component'])
    payload = {
        'fingerprint': snapshot['fingerprint'],
        'serverMemo': snapshot['serverMemo'],
        'updates': [{
            'type': 'callMethod',
            'payload': {
                'id': uuid4().hex[:10],
                'method': snapshot['method'],
                'params': []
            }
        }]
    }

    headers = LIVEWIRE_HEADERS.copy()
    headers['X-CSRF-TOKEN'] = snapshot['csrf']
    headers['Referer'] = snapshot['page_url']

    try:
        response = utils.postHtml(
            post_url,
            headers=headers,
            json_data=payload
        )
    except Exception as e:
        utils.kodilog('ArchiveBate: Livewire API error: {0}'.format(str(e)))
        return None

    if not response:
        utils.kodilog('ArchiveBate: empty Livewire response')
        return None

    try:
        data = json.loads(response)
    except ValueError as e:
        utils.kodilog('ArchiveBate: JSON parse error: {0}'.format(str(e)))
        return None

    effects = data.get('effects') or {}
    html_content = effects.get('html', '')

    if not html_content:
        utils.kodilog('ArchiveBate: no HTML in Livewire response')

    return html_content


def _parse_video_items(soup):
    items = []
    for section in soup.select('section.video_item'):
        link_tag = section.find('a', href=True)
        if not link_tag:
            continue
        url = _absolute_url(link_tag['href'])
        video_tag = section.find('video')
        thumb = video_tag.get('poster') if video_tag else ''
        if not thumb:
            img = section.find('img')
            thumb = img['src'] if img and img.has_attr('src') else ''
        thumb = _absolute_url(thumb)
        duration = utils.cleantext(utils.safe_get_text(section.find('div', class_='duration')))
        info_block = section.find('div', class_='info')
        creator = utils.safe_get_text(info_block.find('a')) if info_block else ''
        meta = utils.safe_get_text(info_block.find('p')) if info_block else ''
        title = creator or 'Video'
        if meta:
            title = '{0} - {1}'.format(title, meta)
        description = meta or ''
        items.append({
            'title': title,
            'url': url,
            'thumb': thumb or site.image,
            'description': description,
            'duration': duration
        })
    return items


def _find_next_page(soup, current_url):
    link = soup.select_one('a.page-link[rel="next"]')
    if not link:
        candidates = soup.select('a.page-link')
        for candidate in candidates:
            label = candidate.get('aria-label', '') or candidate.get_text(strip=True)
            if label and 'next' in label.lower():
                link = candidate
                break
    if link and link.get('href'):
        return urllib_parse.urljoin(current_url, link['href'])
    return None


def _extract_page_number(url):
    parsed = urllib_parse.urlparse(url)
    params = dict(urllib_parse.parse_qsl(parsed.query, keep_blank_values=True))
    try:
        return int(params.get('page', '2'))
    except (TypeError, ValueError):
        return 2


def _search_creators(keyword, page):
    params = {
        'query': keyword,
        'page': page
    }
    query = urllib_parse.urlencode(params)
    url = '{0}?{1}'.format(SEARCH_API, query)
    headers = SEARCH_HEADERS.copy()
    response = utils._getHtml(url, site.url, headers=headers)  # pylint: disable=protected-access
    if not response:
        return {}
    try:
        return json.loads(response)
    except ValueError:
        utils.kodilog('ArchiveBate: failed to parse search JSON')
        return {}


def _absolute_url(value, base=None):
    if not value:
        return ''
    value = value.strip()
    if value.startswith('//'):
        return 'https:' + value
    if value.startswith('http'):
        return value
    return urllib_parse.urljoin(base or site.url, value)
