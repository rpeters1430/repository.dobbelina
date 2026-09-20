"""
    Plugin for ResolveURL
    Copyright (C) 2016 gujal

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

import re
import json
from resolveurl import common
from resolveurl.lib import helpers
from resolveurl.resolver import ResolveUrl, ResolverError


def _balanced_json(text, start):
    """Return the JSON array/object beginning at start without over-capturing."""
    opening = text[start]
    closing = ']' if opening == '[' else '}'
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return None


def _decode_js_string(value):
    """Decode the quoted argument passed to JSON.parse."""
    quote = value[0]
    if quote == '"':
        return json.loads(value)

    return (value[1:-1]
            .replace('\\/', '/')
            .replace('\\\'', "'")
            .replace('\\\\', '\\'))


def _extract_quality_items(html):
    match = re.search(r'qualityItems_[a-zA-Z0-9_]*\s*=\s*', html)
    if not match:
        return []

    value = html[match.end():].lstrip()
    if value.startswith('JSON.parse('):
        value = value[len('JSON.parse('):].lstrip()
        quote = value[0]
        escaped = False
        for index in range(1, len(value)):
            char = value[index]
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                return json.loads(_decode_js_string(value[:index + 1]))
        return []

    if value.startswith('['):
        payload = _balanced_json(value, 0)
        return json.loads(payload) if payload else []
    return []


def _extract_media_definitions(html):
    match = re.search(r'["\']mediaDefinitions["\']\s*:\s*', html)
    if not match:
        return []
    value = html[match.end():].lstrip()
    if not value.startswith('['):
        return []
    payload = _balanced_json(value, 0)
    return json.loads(payload) if payload else []


def _quality_label(value):
    if str(value).upper() in ('4K', 'UHD'):
        return '2160p'
    return value


class PornHubResolver(ResolveUrl):
    name = 'pornhub'
    domains = ['pornhub.com']
    pattern = r'(?://|\.)(pornhub\.com)/(?:view_video\.php\?viewkey=|embed/)([a-zA-Z0-9]+)'

    def get_media_url(self, host, media_id):
        host_url = 'https://www.{0}/'.format(host)
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': host_url,
                   'Cookie': 'accessAgeDisclaimerPH=1; accessAgeDisclaimerUK=1'}

        html = self.net.http_GET(web_url, headers=headers).content
        sources = []

        quality_items = _extract_quality_items(html)
        if quality_items:
            sources = [(_quality_label(src.get('text')), src.get('url'))
                       for src in quality_items if src.get('url')]

        if not sources:
            sections = re.findall(r'(var\sra[a-z0-9]+=.+?);flash', html)
            for section in sections:
                pvars = re.findall(r'var\s(ra[a-z0-9]+)=([^;]+)', section)
                link = re.findall(r'var\smedia_\d+=([^;]+)', section)[0]
                link = re.sub(r"/\*.+?\*/", '', link)
                for key, value in pvars:
                    link = re.sub(key, value, link)
                link = link.replace('"', '').split('+')
                link = [i.strip() for i in link]
                link = ''.join(link)
                if 'urlset' not in link:
                    r = re.findall(r'(\d+p)', link, re.I)
                    if r:
                        sources.append((r[0], link))

        if not sources:
            definitions = _extract_media_definitions(html)
            sources = [
                (
                    _quality_label(src.get('quality') or src.get('defaultQuality')),
                    src.get('videoUrl') or src.get('url'),
                )
                for src in definitions
                if not isinstance(src.get('quality'), list)
                and (src.get('videoUrl') or src.get('url'))
            ]

        if sources:
            headers.update({'Origin': host_url.rstrip('/')})
            return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)

        raise ResolverError('File not found or not Free')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/view_video.php?viewkey={media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
