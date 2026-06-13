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

try:
    _unichr = unichr
except NameError:
    _unichr = chr


class PornHubResolver(ResolveUrl):
    name = 'pornhub'
    domains = ['pornhub.com']
    pattern = r'(?://|\.)(pornhub\.com)/(?:view_video\.php\?viewkey=|embed/)([a-zA-Z0-9]+)'

    @staticmethod
    def _decode_js_string_literal(raw_value):
        raw_value = raw_value.lstrip()
        if not raw_value or raw_value[0] not in ("'", '"'):
            return None

        quote = raw_value[0]
        decoded = []
        index = 1
        length = len(raw_value)
        while index < length:
            char = raw_value[index]
            if char == quote:
                return ''.join(decoded)
            if char != '\\':
                decoded.append(char)
                index += 1
                continue

            index += 1
            if index >= length:
                return None
            escaped = raw_value[index]
            escapes = {
                '\\': '\\',
                '/': '/',
                '"': '"',
                "'": "'",
                'b': '\b',
                'f': '\f',
                'n': '\n',
                'r': '\r',
                't': '\t',
            }
            if escaped == 'u' and index + 4 < length:
                hex_value = raw_value[index + 1:index + 5]
                try:
                    decoded.append(_unichr(int(hex_value, 16)))
                    index += 5
                    continue
                except ValueError:
                    return None
            decoded.append(escapes.get(escaped, escaped))
            index += 1
        return None

    @staticmethod
    def _extract_json_assignment(html, name_pattern):
        match = re.search(r'{0}\s*=\s*'.format(name_pattern), html, re.DOTALL | re.IGNORECASE)
        if not match:
            return None
        decoder = json.JSONDecoder()
        raw_value = html[match.end():].lstrip()
        if raw_value.startswith('JSON.parse'):
            parse_match = re.match(r'JSON\.parse\(\s*', raw_value, re.IGNORECASE)
            if parse_match:
                try:
                    parsed_string = PornHubResolver._decode_js_string_literal(
                        raw_value[parse_match.end():]
                    )
                    if parsed_string is None:
                        return None
                    return json.loads(parsed_string)
                except (TypeError, ValueError):
                    return None
        try:
            value, _ = decoder.raw_decode(raw_value)
            return value
        except ValueError:
            return None

    @staticmethod
    def _extract_json_value_after(html, pattern):
        match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if not match:
            return None
        try:
            value, _ = json.JSONDecoder().raw_decode(html[match.end():].lstrip())
            return value
        except ValueError:
            return None

    @classmethod
    def _extract_media_sources(cls, html):
        sources = []

        quality_items = cls._extract_json_assignment(html, r'(?:var\s+)?qualityItems_\d+')
        if isinstance(quality_items, list):
            sources.extend(
                (src.get('text'), src.get('url'))
                for src in quality_items
                if isinstance(src, dict) and src.get('url')
            )

        flashvars = cls._extract_json_assignment(html, r'flashvars_\d+')
        if isinstance(flashvars, dict):
            for src in flashvars.get('mediaDefinitions', []):
                if not isinstance(src, dict):
                    continue
                quality = src.get('quality')
                video_url = src.get('videoUrl')
                if isinstance(quality, list) or not video_url:
                    continue
                sources.append((quality, video_url))

        media_definitions = cls._extract_json_value_after(
            html,
            r'["\']mediaDefinitions["\']\s*:\s*',
        )
        if isinstance(media_definitions, list):
            for src in media_definitions:
                if not isinstance(src, dict):
                    continue
                quality = src.get('quality') or src.get('defaultQuality') or src.get('format')
                video_url = src.get('videoUrl') or src.get('url')
                if isinstance(quality, list) or not video_url:
                    continue
                sources.append((quality, video_url))

        cleaned = []
        seen_urls = set()
        for quality, video_url in sources:
            if video_url in seen_urls:
                continue
            seen_urls.add(video_url)
            cleaned.append((quality, video_url))
        return cleaned

    def get_media_url(self, host, media_id):
        host_url = 'https://www.{0}/'.format(host)
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.RAND_UA,
                   'Referer': host_url,
                   'Cookie': 'accessAgeDisclaimerPH=1; accessAgeDisclaimerUK=1'}

        html = self.net.http_GET(web_url, headers=headers).content
        sources = self._extract_media_sources(html)

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

        if sources:
            headers.update({'Origin': host_url[:-1]})
            sources = self._sort_sources_list(sources)
            return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError('File not found or not Free')

    @staticmethod
    def _source_quality_value(source):
        label = str(source[0] or '')
        if '4k' in label.lower() or 'uhd' in label.lower():
            return 2160
        digits = ''.join(ch for ch in label if ch.isdigit())
        return int(digits) if digits else 0

    @classmethod
    def _sort_sources_list(cls, sources):
        return sorted(sources, key=cls._source_quality_value, reverse=True)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/view_video.php?viewkey={media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
