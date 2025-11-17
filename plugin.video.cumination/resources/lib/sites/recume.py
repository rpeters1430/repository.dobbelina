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

import json
import re
from datetime import datetime

from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('recume', '[COLOR hotpink]Recu.me[/COLOR]', 'https://recu.me/',
                 'https://recu.me/favicon.ico', 'recume')

API_PAGE_SIZE = 36
API_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': utils.base_hdrs.get('User-Agent', '')
}


def _build_posts_url(page=1, search=None, category=None):
    params = {
        'page': page,
        'per_page': API_PAGE_SIZE,
        '_embed': '1',
        'orderby': 'date',
        'order': 'desc'
    }
    if search:
        params['search'] = search
    if category:
        params['categories'] = category
    query = urllib_parse.urlencode(params)
    return urllib_parse.urljoin(site.url, 'wp-json/wp/v2/posts?{}'.format(query))


def _build_categories_url():
    return urllib_parse.urljoin(site.url, 'wp-json/wp/v2/categories?per_page=100&orderby=name&order=asc')


def _fetch_json(url):
    response = utils.getHtml(url, headers=API_HEADERS)
    if not response:
        return []
    try:
        data = json.loads(response)
    except ValueError:
        utils.kodilog('Recu.me: failed to parse JSON for {}'.format(url))
        return []
    if isinstance(data, dict) and data.get('code'):
        utils.kodilog('Recu.me API error {}: {}'.format(data.get('code'), data.get('message', 'Unknown error')))
        utils.notify('Recu.me', data.get('message', 'Failed to load data'))
        return []
    return data


def _strip_html(text):
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', ' ', text)
    return utils.cleantext(text)


def _extract_image(post):
    embedded = post.get('_embedded') or {}
    media = embedded.get('wp:featuredmedia') or []
    if isinstance(media, list):
        for item in media:
            source = item.get('source_url') if isinstance(item, dict) else None
            if source:
                return source
    jetpack = post.get('jetpack_featured_media_url')
    if jetpack:
        return jetpack
    featured = post.get('better_featured_image')
    if isinstance(featured, dict):
        return featured.get('source_url')
    return ''


def _extract_duration(text):
    if not text:
        return ''
    match = re.search(r'(\d{1,2}:\d{2}:\d{2})', text)
    if match:
        return match.group(1)
    match = re.search(r'(\d{1,2}:\d{2})', text)
    if match:
        return match.group(1)
    match = re.search(r'(\d{1,2}h\d{1,2}m(?:\d{1,2}s)?)', text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return ''


def _extract_quality(text):
    if not text:
        return ''
    match = re.search(r'(\d{3,4}p)', text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return ''


def _format_description(post):
    excerpt = _strip_html(post.get('excerpt', {}).get('rendered', ''))
    content = post.get('content', {}).get('rendered', '')
    published = post.get('date') or ''
    date_str = ''
    if published:
        try:
            dt = datetime.strptime(published.split('+')[0], '%Y-%m-%dT%H:%M:%S')
            date_str = dt.strftime('%Y-%m-%d')
        except ValueError:
            date_str = published.split('T')[0]
    parts = []
    if date_str:
        parts.append('Published: {}'.format(date_str))
    if excerpt:
        parts.append(excerpt)
    elif content:
        parts.append(_strip_html(content)[:220])
    return '[CR]'.join(parts)


def _get_next_page_url(url, current_len):
    parsed = urllib_parse.urlparse(url)
    params = dict(urllib_parse.parse_qsl(parsed.query, keep_blank_values=True))
    try:
        per_page = int(params.get('per_page', API_PAGE_SIZE))
    except ValueError:
        per_page = API_PAGE_SIZE
    if current_len < per_page:
        return None
    try:
        page = int(params.get('page', 1)) + 1
    except ValueError:
        page = 2
    params['page'] = str(page)
    new_query = urllib_parse.urlencode(params)
    parsed = parsed._replace(query=new_query)
    return urllib_parse.urlunparse(parsed), page


@site.register(default_mode=True)
def Main(url=None):
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', _build_categories_url(), 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url, 'Search', site.img_search)
    List(_build_posts_url())


@site.register()
def List(url):
    posts = _fetch_json(url)
    if not posts:
        utils.eod()
        return
    seen = set()
    for post in posts:
        if not isinstance(post, dict):
            continue
        link = post.get('link') or ''
        if not link:
            slug = post.get('slug')
            if slug:
                link = urllib_parse.urljoin(site.url, slug + '/')
        if not link or link in seen:
            continue
        seen.add(link)
        title = _strip_html(post.get('title', {}).get('rendered', '')) or 'Video'
        thumb = _extract_image(post)
        content_html = post.get('content', {}).get('rendered', '')
        duration = _extract_duration(content_html)
        quality = _extract_quality(content_html)
        description = _format_description(post)
        site.add_download_link(title, link, 'Playvid', thumb, description, duration=duration, quality=quality)
    next_info = _get_next_page_url(url, len(posts))
    if next_info:
        next_url, page_no = next_info
        site.add_dir('Next Page ({})'.format(page_no), next_url, 'List', site.img_next)
    utils.eod()


@site.register()
def Categories(url):
    categories = _fetch_json(url or _build_categories_url())
    if not categories:
        utils.eod()
        return
    for cat in sorted(categories, key=lambda x: x.get('name', '').lower() if isinstance(x, dict) else ''):
        if not isinstance(cat, dict):
            continue
        cat_id = cat.get('id')
        if not cat_id:
            continue
        name = utils.cleantext(cat.get('name', 'Category'))
        count = cat.get('count', 0)
        if count:
            name = '{} [COLOR deeppink]({})[/COLOR]'.format(name, count)
        cat_url = _build_posts_url(category=cat_id)
        site.add_dir(name, cat_url, 'List', site.img_cat)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(site.url, 'Search')
        return
    search_url = _build_posts_url(search=keyword)
    List(search_url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.play_from_site_link(url, site.url)
