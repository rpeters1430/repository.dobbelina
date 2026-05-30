"""
Cumination
Copyright (C) 2023 Team Cumination

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
from urllib.request import Request, urlopen
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('yespornvip', '[COLOR hotpink]YesPorn.vip[/COLOR]', 'https://yesporn.vip/', 'yespornvip.webp', 'yespornvip', category='Video Tubes')


@site.register(default_mode=True)
def Main():
    fetch_homepage()
    kt = get_cookie_for_domain('kt_qparams', site.url)
    if not kt:
        kt = '6i3wgc'

    if '-' in kt:
        kt = kt.split('-')[-1]
    if '&' in kt:
        kt = kt.split('&')[0]

    site.add_dir('[COLOR hotpink]Team Skeet[/COLOR]', site.url + 'channels/team-skeet-' + kt + '/', 'List', site.img_cat)
    site.add_dir('[COLOR hotpink]OnlyFans[/COLOR]', site.url + 'channels/onlyfans-' + kt + '/', 'List', site.img_cat)
    site.add_dir('[COLOR hotpink]Vixen[/COLOR]', site.url + 'channels/vixen-' + kt + '/', 'List', site.img_cat)
    site.add_dir('[COLOR hotpink]Pure Taboo[/COLOR]', site.url + 'channels/puretaboo-' + kt + '/', 'List', site.img_cat)

    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/', 'Search', site.img_search)

    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    for item in soup.select('div.thumb_rel.item'):
        if 'item--adv-thumb' in (item.get('class') or []):
            continue
        link = item.select_one('a[title]')
        if not link:
            continue
        name = utils.safe_get_attr(link, 'title')
        img = utils.safe_get_attr(item.select_one('img'), 'data-webp', ['data-original'])
        quality = utils.safe_get_text(item.select_one('.qualtiy'))
        duration = utils.safe_get_text(item.select_one('.time'))
        embed_el = item.select_one('[data-fav-video-id]')
        if not embed_el:
            continue
        embed = utils.safe_get_attr(embed_el, 'data-fav-video-id')
        if not embed:
            continue
        videopage = site.url + 'embed/' + embed
        site.add_download_link(
            utils.cleantext(name) + ' [COLOR yellow]({})[/COLOR][COLOR hotpink] [{}][/COLOR]'.format(duration, quality),
            videopage, 'Playvid', img, name
        )
    next_el = soup.select_one('a.next[data-parameters]')
    if next_el:
        params = utils.safe_get_attr(next_el, 'data-parameters', default='')
        nextpage = ''
        for part in params.split(';'):
            part = part.strip()
            if part.startswith('from:'):
                nextpage = part.split(':', 1)[1]
                break
        if nextpage:
            base = url.split('?from=')[0] if '?from=' in url else url
            next_url = base + '?from=' + nextpage
            site.add_dir('Next Page... ({})'.format(nextpage), next_url, 'List', site.img_next)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url += keyword.replace(' ', '+')
        List(url + '/')


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    play_from_kt_player(vp, utils.getHtml(url, site.url), url)


def play_from_kt_player(self, html, url=None):
    from resources.lib.decrypters.kvsplayer import kvs_decode
    license = re.search(r"license_code:\s*'(\$\d+)", html, re.DOTALL | re.IGNORECASE)
    if license:
        license = license.group(1)
    match = re.compile(r"video(?:_|_alt_)url\d?:\s*'([^']+)[^;]+?video(?:_|_alt_)url\d?_text:\s*'([^']+)", re.DOTALL | re.IGNORECASE).findall(html)
    if not match:
        match = re.compile(r"video(?:_|_alt_)url\d?: '([^']+)'.+?postfix\s*:\s*'([^']+)'", re.DOTALL | re.IGNORECASE).findall(html)

    sources = {qual: videourl for videourl, qual in match}
    videourl = list(sources.values())[0]
    if videourl.startswith('function/0/'):
        if not license:
            utils.notify('oh_oh', 'Unable to play video: License code not found')
            self.progress.close()
            return
        videourl = kvs_decode(videourl, license)
    videourl += '|User-Agent={0}&Referer={1}'.format(utils.USER_AGENT, url)

    if not videourl:
        self.progress.close()
        return
    self.play_from_direct_link(videourl)


def get_cookie_for_domain(name, domain):
    domain = domain.replace('https://', '').replace('http://', '').split('/')[0]
    for c in utils.cj:
        if c.name == name and domain in c.domain:
            return c.value
    return None


def fetch_homepage():
    try:
        req = Request('https://yesporn.vip/', headers=utils.base_hdrs)
        urlopen(req)
        utils.cj.save(utils.TRANSLATEPATH(utils.cookiePath), ignore_discard=True, ignore_expires=True)
    except Exception as e:
        utils.kodilog("fetch_homepage error: %s" % e)
