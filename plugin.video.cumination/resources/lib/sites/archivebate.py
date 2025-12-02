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

POSTS_API = urllib_parse.urljoin(site.url, 'wp-json/wp/v2/posts')
CATEGORIES_API = urllib_parse.urljoin(site.url, 'wp-json/wp/v2/categories')
POSTS_PER_PAGE = 30


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url, 'Search', site.img_search)
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url, 'Categories', site.img_cat)
    ListVideos(site.url)


@site.register()
def ListVideos(url=None, page=None):
    """List videos using the WordPress posts API."""

    current_page = _resolve_page(url, page)
    api_url = _build_posts_url(url, current_page)
    response = utils.getHtml(api_url, site.url)

    if not response:
        utils.notify('Nothing found')
        utils.eod()
        return

    try:
        posts = json.loads(response)
    except ValueError as exc:  # pragma: no cover - defensive logging
        utils.kodilog('ArchiveBate: Failed to decode posts JSON: {0}'.format(exc))
        utils.notify('Nothing found')
        utils.eod()
        return

    if not isinstance(posts, list):
        utils.kodilog('ArchiveBate: Unexpected posts payload type: {0}'.format(type(posts)))
        utils.notify('Nothing found')
        utils.eod()
        return

    if not posts:
        utils.notify('Nothing found')
        utils.eod()
        return

    for post in posts:
        title = utils.cleantext(_get_nested(post, ['title', 'rendered']))
        url = post.get('link', '')
        thumb = _select_thumb(post)
        description = utils.cleanhtml(_get_nested(post, ['excerpt', 'rendered']))
        duration = _extract_duration(post)

        site.add_download_link(title, url, 'Playvid', thumb, description, duration=duration)

    if len(posts) >= POSTS_PER_PAGE:
        next_page = current_page + 1
        label = '[COLOR hotpink]Next Page ({})[/COLOR]'.format(next_page)
        next_url = _build_posts_url(url or site.url, next_page)
        site.add_dir(label, next_url, 'ListVideos', site.img_next)

    utils.eod()


@site.register()
def Search(url=None, keyword=None):
    """Search for videos via the posts API."""
    if not keyword:
        site.search_dir(url or site.url, 'Search')
        return

    search_url = _build_posts_url(url or site.url, search=keyword)
    ListVideos(search_url)


@site.register()
def Categories(url=None):
    """List categories from the WordPress categories API."""
    api_url = url or CATEGORIES_API
    response = utils.getHtml(api_url, site.url)

    if not response:
        utils.notify('Unable to load categories')
        utils.eod()
        return

    try:
        categories = json.loads(response)
    except ValueError as exc:  # pragma: no cover - defensive logging
        utils.kodilog('ArchiveBate: Failed to decode categories JSON: {0}'.format(exc))
        utils.notify('Unable to load categories')
        utils.eod()
        return

    if not isinstance(categories, list):
        utils.kodilog('ArchiveBate: Unexpected categories payload type: {0}'.format(type(categories)))
        utils.notify('Unable to load categories')
        utils.eod()
        return

    if not categories:
        utils.notify('No categories found')
        utils.eod()
        return

    for category in categories:
        cat_id = category.get('id')
        name = category.get('name', '').strip()
        count = category.get('count', 0)

        label = '[COLOR hotpink]{0} ({1})[/COLOR]'.format(name, count)
        cat_url = '{0}?categories={1}&page=1'.format(POSTS_API, cat_id)
        site.add_dir(label, cat_url, 'ListVideos', site.img_cat)

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
    return node if node is not None else default


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


def _build_posts_url(url, page=None, search=None):
    """Construct a posts API URL with pagination and optional search."""
    base_url = url or POSTS_API
    parsed = urllib_parse.urlparse(base_url)
    if not parsed.path or parsed.path == '/':
        api_path = urllib_parse.urlparse(POSTS_API).path
        parsed = parsed._replace(path=api_path)
    params = dict(urllib_parse.parse_qsl(parsed.query, keep_blank_values=True))
    params.setdefault('per_page', str(POSTS_PER_PAGE))
    if page is None:
        try:
            page_value = int(params.get('page', 1))
        except (TypeError, ValueError):
            page_value = 1
    else:
        try:
            page_value = int(page)
        except (TypeError, ValueError):
            page_value = 1
    params['page'] = str(page_value)
    if search:
        params['search'] = search
    query = urllib_parse.urlencode(params)
    return urllib_parse.urlunparse(parsed._replace(query=query))


def _extract_duration(post):
    """Pull duration from the ACF field or rendered content."""
    acf = post.get('acf') or {}
    duration = acf.get('duration')
    if duration:
        return duration

    rendered = utils.cleantext(_get_nested(post, ['content', 'rendered'])) or ''
    match = re.search(r'(\d{1,2}:\d{2})', rendered)
    return match.group(1) if match else ''


def _resolve_page(url, page=None):
    try:
        if page is not None:
            return int(page)
    except (TypeError, ValueError):
        return 1

    if url:
        parsed = urllib_parse.urlparse(url)
        params = dict(urllib_parse.parse_qsl(parsed.query, keep_blank_values=True))
        try:
            return int(params.get('page', 1))
        except (TypeError, ValueError):
            return 1

    return 1
