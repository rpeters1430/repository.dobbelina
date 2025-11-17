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
from collections import OrderedDict

from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('archivebate', '[COLOR hotpink]ArchiveBate[/COLOR]', 'https://archivebate.com/', 'https://archivebate.com/favicon.ico', 'archivebate')

POSTS_PER_PAGE = 30
CATEGORIES_PER_PAGE = 50
POSTS_API = urllib_parse.urljoin(site.url, 'wp-json/wp/v2/posts?per_page={0}&_embed=1&orderby=date&order=desc'.format(POSTS_PER_PAGE))
CATEGORIES_API = urllib_parse.urljoin(site.url, 'wp-json/wp/v2/categories?per_page={0}&page=1&orderby=count&order=desc'.format(CATEGORIES_PER_PAGE))
DIRECT_REGEX = r"""(?:file"?\s*[:=]\s*[\"']|source\s+src=\s*[\"'])([^\"']+(?:\.mp4|\.m3u8)[^\"']*)"""
TAG_RE = re.compile(r'<[^>]+>')
IMG_RE = re.compile(r"<img[^>]+src=[\"']([^\"']+)", re.IGNORECASE)
IFRAME_RE = re.compile(r"<iframe[^>]+src=[\"']([^\"']+)", re.IGNORECASE)


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', CATEGORIES_API, 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', POSTS_API, 'Search', site.img_search)
    ListVideos(POSTS_API, page=1)


@site.register()
def ListVideos(url, page=1):
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1

    list_url = _update_query(url or POSTS_API, page=page)
    payload = utils.getHtml(list_url, site.url)
    if not payload:
        utils.notify(msg='Nothing found')
        utils.eod()
        return

    try:
        items = json.loads(payload)
    except ValueError:
        utils.notify(msg='Unable to load videos')
        utils.eod()
        return

    if isinstance(items, dict):
        if items.get('code'):
            utils.notify(msg=utils.cleantext(items.get('message', 'Nothing found')))
            utils.eod()
            return
        # Some WP endpoints can return dicts instead of lists
        items = items.get('items') or []

    listed = 0
    for post in items:
        if not isinstance(post, dict):
            continue
        link = post.get('link')
        if not link:
            continue
        name = utils.cleantext(post.get('title', {}).get('rendered', ''))
        if not name:
            continue
        img = _get_post_image(post)
        desc = _get_excerpt(post)
        duration = _get_duration(post)
        site.add_download_link(name, link, 'Playvid', img, desc or '', duration=duration or '')
        listed += 1

    if not listed:
        utils.notify(msg='Nothing found')
    else:
        per_page = _get_per_page(url or POSTS_API, default=POSTS_PER_PAGE)
        if listed >= per_page:
            label = '[COLOR hotpink]Next Page...[/COLOR] ({0})'.format(page + 1)
            site.add_dir(label, url or POSTS_API, 'ListVideos', site.img_next, page=page + 1)

    utils.eod()


