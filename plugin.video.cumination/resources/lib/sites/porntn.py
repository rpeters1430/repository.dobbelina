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
from resources.lib.decrypters.kvsplayer import kvs_decode

site = AdultSite('porntn', '[COLOR hotpink]PornTN[/COLOR]', 'https://porntn.com/', 'porntn.png')


@site.register(default_mode=True)
def Main(url):
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'new/?mode=async&function=get_block&block_id=list_categories_categories_list&sort_by=title', 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Tags[/COLOR]', site.url + 'tags/', 'Tags', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/', 'Search', site.img_search)
    List(site.url + '?mode=async&function=get_block&block_id=list_videos_most_recent_videos&sort_by=post_date&from=1', 1)
    utils.eod()


@site.register()
def List(url, page=1):
    try:
        listhtml = utils.getHtml(url, '')
    except Exception:
        return None

    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return

    for item in soup.select('.item'):
        link = item.select_one('a[href][title]')
        if not link:
            continue

        videopage = utils.safe_get_attr(link, 'href', default='')
        if not videopage.startswith('http'):
            videopage = urllib_parse.urljoin(site.url, videopage)

        name = utils.cleantext(utils.safe_get_attr(link, 'title', default=utils.safe_get_text(link, default='')))
        img_tag = item.select_one('[data-original]')
        img = utils.safe_get_attr(img_tag, 'data-original', ['src'])
        if img:
            if img.startswith('//'):
                img = 'https:' + img
            elif not img.startswith('http'):
                img = urllib_parse.urljoin(site.url, img)

        duration = utils.safe_get_text(item.select_one('.duration'), default='')

        contextmenu = []
        contexturl = (utils.addon_sys
                      + "?mode=porntn.Lookupinfo"
                      + "&url=" + urllib_parse.quote_plus(videopage))
        contextmenu.append(('[COLOR deeppink]Lookup info[/COLOR]', 'RunPlugin(' + contexturl + ')'))

        site.add_download_link(name, videopage, 'Playvid', img, name, contextm=contextmenu, duration=duration)

    next_link = soup.select_one('.next[href]')
    if next_link:
        np = utils.safe_get_attr(next_link, 'href', default='')
        np_match = re.search(r'from(?:_videos)?=(\d+)', np)
        next_from = np_match.group(1) if np_match else ''
        nextp = url
        for p in ['from', 'from_videos']:
            nextp = nextp.replace('{}={}'.format(p, str(page)), '{}={}'.format(p, next_from))
        label = 'Next Page ({})'.format(next_from) if next_from else 'Next Page'
        site.add_dir(label, nextp, 'List', site.img_next, page=next_from)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    html = utils.getHtml(url, site.url)
    sources = {}
    license = re.compile(r"license_code:\s*'([^']+)", re.DOTALL | re.IGNORECASE).findall(html)[0]
    patterns = [r"video_url:\s*'([^']+)[^;]+?video_url_text:\s*'([^']+)",
                r"video_alt_url:\s*'([^']+)[^;]+?video_alt_url_text:\s*'([^']+)",
                r"video_alt_url2:\s*'([^']+)[^;]+?video_alt_url2_text:\s*'([^']+)",
                r"video_url:\s*'([^']+)',\s*postfix:\s*'\.mp4',\s*(preview)"]
    for pattern in patterns:
        items = re.compile(pattern, re.DOTALL | re.IGNORECASE).findall(html)
        for surl, qual in items:
            qual = '00' if qual == 'preview' else qual
            qual = qual.replace(' HD', '')
            surl = kvs_decode(surl, license)
            sources[qual] = surl
    videourl = utils.selector('Select quality', sources, setting_valid='qualityask', sort_by=lambda x: 1081 if x == '4k' else int(x[:-1]), reverse=True)

    if not videourl:
        vp.progress.close()
        return
    vp.play_from_direct_link(videourl + '|referer=' + url)


@site.register()
def Categories(url):
    try:
        cathtml = utils.getHtml(url, '')
    except Exception:
        return None
    soup = utils.parse_html(cathtml)
    if not soup:
        utils.eod()
        return

    for card in soup.select('a.item[href][title]'):
        catpage = utils.safe_get_attr(card, 'href', default='')
        name = utils.cleantext(utils.safe_get_attr(card, 'title', default=''))
        videos = utils.safe_get_text(card.select_one('.videos'), default='')
        if not catpage or not name:
            continue

        label = name + (' [COLOR hotpink]({})[/COLOR]'.format(videos) if videos else '')
        catpage = catpage + '?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=1'
        site.add_dir(label, catpage, 'List', '', page=1)
    utils.eod()


@site.register()
def Tags(url):
    try:
        taghtml = utils.getHtml(url, '')
    except Exception:
        return None
    soup = utils.parse_html(taghtml)
    if not soup:
        utils.eod()
        return

    for link in soup.select('a[href*="/tags/"]'):
        tagpage = utils.safe_get_attr(link, 'href', default='')
        name = utils.cleantext(utils.safe_get_text(link, default=''))
        if not tagpage or not name:
            continue
        if tagpage.startswith('/'):
            tagpage = site.url.rstrip('/') + tagpage
        tagpage = tagpage + '?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=1'
        site.add_dir(name, tagpage, 'List', '', page=1)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(searchUrl, 'Search')
    else:
        title = keyword.replace(' ', '-')
        searchUrl = searchUrl + title + '?mode=async&function=get_block&block_id=list_videos_videos_list_search_result&category_ids=&sort_by=&from_videos=1'
        List(searchUrl, 1)


@site.register()
def Lookupinfo(url):
    class porntnLookup(utils.LookupInfo):
        def url_constructor(self, url):
            if 'categories/' in url:
                return url + '?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=1'

    lookup_list = [
        ("Cat", r'<a href="(https://porntn\.com/categories/[^"]+)">([^<]+)<', ''),
    ]

    lookupinfo = porntnLookup(site.url, url, 'porntn.List', lookup_list)
    lookupinfo.getinfo()
