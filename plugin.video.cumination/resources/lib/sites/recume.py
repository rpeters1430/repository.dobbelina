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

from bs4 import BeautifulSoup
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('recume', '[COLOR hotpink]Recu.me[/COLOR]', 'https://recu.me/',
                 'https://recu.me/favicon.ico', 'recume')

API_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': utils.base_hdrs.get('User-Agent', ''),
    'X-Requested-With': 'XMLHttpRequest',
    'X-Requested-By': 'Cumination'
}


def _build_posts_url(page=1, search=None, category=None):
    if search:
        return urllib_parse.urljoin(site.url, '?s={}'.format(search))

    if category:
        if str(page) == '1':
            return category
        return '{}/page/{}/'.format(category.rstrip('/'), page)

    if str(page) == '1':
        return site.url
    return urllib_parse.urljoin(site.url, 'page/{}/'.format(page))


def _build_categories_url():
    return urllib_parse.urljoin(site.url, 'wp-json/wp/v2/categories?per_page=100&orderby=name&order=asc')


def _fetch_json(url):
    headers = API_HEADERS.copy()
    if not headers.get('User-Agent'):
        headers['User-Agent'] = utils.base_hdrs.get('User-Agent', '')

    response = None
    try:
        response = utils._getHtml(  # pylint: disable=protected-access
            url, referer=site.url, headers=headers
        )
    except Exception as exc:  # pragma: no cover - surfaced in Kodi log
        utils.kodilog('Recu.me request failed: {}'.format(exc))

    if not response or utils.is_cloudflare_challenge_page(response):
        try:
            response = utils.flaresolve(url, site.url)
        except Exception as exc:  # pragma: no cover
            utils.kodilog('Recu.me FlareSolverr error: {}'.format(exc))
            return []

    if not response:
        return []

    try:
        data = json.loads(response)
    except ValueError:
        preview = response[:800] + '...' if len(response) > 800 else response
        utils.kodilog('Recu.me: failed to parse JSON for {} (snippet: {})'.format(url, preview))
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
            date_part = published.split('T')[0]
            dt = datetime.strptime(date_part, '%Y-%m-%d')
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
@site.register(default_mode=True)
def Main(url=None):
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', _build_categories_url(), 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url, 'Search', site.img_search)
    List(_build_posts_url())
    utils.eod()


@site.register()
def List(url):
    html_response = utils._getHtml(url, referer=site.url, headers=API_HEADERS)

    if not html_response or utils.is_cloudflare_challenge_page(html_response):
        html_response = utils.flaresolve(url, site.url)

    if not html_response:
        utils.eod()
        return

    soup = BeautifulSoup(html_response, 'html.parser')
    posts = soup.find_all('article')

    for post in posts:
        link_tag = post.find('a')
        if not link_tag:
            continue

        link = link_tag.get('href')
        title = link_tag.get('title') or link_tag.get_text(strip=True)
        if not link or not title:
            continue

        img_tag = post.find('img')
        thumb = img_tag.get('src') if img_tag else ''
        description = 'Found on Recu.me'

        site.add_download_link(title, link, 'Playvid', thumb, description)

    if posts:
        current_page = 1
        match = re.search(r'page/(\d+)', url)
        if match:
            current_page = int(match.group(1))

        next_page = current_page + 1

        if 's=' not in url:
            base_url = re.sub(r'page/\d+/?', '', url).rstrip('/')
            if not base_url:
                base_url = site.url.rstrip('/')
            next_url = '{}/page/{}/'.format(base_url, next_page)
            site.add_dir('Next Page ({})'.format(next_page), next_url, 'List', site.img_next)

    utils.eod()


@site.register()
def Categories(url):
    base_url = url or _build_categories_url()
    parsed_url = urllib_parse.urlparse(base_url)
    params = dict(urllib_parse.parse_qsl(parsed_url.query))
    try:
        per_page = int(params.get('per_page', 100))
    except ValueError:
        per_page = 100

    all_categories = []
    page = 1
    while True:
        params['page'] = page
        paged_query = urllib_parse.urlencode(params)
        paged_url = urllib_parse.urlunparse(parsed_url._replace(query=paged_query))
        categories = _fetch_json(paged_url)
        if not categories:
            break
        all_categories.extend(categories)
        if len(categories) < per_page:
            break
        page += 1

    if not all_categories:
        utils.eod()
        return

    for cat in sorted(all_categories, key=lambda x: x.get('name', '').lower() if isinstance(x, dict) else ''):
        if not isinstance(cat, dict):
            continue
        name = utils.cleantext(cat.get('name', 'Category'))
        if not name:
            continue
        count = cat.get('count', 0)
        if count:
            name = '{} [COLOR deeppink]({})[/COLOR]'.format(name, count)
        cat_link = cat.get('link') or ''
        if not cat_link:
            slug = cat.get('slug')
            if slug:
                cat_link = urllib_parse.urljoin(site.url, 'category/{}/'.format(slug.strip('/')))
        if not cat_link:
            continue
        cat_url = _build_posts_url(category=cat_link)
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
