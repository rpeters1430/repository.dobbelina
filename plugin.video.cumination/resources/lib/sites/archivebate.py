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

    posts = _parse_posts_json(response)
    if posts:
        _render_posts(posts)
        _add_next_dir(current_page, len(posts), url)
        utils.eod()
        return

    html_url = _build_frontend_url(current_page)
    html = utils.getHtml(html_url, site.url)
    entries, next_page_url = _parse_posts_html(html)

    if not entries:
        utils.notify('Nothing found')
        utils.eod()
        return

    _render_posts(entries)

    if next_page_url:
        label = _format_next_label(next_page_url)
        site.add_dir(label, next_page_url, 'ListVideos', site.img_next)

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


def _parse_posts_json(response):
    if not response:
        return []

    try:
        posts = json.loads(response)
    except ValueError as exc:  # pragma: no cover - defensive logging
        utils.kodilog('ArchiveBate: Failed to decode posts JSON: {0}'.format(exc))
        return []

    if not isinstance(posts, list):
        utils.kodilog('ArchiveBate: Unexpected posts payload type: {0}'.format(type(posts)))
        return []

    return posts


def _render_posts(posts):
    for post in posts:
        title = utils.cleantext(_get_nested(post, ['title', 'rendered']))
        url = post.get('link', '')
        thumb = _select_thumb(post)
        description = utils.cleanhtml(_get_nested(post, ['excerpt', 'rendered']))
        duration = _extract_duration(post)

        site.add_download_link(title, url, 'Playvid', thumb, description, duration=duration)


def _add_next_dir(current_page, posts_count, url):
    if posts_count >= POSTS_PER_PAGE:
        next_page = current_page + 1
        label = '[COLOR hotpink]Next Page ({})[/COLOR]'.format(next_page)
        next_url = _build_posts_url(url or site.url, next_page)
        site.add_dir(label, next_url, 'ListVideos', site.img_next)


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


def _parse_posts_html(html):
    if not html:
        return [], None

    try:
        soup = utils.parse_html(html)
    except (ImportError, ValueError) as exc:  # pragma: no cover - defensive logging
        utils.kodilog('ArchiveBate: Failed to parse HTML listing with BeautifulSoup: {0}'.format(exc))
        return _parse_posts_html_no_bs(html)

    entries = []
    for article in soup.select('article'):
        link_el = article.select_one('h2.entry-title a, h3.entry-title a, a[rel="bookmark"]')
        if not link_el:
            continue

        title = utils.cleantext(link_el.get_text())
        url = urllib_parse.urljoin(site.url, link_el.get('href', ''))

        img_el = article.select_one('img')
        thumb = utils.safe_get_attr(img_el, 'data-src', ['data-original', 'src'])

        desc_el = article.select_one('.entry-summary, .entry-content, p')
        description = utils.cleantext(desc_el.get_text()) if desc_el else ''

        duration_el = article.select_one('.duration, .video-duration')
        duration = utils.cleantext(duration_el.get_text()) if duration_el else ''

        entries.append({
            'title': {'rendered': title},
            'link': url,
            'jetpack_featured_media_url': thumb,
            'better_featured_image': {'source_url': thumb} if thumb else {},
            'excerpt': {'rendered': description},
            'content': {'rendered': description},
            'acf': {'duration': duration} if duration else {},
        })

    next_link = _find_next_link(soup)
    return entries, next_link


def _parse_posts_html_no_bs(html):
    entries = []
    for article in re.findall(r'<article[^>]*>(.*?)</article>', html, re.S | re.I):
        link_match = re.search(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)', article, re.I)
        if not link_match:
            continue

        url = urllib_parse.urljoin(site.url, link_match.group(1))
        title = utils.cleantext(link_match.group(2))

        img_match = re.search(r'<img[^>]+(?:data-src|data-original|src)=["\']([^"\']+)["\']', article, re.I)
        thumb = img_match.group(1) if img_match else ''

        desc_match = re.search(r'<(?:div|p)[^>]*(?:entry-summary|entry-content)[^>]*>(.*?)</(?:div|p)>', article, re.S | re.I)
        description = utils.cleantext(desc_match.group(1)) if desc_match else ''

        duration_match = re.search(r'class=["\'][^"\']*(?:duration|video-duration)[^"\']*["\'][^>]*>\s*([0-9]{1,2}:[0-9]{2})', article, re.I)
        duration = duration_match.group(1) if duration_match else ''

        entries.append({
            'title': {'rendered': title},
            'link': url,
            'jetpack_featured_media_url': thumb,
            'better_featured_image': {'source_url': thumb} if thumb else {},
            'excerpt': {'rendered': description},
            'content': {'rendered': description},
            'acf': {'duration': duration} if duration else {},
        })

    next_match = re.search(r'<a[^>]+class=["\'][^"\']*(?:nextpostslink|next|pagination-next|page-numbers\s+next)[^"\']*["\'][^>]+href=["\']([^"\']+)["\']', html, re.I)
    next_link = urllib_parse.urljoin(site.url, next_match.group(1)) if next_match else None
    return entries, next_link


def _find_next_link(soup):
    link = soup.find('a', rel=lambda val: val and 'next' in val.lower())
    if not link:
        link = soup.select_one('a.next, a.nextpostslink, a.pagination-next, a.page-numbers.next')
    return urllib_parse.urljoin(site.url, link.get('href', '')) if link else None


def _format_next_label(next_page_url):
    next_page = _extract_page_number(next_page_url)
    if next_page:
        return '[COLOR hotpink]Next Page ({})[/COLOR]'.format(next_page)
    return '[COLOR hotpink]Next Page[/COLOR]'


def _extract_page_number(url):
    parsed = urllib_parse.urlparse(url or '')
    params = dict(urllib_parse.parse_qsl(parsed.query, keep_blank_values=True))
    try:
        if 'page' in params:
            return int(params.get('page'))
    except (TypeError, ValueError):
        return None

    path_match = re.search(r'/page/(\d+)/?', parsed.path or '')
    if path_match:
        try:
            return int(path_match.group(1))
        except (TypeError, ValueError):
            return None
    return None


def _build_frontend_url(page):
    if page and page > 1:
        return urllib_parse.urljoin(site.url, 'page/{0}/'.format(page))
    return site.url


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
