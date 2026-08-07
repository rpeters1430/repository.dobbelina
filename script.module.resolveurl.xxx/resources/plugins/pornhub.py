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

        qvars = re.search(r'qualityItems_[^=]+=\s*(.+?);(?:\s*</script>|\n|$)', html, re.DOTALL)
        if qvars:
            raw_q = qvars.group(1).strip()
            json_parse_match = re.search(r'^JSON\.parse\((["\'])(.+)\1\)$', raw_q, re.DOTALL)
            if json_parse_match:
                q_str = json_parse_match.group(2).replace(r'\/', '/').replace(r'\"', '"')
                try:
                    data = json.loads(q_str)
                except Exception:
                    data = []
            else:
                try:
                    data = json.loads(raw_q)
                except Exception:
                    data = []
            
            for src in data:
                if isinstance(src, dict) and src.get('url'):
                    q = src.get('text') or src.get('quality') or src.get('defaultQuality') or ''
                    if str(q).upper() == '4K':
                        q = '2160p'
                    sources.append((q, src.get('url')))

        if not sources:
            sections = re.findall(r'(var\sra[a-z0-9]+=.+?);flash', html, re.DOTALL)
            for section in sections:
                pvars = re.findall(r'var\s(ra[a-z0-9]+)=([^;]+)', section)
                link_match = re.findall(r'var\smedia_\d+=([^;]+)', section)
                if link_match:
                    link = link_match[0]
                    link = re.sub(r"/\*.+?\*/", '', link)
                    for key, value in pvars:
                        link = re.sub(key, value, link)
                    link = link.replace('"', '').split('+')
                    link = [i.strip() for i in link]
                    link = ''.join(link)
                    if 'urlset' not in link:
                        r = re.findall(r'(\d+p)', link, re.I)
                        if r:
                            q = r[0]
                            if str(q).upper() == '4K':
                                q = '2160p'
                            sources.append((q, link))

        if not sources:
            mdef_match = re.search(r'"mediaDefinitions"\s*:\s*(\[\s*\{.+?\}\s*\])', html, re.DOTALL)
            if mdef_match:
                try:
                    data = json.loads(mdef_match.group(1))
                    for src in data:
                        if isinstance(src, dict):
                            url = src.get('videoUrl') or src.get('url')
                            q = src.get('quality') or src.get('defaultQuality') or ''
                            if str(q).upper() == '4K':
                                q = '2160p'
                            if url and type(q) is not list:
                                sources.append((q, url))
                except Exception:
                    pass

        if not sources:
            fvars = re.search(r'flashvars_\d+\s*=\s*(\{.+?\});', html, re.DOTALL)
            if fvars:
                try:
                    media_defs = json.loads(fvars.group(1)).get('mediaDefinitions', [])
                    for src in media_defs:
                        if isinstance(src, dict):
                            url = src.get('videoUrl') or src.get('url')
                            q = src.get('quality') or src.get('defaultQuality') or ''
                            if str(q).upper() == '4K':
                                q = '2160p'
                            if url and type(q) is not list:
                                sources.append((q, url))
                except Exception:
                    pass

        if sources:
            headers.update({'Origin': host_url[:-1]})
            return helpers.pick_source(helpers.sort_sources_list(sources)) + helpers.append_headers(headers)

        raise ResolverError('File not found or not Free')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://www.{host}/view_video.php?viewkey={media_id}')

    @classmethod
    def _is_enabled(cls):
        return True
