"""
    Cumination
    Copyright (C) 2025 Team Cumination

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

from __future__ import annotations

import re
from collections import OrderedDict
from typing import Dict, Iterable, List, Optional, Tuple

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    'peachurnet',
    '[COLOR hotpink]PeachUrNet[/COLOR]',
    'https://peachurnet.com/',
    'https://peachurnet.com/favicon-32x32.png',
    'peachurnet'
)

HOME_CACHE: Dict[str, Optional[Iterable]] = {
    'sections': None,
    'search': None,
}

VIDEO_HOST_PATTERN = re.compile(r'https?://[^"\']+?(?:m3u8|mp4|m4v|webm)', re.IGNORECASE)
STYLE_URL_PATTERN = re.compile(r"url\(['\"]?(?P<url>[^)\'\"]+)['\"]?\)")
DURATION_CLASSES = re.compile(r'duration|length', re.IGNORECASE)
META_CLASSES = re.compile(r'(meta|info|date|views|category)', re.IGNORECASE)


def _home_url() -> str:
    return urllib_parse.urljoin(site.url, 'en')


def _ensure_headers() -> Dict[str, str]:
    headers = utils.base_hdrs.copy()
    headers['Referer'] = site.url
    headers['Origin'] = site.url.rstrip('/')
    return headers


def _absolute_url(url: str, base: Optional[str] = None) -> str:
    if not url:
        return ''
    url = url.strip()
    if url.startswith('//'):
        return 'https:' + url
    if url.startswith('http'):
        return url
    base_url = base or site.url
    return urllib_parse.urljoin(base_url, url.lstrip('/'))


def _clean_image(img: str) -> str:
    if not img:
        return ''
    img = img.strip()
    if ' ' in img and img.startswith('http'):
        img = img.split(' ')[0]
    if img.startswith('//'):
        img = 'https:' + img
    if img.startswith('/'):
        img = urllib_parse.urljoin(site.url, img.lstrip('/'))
    return img


def _extract_from_style(style_value: str) -> str:
    if not style_value:
        return ''
    match = STYLE_URL_PATTERN.search(style_value)
    return _clean_image(match.group('url')) if match else ''


def _cache_homepage_metadata(force: bool = False) -> None:
    global HOME_CACHE
    if HOME_CACHE['sections'] is not None and HOME_CACHE['search'] is not None and not force:
        return

    try:
        html = utils.getHtml(_home_url(), headers=_ensure_headers())
    except Exception as exc:  # pragma: no cover - network/runtime issues surfaced to Kodi UI
        utils.kodilog('peachurnet Main load error: {}'.format(exc))
        HOME_CACHE['sections'] = []
        HOME_CACHE['search'] = urllib_parse.urljoin(site.url, 'en/search?q=')
        return

    soup = utils.parse_html(html)
    sections: List[Tuple[str, str]] = []
    seen = set()

    for anchor in soup.select('nav a[href], header a[href]'):
        label = utils.safe_get_text(anchor)
        href = utils.safe_get_attr(anchor, 'href')
        if not label or not href:
            continue
        label = label.strip()
        href = href.strip()
        if len(label) < 2 or label.lower() in {'home', 'blog', 'sign in', 'login'}:
            continue
        if '/video/' in href or href.startswith('#'):
            continue
        full_url = _absolute_url(href)
        if not full_url.startswith(site.url):
            continue
        if full_url in seen:
            continue
        seen.add(full_url)
        sections.append((label, full_url))

    HOME_CACHE['sections'] = sections
    HOME_CACHE['search'] = _discover_search_endpoint(soup)


def _discover_search_endpoint(soup) -> str:
    fallback = urllib_parse.urljoin(site.url, 'en/search?q=')
    for form in soup.find_all('form'):
        method_attr = utils.safe_get_attr(form, 'method')
        method = method_attr.lower() if method_attr else 'get'
        if method != 'get':
            continue
        input_tag = form.find('input', attrs={'name': re.compile('q|keyword|search', re.IGNORECASE)})
        if not input_tag:
            continue
        action = utils.safe_get_attr(form, 'action', default='') or '/en/search'
        base = _absolute_url(action)
        query_name = input_tag.get('name', 'q')
        separator = '&' if '?' in base else '?'
        return f'{base}{separator}{query_name}='
    return fallback


def _extract_title(element) -> str:
    if not element:
        return ''
    for selector in ['.title', '.video-title', 'h3', 'h2', 'h4', 'p', 'span']:
        node = element.select_one(selector)
        if node:
            title = utils.safe_get_text(node)
            if title:
                return title
    title = utils.safe_get_text(element)
    if title:
        return title
    parent = element.find_parent()
    return utils.safe_get_text(parent) if parent else ''


def _extract_thumbnail(element) -> str:
    img_tag = element.select_one('img')
    if img_tag:
        thumb = utils.safe_get_attr(img_tag, 'data-src', ['data-original', 'data-lazy-src', 'src', 'data-srcset', 'srcset'])
        if thumb and ' ' in thumb and thumb.startswith('http'):
            thumb = thumb.split(' ')[0]
        if thumb:
            return _clean_image(thumb)
    style_thumb = _extract_from_style(utils.safe_get_attr(element, 'style'))
    if style_thumb:
        return style_thumb
    parent = element.find_parent()
    if parent:
        return _extract_thumbnail(parent)
    return ''


def _extract_duration(element) -> str:
    for target in (element, element.find_parent() if element else None):
        if not target:
            continue
        attr_duration = target.get('data-duration') or target.get('data-length')
        if attr_duration:
            return attr_duration.strip()
        duration_tag = target.find(attrs={'class': DURATION_CLASSES})
        if duration_tag:
            duration = utils.safe_get_text(duration_tag)
            if duration:
                return duration
    return ''


def _extract_metadata(element) -> str:
    parent = element.find_parent()
    meta_bits: List[str] = []
    search_target = parent if parent else element
    if not search_target:
        return ''
    for meta_tag in search_target.find_all(['span', 'div', 'time'], limit=6):
        css = ' '.join(meta_tag.get('class', []))
        if css and META_CLASSES.search(css):
            text = utils.safe_get_text(meta_tag)
            if text:
                meta_bits.append(text)
                continue
        if meta_tag.name == 'time':
            meta_bits.append(utils.safe_get_text(meta_tag))
    joined = ' | '.join(bit for bit in meta_bits if bit)
    return joined


def _parse_video_cards(soup) -> List[Dict[str, str]]:
    cards: List[Dict[str, str]] = []
    seen = set()
    for link in soup.select('a[href*="/video/"]'):
        href = utils.safe_get_attr(link, 'href')
        if not href:
            continue
        href = href.split('#')[0]
        if '/video/' not in href:
            continue
        key = href
        if key in seen:
            continue
        seen.add(key)
        title = utils.cleantext(_extract_title(link))
        if not title:
            continue
        thumb = _extract_thumbnail(link)
        duration = _extract_duration(link)
        meta = _extract_metadata(link)
        plot_parts = [title]
        if duration:
            plot_parts.append(f'Duration: {duration}')
        if meta:
            plot_parts.append(meta)
        plot = '\n'.join(plot_parts)
        cards.append({
            'title': title,
            'url': _absolute_url(href),
            'thumb': thumb,
            'plot': plot,
        })
    return cards


def _find_next_page(soup, current_url: str) -> str:
    selectors = [
        'a[rel="next"]',
        'a[aria-label*="next" i]',
        '.pagination a.next',
        'li.next a',
    ]
    for selector in selectors:
        link = soup.select_one(selector)
        if link:
            href = utils.safe_get_attr(link, 'href')
            if href:
                return _absolute_url(href, current_url)
    for link in soup.find_all('a', string=re.compile('next', re.IGNORECASE)):
        href = utils.safe_get_attr(link, 'href')
        if href:
            return _absolute_url(href, current_url)
    return ''


def _gather_video_sources(html: str, base_url: str) -> OrderedDict:
    soup = utils.parse_html(html)
    sources: OrderedDict[str, str] = OrderedDict()

    def _add_source(src: str):
        if not src:
            return
        link = _absolute_url(src, base_url)
        if not link or link in sources.values():
            return
        host = utils.get_vidhost(link)
        sources[host] = link

    for tag in soup.select('video source[src], source[data-src], source[data-hls], source[data-mp4]'):
        _add_source(utils.safe_get_attr(tag, 'src', ['data-src', 'data-hls', 'data-mp4']))

    for tag in soup.select('[data-src], [data-hls], [data-mp4], [data-video]'):
        _add_source(utils.safe_get_attr(tag, 'data-src', ['data-hls', 'data-mp4', 'data-video']))

    for iframe in soup.select('iframe[src]'):
        _add_source(utils.safe_get_attr(iframe, 'src'))

    for match in VIDEO_HOST_PATTERN.findall(html):
        _add_source(match)

    return sources


@site.register(default_mode=True)
def Main():
    _cache_homepage_metadata()
    site.add_dir('[COLOR hotpink]Latest Updates[/COLOR]', _home_url(), 'List', site.img_cat)
    sections = HOME_CACHE.get('sections') or []
    for label, url in sections:
        site.add_dir(f'[COLOR hotpink]{label}[/COLOR]', url, 'List', site.img_cat)
    search_url = HOME_CACHE.get('search') or urllib_parse.urljoin(site.url, 'en/search?q=')
    site.add_dir('[COLOR hotpink]Search[/COLOR]', search_url, 'Search', site.img_search)
    utils.eod()


@site.register()
def List(url):
    target_url = _absolute_url(url)
    try:
        html = utils.getHtml(target_url, headers=_ensure_headers())
    except Exception as exc:  # pragma: no cover - surfaced to Kodi UI
        utils.kodilog('peachurnet List load error: {}'.format(exc))
        utils.notify('PeachUrNet', 'Unable to load listing page')
        utils.eod()
        return

    soup = utils.parse_html(html)
    videos = _parse_video_cards(soup)

    if not videos:
        utils.notify('PeachUrNet', 'No videos found on this page')

    for video in videos:
        site.add_download_link(video['title'], video['url'], 'Playvid', video['thumb'], video['plot'])

    next_page = _find_next_page(soup, target_url)
    if next_page:
        site.add_dir('[COLOR hotpink]Next Page...[/COLOR]', next_page, 'List', site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    _cache_homepage_metadata()
    search_base = HOME_CACHE.get('search') or urllib_parse.urljoin(site.url, 'en/search?q=')
    if not keyword:
        site.search_dir(search_base, 'Search')
        return
    search_url = f'{search_base}{urllib_parse.quote_plus(keyword)}'
    List(search_url)


@site.register()
def Playvid(url, name, download=None):
    videopage = _absolute_url(url)
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    try:
        html = utils.getHtml(videopage, headers=_ensure_headers())
    except Exception as exc:  # pragma: no cover - surfaced to Kodi UI
        utils.kodilog('peachurnet Playvid load error: {}'.format(exc))
        vp.progress.close()
        utils.notify('PeachUrNet', 'Unable to load video page')
        return

    sources = _gather_video_sources(html, videopage)
    if not sources:
        vp.progress.close()
        utils.notify('PeachUrNet', 'No playable sources found')
        return

    videourl = utils.selector('Select source', sources)
    if not videourl:
        vp.progress.close()
        return

    vp.play_from_link_to_resolve(videourl)