@site.register()
def Categories(url):
    page_url = url or CATEGORIES_API
    payload = utils.getHtml(page_url, site.url)
    if not payload:
        utils.notify(msg='Nothing found')
        utils.eod()
        return

    try:
        cat_items = json.loads(payload)
    except ValueError:
        utils.notify(msg='Unable to load categories')
        utils.eod()
        return

    if isinstance(cat_items, dict):
        if cat_items.get('code'):
            utils.notify(msg=utils.cleantext(cat_items.get('message', 'Nothing found')))
            utils.eod()
            return
        cat_items = cat_items.get('items') or []

    for category in cat_items:
        if not isinstance(category, dict):
            continue
        cat_id = category.get('id')
        name = utils.cleantext(category.get('name', ''))
        if not cat_id or not name:
            continue
        count = int(category.get('count') or 0)
        label = '{0} [COLOR hotpink]({1})[/COLOR]'.format(name, count) if count else name
        cat_url = _update_query(POSTS_API, categories=cat_id, page=1)
        site.add_dir(label, cat_url, 'ListVideos', site.img_cat, page=1)

    current_page = _get_page_number(page_url)
    per_page = _get_per_page(page_url, default=CATEGORIES_PER_PAGE)
    if len(cat_items) >= per_page:
        next_url = _update_query(page_url, page=current_page + 1)
        site.add_dir('[COLOR hotpink]More categories...[/COLOR]', next_url, 'Categories', site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    base = url or POSTS_API
    if not keyword:
        site.search_dir(base, 'Search')
        return
    keyword = keyword.strip()
    if not keyword:
        site.search_dir(base, 'Search')
        return
    search_url = _update_query(base, search=keyword, page=1)
    ListVideos(search_url, page=1)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download, direct_regex=DIRECT_REGEX)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    html = utils.getHtml(url, site.url)
    if not html:
        utils.notify(msg='Video unavailable')
        return

    iframe = IFRAME_RE.search(html)
    if iframe:
        iframe_url = urllib_parse.urljoin(url, iframe.group(1))
        iframe_html = utils.getHtml(iframe_url, url)
        if iframe_html:
            vp.play_from_html(iframe_html, iframe_url)
            return

    vp.play_from_html(html, url)


def _update_query(url, **params):
    parsed = urllib_parse.urlparse(url)
    query = OrderedDict(urllib_parse.parse_qsl(parsed.query, keep_blank_values=True))
    for key, value in params.items():
        if value is None:
            query.pop(key, None)
        else:
            query[key] = str(value)
    new_query = urllib_parse.urlencode(query, doseq=True)
    return urllib_parse.urlunparse(parsed._replace(query=new_query))


def _get_per_page(url, default):
    parsed = urllib_parse.urlparse(url)
    params = dict(urllib_parse.parse_qsl(parsed.query, keep_blank_values=True))
    value = params.get('per_page')
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _get_page_number(url):
    parsed = urllib_parse.urlparse(url)
    params = dict(urllib_parse.parse_qsl(parsed.query, keep_blank_values=True))
    value = params.get('page')
    try:
        return int(value)
    except (TypeError, ValueError):
        return 1


def _get_post_image(post):
    jetpack_img = post.get('jetpack_featured_media_url')
    if jetpack_img:
        return jetpack_img

    better = post.get('better_featured_image')
    if isinstance(better, dict):
        source = better.get('source_url')
        if source:
            return source
        media_details = better.get('media_details', {})
        sizes = media_details.get('sizes', {}) if isinstance(media_details, dict) else {}
        for key in ('medium_large', 'large', 'full', 'medium'):
            size_data = sizes.get(key)
            if isinstance(size_data, dict) and size_data.get('source_url'):
                return size_data.get('source_url')

    embedded = post.get('_embedded') or {}
    media = embedded.get('wp:featuredmedia')
    if isinstance(media, list) and media:
        media = media[0]
    if isinstance(media, dict):
        source = media.get('source_url')
        if source:
            return source
        media_details = media.get('media_details', {})
        sizes = media_details.get('sizes', {}) if isinstance(media_details, dict) else {}
        for key in ('medium_large', 'large', 'full', 'medium'):
            size_data = sizes.get(key)
            if isinstance(size_data, dict) and size_data.get('source_url'):
                return size_data.get('source_url')

    content = post.get('content', {}).get('rendered', '')
    match = IMG_RE.search(content)
    if match:
        return urllib_parse.urljoin(site.url, match.group(1))

    return site.image


def _get_excerpt(post):
    excerpt = post.get('excerpt', {}).get('rendered') or post.get('content', {}).get('rendered', '')
    if not excerpt:
        return ''
    text = TAG_RE.sub(' ', excerpt)
    text = re.sub(r'\s+', ' ', text).strip()
    return utils.cleantext(text) if text else ''


def _get_duration(post):
    duration_fields = ['duration', 'video_duration', 'videoLength']
    acf = post.get('acf') or {}
    for field in duration_fields:
        value = post.get(field) or acf.get(field)
        if value:
            return utils.cleantext(str(value))
    return ''
