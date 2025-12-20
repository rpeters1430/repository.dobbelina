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
import json
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite("hentaistream", "[COLOR hotpink]HentaiStream[/COLOR]", 'https://hstream.moe/', "hentaistream.png", "hentaistream")


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Tags[/COLOR]', site.url + 'search?order=recently-uploaded&page=1', 'Tags', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search?search=', 'Search', site.img_search)
    List(site.url + 'search?order=recently-uploaded&page=1')


@site.register()
def List(url, episodes=True):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    # Find all video items with wire:key attribute
    items = soup.find_all('div', attrs={'wire:key': True})

    for item in items:
        link = item.find('a')
        if not link:
            continue

        videopage = utils.safe_get_attr(link, 'href')
        if not videopage:
            continue

        img_tag = link.find('img')
        name = utils.safe_get_attr(img_tag, 'alt')
        img = utils.safe_get_attr(img_tag, 'src')

        # Find quality indicator
        quality_tag = link.find('p', class_='quality')
        if not quality_tag:
            quality_tag = link.find('p')
        hd = utils.safe_get_text(quality_tag, default='')

        if name and img:
            name = utils.cleantext(name)
            hd = " [COLOR orange]{0}[/COLOR]".format(hd.upper().strip()) if hd else ''

            # Ensure full URLs
            if not img.startswith('http'):
                img = site.url + img.lstrip('/')
            if not videopage.startswith('http'):
                videopage = site.url + videopage.lstrip('/')

            fanart_img = img
            cover_img = fanart_img.replace('gallery', 'cover').replace('-0-thumbnail', '')
            site.add_download_link(name, videopage, 'Playvid', cover_img, name, fanart=fanart_img, quality=hd)

    # Handle pagination
    nextregex = 'next' if episodes else 'nextPage'
    next_link = soup.find('a', rel=nextregex)
    if next_link:
        pagelookup = re.search(r"page=(\d+)", url)
        if pagelookup:
            np = int(pagelookup.group(1)) + 1
            url = url.replace("page={0}".format(pagelookup.group(1)), "page={0}".format(np))
            site.add_dir('Next Page ({0})'.format(np), url, 'List', site.img_next)
    utils.eod()


@site.register()
def Tags(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    # Find all label tags with for attribute starting with "tags-"
    labels = soup.find_all('label')
    tags_list = []

    for label in labels:
        for_attr = utils.safe_get_attr(label, 'for')
        if for_attr and for_attr.startswith('tags-'):
            tag_id = for_attr.replace('tags-', '')
            name = utils.safe_get_text(label)
            if tag_id and name:
                tags_list.append((tag_id, name))

    # Sort tags alphabetically
    for tag_id, name in sorted(tags_list, key=lambda x: x[1]):
        name = utils.cleantext(name)
        tagpage = site.url + 'search?order=recently-uploaded&page=1&tags[0]={}'.format(tag_id)
        site.add_dir(name, tagpage, 'List', '', name)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        title = keyword.replace(' ', '%20')
        url = url + title + '&page=1'
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vpage = utils.getHtml(url, site.url)
    soup = utils.parse_html(vpage)

    # Find the hidden input with episode ID
    videoid_input = soup.find('input', {'id': 'e_id', 'type': 'hidden'})
    if videoid_input:
        videoid = utils.safe_get_attr(videoid_input, 'value')
    else:
        videoid = None

    if not videoid:
        utils.notify('Oh Oh', 'No Videos found')
        return

    payload = {'episode_id': videoid}

    hstreamhdrs = utils.base_hdrs
    xsrftoken = get_cookies()
    xsrftoken = urllib_parse.unquote(xsrftoken)
    if not xsrftoken:
        utils.notify('Oh Oh', 'No Videos found')
        return

    hstreamhdrs['x-xsrf-token'] = xsrftoken
    hstreamhdrs['content-type'] = 'application/json'

    videojson = utils._postHtml(site.url + 'player/api', headers=hstreamhdrs, json_data=payload)
    videojson = json.loads(videojson)

    qualities = {'2160': '/2160/manifest.mpd',
                 '1080': '/1080/manifest.mpd',
                 '720': '/720/manifest.mpd'}

    videoquality = utils.prefquality(qualities, sort_by=lambda x: int(x), reverse=True)
    if not videoquality:
        return

    domains = videojson['stream_domains'] + videojson['asia_stream_domains']
    if not len(domains) > 1 or utils.addon.getSetting("dontask") == "true":
        domain = domains[0]
    else:
        domain = utils.selector('Select videohost', domains)
    if not domain:
        return

    videourl = '{}/{}{}'.format(domain, videojson['stream_url'], videoquality)
    suburl = '{}/{}/eng.ass'.format(domain, videojson['stream_url'])

    if utils.checkUrl(suburl):
        utils.playvid(videourl, name, subtitle=suburl)
    else:
        vp = utils.VideoPlayer(name, download)
        vp.progress.update(50, "[CR]Loading video[CR]")
        vp.play_from_direct_link(videourl)


def get_cookies():
    domain = site.url.split('/')[2]
    for cookie in utils.cj:
        if domain in cookie.domain and cookie.name == 'XSRF-TOKEN':
            return cookie.value
    return ''
