'''
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
'''

import re
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('americass', '[COLOR hotpink]Americass[/COLOR]', 'https://americass.net/', 'americass.png', 'americass')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Models[/COLOR]', site.url + 'actor/', 'ActorABC', site.img_cat)
    site.add_dir('[COLOR hotpink]Tags[/COLOR]', site.url + 'tag/', 'Tags', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'video/search/', 'Search', site.img_search)
    List(site.url + 'video?page=1')
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, '')
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return

    for wrapper in soup.select('.wrapper'):
        link = wrapper.select_one('a[href]')
        if not link:
            continue

        videopage = utils.safe_get_attr(link, 'href', default='')
        if not videopage:
            continue

        videopage = videopage.lstrip('/')
        videopage = site.url + videopage.replace('interstice-ad?path=/', '')

        img_tag = wrapper.select_one('img[data-src]')
        img = utils.safe_get_attr(img_tag, 'data-src', ['src'])
        if img and img.startswith('//'):
            img = 'https:' + img

        duration_elem = wrapper.select_one('.duration-overlay')
        duration = utils.safe_get_text(duration_elem, default='')

        name_elem = wrapper.select_one('.mb-0')
        name = utils.cleantext(utils.safe_get_text(name_elem, default=''))

        if not name:
            continue

        contexturl = (utils.addon_sys
                      + "?mode=americass.Lookupinfo"
                      + "&url=" + urllib_parse.quote_plus(videopage))
        contextmenu = [('[COLOR deeppink]Lookup info[/COLOR]', 'RunPlugin(' + contexturl + ')')]

        site.add_download_link(name, videopage, 'Playvid', img, name, contextm=contextmenu, duration=duration)

    next_link = soup.select_one('a[rel="next"][href]')
    if next_link:
        np = utils.safe_get_attr(next_link, 'href', default='')
        if np:
            np = np.lstrip('/')
            np = site.url + np
            site.add_dir('Next Page...', np, 'List', site.img_next)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, site.url)
    r = re.compile(r"src=\\u0022([^ ]+)\\u0022", re.DOTALL | re.IGNORECASE).search(videopage)
    if r:
        videourl = r.group(1).replace('\\/', '/')
        vp.progress.update(75, "[CR]Video found[CR]")
        vp.play_from_direct_link(videourl)
    else:
        r = re.compile(r'<iframe.+?src="([^"]+)', re.DOTALL | re.IGNORECASE).search(videopage)
        if r:
            vp.progress.update(75, "[CR]Video found[CR]")
            vp.play_from_link_to_resolve(r.group(1))
        else:
            vp.progress.close()
            utils.notify('Oh oh', 'Couldn\'t find a playable link')


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        title = keyword.replace(' ', '%20')
        searchUrl = url + title
        List(searchUrl)


@site.register()
def Tags(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return

    for link in soup.select('a[href*="/tag/"]'):
        tagpage = utils.safe_get_attr(link, 'href', default='')
        if not tagpage or not tagpage.startswith('/tag'):
            continue

        tag = utils.cleantext(utils.safe_get_text(link, default=''))
        # Try to find video count (usually in next sibling or nearby element)
        videos = ''
        next_elem = link.find_next_sibling()
        if next_elem:
            videos = utils.safe_get_text(next_elem, default='')

        if tag:
            tag_name = '{} - Videos {}'.format(tag, videos) if videos else tag
            site.add_dir(tag_name, site.url + tagpage.lstrip('/'), 'List', '')

    utils.eod()


@site.register()
def ActorABC(url):
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    for letter in letters:
        actorpage = url + '?l=' + letter.lower()
        site.add_dir(letter, actorpage, 'Actor', '')
    utils.eod()


@site.register()
def Actor(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return

    for link in soup.select('a[href*="/actor/"]'):
        actorpage = utils.safe_get_attr(link, 'href', default='')
        if not actorpage or not actorpage.startswith('/actor'):
            continue

        img_tag = link.select_one('img[src]')
        img = utils.safe_get_attr(img_tag, 'src', default='')
        if img and not img.startswith('http'):
            img = site.url + img.lstrip('/')

        label_elem = link.select_one('.label')
        name = utils.cleantext(utils.safe_get_text(label_elem, default=''))

        if name:
            site.add_dir(name, site.url + actorpage.lstrip('/'), 'List', img)

    next_link = soup.select_one('a[rel="next"][href]')
    if next_link:
        np = utils.safe_get_attr(next_link, 'href', default='')
        if np:
            np = np.lstrip('/')
            site.add_dir('Next Page...', site.url + np, 'Actor', site.img_next)
    utils.eod()


@site.register()
def Lookupinfo(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    if not soup:
        return

    lookup_items = []

    # Find actors
    for link in soup.select('a[href*="/actor/"]'):
        actor_url = utils.safe_get_attr(link, 'href', default='')
        name_elem = link.select_one('.name')
        actor_name = utils.cleantext(utils.safe_get_text(name_elem, default=''))
        if actor_url and actor_name and '/actor/' in actor_url:
            actor_url = site.url + actor_url.lstrip('/')
            lookup_items.append(('Actor', actor_name, actor_url))

    # Find tags
    for link in soup.select('a[href*="/tag/"]'):
        tag_url = utils.safe_get_attr(link, 'href', default='')
        badge_elem = link.select_one('.badge')
        tag_name = utils.cleantext(utils.safe_get_text(badge_elem or link, default=''))
        if tag_url and tag_name and '/tag/' in tag_url:
            tag_url = site.url + tag_url.lstrip('/')
            lookup_items.append(('Tag', tag_name, tag_url))

    if not lookup_items:
        utils.notify('Lookup', 'No actors or tags found')
        return

    utils.kodiDB(lookup_items, 'americass.List')
