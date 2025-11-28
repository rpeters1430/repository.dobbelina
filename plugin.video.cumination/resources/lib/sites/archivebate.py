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
def Main(page_url=None):
    site.add_dir('[COLOR hotpink]Search Creators[/COLOR]', SEARCH_API, 'Search', site.img_search)
    ListVideos(page_url or POSTS_API, page=1)


@site.register()
def ListVideos(url=None, page=1):
    """List videos from the WordPress API (JSON)."""
    api_url = url or POSTS_API
    parsed = urllib_parse.urlparse(api_url)
    params = dict(urllib_parse.parse_qsl(parsed.query, keep_blank_values=True))
    params.setdefault('per_page', POSTS_PER_PAGE)
    try:
        params['page'] = int(page)
    except (TypeError, ValueError):
        params['page'] = 1

    api_url = parsed._replace(query=urllib_parse.urlencode(params)).geturl()
    response = utils.getHtml(api_url, site.url)
    if not response:
        utils.notify('Unable to load listing')
        utils.eod()
        return

    try:
        posts = json.loads(response)
    except ValueError:
        utils.notify('Invalid response')
        utils.eod()
        return

    if not posts:
        utils.notify('Nothing found')
        utils.eod()
        return

    for post in posts:
        title = utils.cleantext(_get_nested(post, ['title', 'rendered'])) or 'Video'
        link = post.get('link') or _absolute_url('', site.url)
        thumb = _select_thumb(post)
        excerpt = utils.cleantext(_get_nested(post, ['excerpt', 'rendered']))
        duration = _get_duration(post)

        site.add_download_link(
            title,
            link,
            'Playvid',
            thumb or site.image,
            excerpt,
            duration=duration
        )

    if len(posts) >= POSTS_PER_PAGE:
        next_page = params['page'] + 1
        params['page'] = next_page
        next_url = parsed._replace(query=urllib_parse.urlencode(params)).geturl()
        label = '[COLOR hotpink]Next Page ({})[/COLOR]'.format(next_page)
        site.add_dir(label, next_url, 'ListVideos', site.img_next)

    utils.eod()


@site.register()
def Search(url=None, keyword=None, page=1):
    """Build a search URL for posts and delegate to ListVideos."""
    if not keyword:
        site.search_dir(url or POSTS_API, 'Search')
        return

    base = url or POSTS_API
    parsed = urllib_parse.urlparse(base)
    params = dict(urllib_parse.parse_qsl(parsed.query, keep_blank_values=True))
    params['search'] = keyword
    params.setdefault('per_page', POSTS_PER_PAGE)
    params['page'] = int(page or 1)
    search_url = parsed._replace(query=urllib_parse.urlencode(params)).geturl()
    ListVideos(search_url, page=params['page'])


@site.register()
def Categories(url=None):
    """List categories via the WP API."""
    api_url = url or CATEGORIES_API
    response = utils.getHtml(api_url, site.url)
    if not response:
        utils.notify('Unable to load categories')
        utils.eod()
        return

    try:
        categories = json.loads(response)
    except ValueError:
        utils.notify('Invalid category response')
        utils.eod()
        return

    for category in categories:
        cat_id = category.get('id')
        name = category.get('name') or 'Category'
        count = category.get('count') or 0
        label = f"{name} ({count})"
        posts_url = f"{POSTS_API}?categories={cat_id}"
        site.add_dir(label, posts_url, 'ListVideos', site.img_cat)

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

    response = utils._getHtml(  # pylint: disable=protected-access
        post_url,
        snapshot['page_url'],
        headers=headers,
        data=json.dumps(payload)
    )
    if not response:
        return None

    try:
        data = json.loads(response)
    except ValueError:
        utils.kodilog('ArchiveBate: unexpected Livewire response')
        return None

    effects = data.get('effects') or {}
    return effects.get('html')


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
