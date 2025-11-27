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
    ListVideos(page_url or site.url)


@site.register()
def ListVideos(url, page_url=None):
    page_url = page_url or url or site.url
    snapshot = _get_livewire_snapshot(page_url)
    if not snapshot:
        utils.notify('ArchiveBate', 'Unable to load listing')
        utils.eod()
        return

    component_html = _call_livewire(snapshot)
    if not component_html:
        utils.notify('ArchiveBate', 'No response from server')
        utils.eod()
        return

    soup = utils.parse_html(component_html)
    videos = _parse_video_items(soup)

    if not videos:
        utils.notify('ArchiveBate', 'No videos found')

    for video in videos:
        site.add_download_link(
            video['title'],
            video['url'],
            'Playvid',
            video['thumb'],
            video['description'],
            duration=video['duration']
        )

    next_url = _find_next_page(soup, snapshot['page_url'])
    if next_url:
        label = '[COLOR hotpink]Next Page...[/COLOR] ({})'.format(_extract_page_number(next_url))
        site.add_dir(label, next_url, 'ListVideos', site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None, page=1):
    if not keyword:
        site.search_dir(site.url, 'Search')
        return

    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1

    payload = _search_creators(keyword, page)
    if not payload:
        utils.notify('ArchiveBate', 'No creators found')
        utils.eod()
        return

    creators = payload.get('data') or []
    for creator in creators:
        username = creator.get('username')
        if not username:
            continue
        platform = creator.get('platform')
        gender = creator.get('gender')
        extras = [value for value in (platform, gender) if value]
        label = username
        if extras:
            label = '{} [COLOR hotpink]({})[/COLOR]'.format(username, ' · '.join(extras))
        profile_url = urllib_parse.urljoin(site.url, 'profile/{0}'.format(username))
        site.add_dir(label, profile_url, 'ListVideos', site.img_cat)

    meta = payload.get('meta') or {}
    current_page = int(meta.get('current_page') or page)
    last_page = int(meta.get('last_page') or current_page)
    if current_page < last_page:
        next_label = '[COLOR hotpink]Next Page ({})[/COLOR]'.format(current_page + 1)
        site.add_dir(next_label, url or SEARCH_API, 'Search', site.img_next,
                     keyword=keyword, page=current_page + 1)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.play_from_site_link(url, site.url)


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
