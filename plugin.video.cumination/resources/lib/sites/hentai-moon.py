"""
    Cumination
    Copyright (C) 2023 Team Cumin

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
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.decrypters.kvsplayer import kvs_decode

site = AdultSite("hentai-moon", "[COLOR hotpink]Hentai Moon[/COLOR]", 'https://hentai-moon.com/', "hentai-moon.png", "hentai-moon")

ajaxlist = '?mode=async&function=get_block&block_id=list_videos_latest_videos_list&sort_by=post_date&from=1'
ajaxcommon = '?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=1'
ajaxtop = '?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=rating&from=1'
ajaxmost = '?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=video_viewed&from=1'


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'categories/?mode=async&function=get_block&block_id=list_categories_categories_list&sort_by=title', 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Series[/COLOR]', site.url + 'series/?mode=async&function=get_block&block_id=list_dvds_channels_list&sort_by=title&from=1', 'Series', site.img_cat)
    site.add_dir('[COLOR hotpink]Tags[/COLOR]', site.url + 'tags/', 'Tags', site.img_cat)
    site.add_dir('[COLOR hotpink]Top Rated[/COLOR]', site.url + 'top-rated/' + ajaxtop, 'List', site.img_cat)
    site.add_dir('[COLOR hotpink]Most Viewed[/COLOR]', site.url + 'most-popular/' + ajaxmost, 'List', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/', 'Search', site.img_search)
    List(site.url + 'latest-updates/' + ajaxlist)


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return
    thumbnails = utils.Thumbnails(site.name)

    for card in _iter_video_cards(soup):
        link = card.select_one('a[href]')
        if not link:
            continue

        videopage = urllib_parse.urljoin(site.url, utils.safe_get_attr(link, 'href', default=''))
        name = utils.cleantext(utils.safe_get_attr(link, 'title', default='') or utils.safe_get_text(link, default=''))
        if not name or not videopage:
            continue

        img = thumbnails.fix_img(
            utils.safe_get_attr(link.select_one('img'), 'data-original', fallback_attrs=['src'], default='')
        )
        duration = utils.safe_get_text(link.select_one('.duration'), default='')
        hd = ' [COLOR orange]HD[/COLOR]' if link.select_one('.is_hd') else ''
        contextmenu = _lookup_context_menu(videopage)
        site.add_download_link(name, videopage, 'Playvid', img, name, contextm=contextmenu, duration=duration, quality=hd)

    _add_next_page(soup, url, 'List')
    utils.eod()


@site.register()
def Categories(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return
    for link in soup.select('a.item[href][title], div.item a[href][title]'):
        catpage = urllib_parse.urljoin(site.url, utils.safe_get_attr(link, 'href', default=''))
        name = utils.cleantext(utils.safe_get_attr(link, 'title', default=''))
        if not catpage or not name:
            continue

        videos = utils.safe_get_text(link.select_one('.videos'), default='').strip()
        label = name if not videos else "{0} [COLOR deeppink]{1}[/COLOR]".format(name, videos)
        catpage = "{0}{1}".format(catpage, ajaxcommon)
        image = utils.safe_get_attr(link.select_one('img'), 'src', default='')
        site.add_dir(label, catpage, 'List', image, name)
    utils.eod()


@site.register()
def Tags(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return
    for link in soup.select('a[href*="tags/"]'):
        tagpage = utils.safe_get_attr(link, 'href', default='')
        name = utils.cleantext(utils.safe_get_text(link, default=''))
        if not tagpage or not name:
            continue
        tagpage = "{0}{1}".format(urllib_parse.urljoin(site.url, tagpage), ajaxcommon)
        site.add_dir(name, tagpage, 'List', '')
    utils.eod()


@site.register()
def Series(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return
    for link in soup.select('a.item[href][title], div.item a[href][title]'):
        seriepage = urllib_parse.urljoin(site.url, utils.safe_get_attr(link, 'href', default=''))
        name = utils.cleantext(utils.safe_get_attr(link, 'title', default=''))
        if not seriepage or not name:
            continue

        videos = utils.safe_get_text(link.select_one('.videos'), default='').strip()
        label = name if not videos else "{0} [COLOR deeppink]{1}[/COLOR]".format(name, videos)
        seriepage = "{0}{1}".format(seriepage, ajaxcommon)
        img = utils.safe_get_attr(link.select_one('img'), 'data-original', fallback_attrs=['src'], default='')
        site.add_dir(label, seriepage, 'List', img, name)

    _add_next_page(soup, url, 'Series')
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        title = keyword.replace(' ', '-')
        searchq = keyword.replace(' ', '+')
        url = "{0}{1}/?mode=async&function=get_block&block_id=list_videos_videos_list_search_result&q={2}&cat_ids=&sort_by=&from_videos=1".format(url, title, searchq)
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    vpage = utils.getHtml(url, site.url)

    videourl = None
    sources = {}
    license = re.compile(r"license_code:\s*'([^']+)", re.DOTALL | re.IGNORECASE).findall(vpage)[0]
    patterns = [r"video_url:\s*'([^']+)[^;]+?video_url_text:\s*'([^']+)",
                r"video_alt_url\d*?:\s*'([^']+)[^;]+?video_alt_url\d*?_text:\s*'([^']+)",
                r"video_url:\s*'([^']+)',\s*postfix:\s*'\.mp4',\s*(preview)"]
    for pattern in patterns:
        items = re.compile(pattern, re.DOTALL | re.IGNORECASE).findall(vpage)
        for surl, qual in items:
            qual = '00' if qual == 'preview' else qual
            surl = kvs_decode(surl, license)
            sources.update({qual: surl})

    if len(sources) > 0:
        videourl = utils.selector('Select quality', sources, setting_valid='qualityask', sort_by=lambda x: 1081 if x == '4k' else int(x[:-1]), reverse=True)
        if not videourl:
            vp.progress.close()
            return
    else:
        match = re.search(r'Download:\s*?<a href="([^"]+)"', vpage, re.IGNORECASE | re.DOTALL)
        if match:
            videourl = match.group(1)

    if videourl:
        vp.play_from_direct_link(videourl)
    else:
        vp.progress.close()
        utils.notify('Oh Oh', 'No Videos found')


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Cat", '/(categories/[^"]+)">([^<]+)<', ''),
        ("Tag", '/(tags[^"]+)">([^<]+)<', ''),
        ("Serie", '/(series/[^"]+)">([^<]+)<', '')
    ]

    lookupinfo = utils.LookupInfo(site.url, url, 'hentai-moon.List', lookup_list)
    lookupinfo.getinfo()


def _iter_video_cards(soup):
    if not soup:
        return
    selectors = ['div.item', 'div.item-thumb', 'div.video-item']
    for selector in selectors:
        for card in soup.select(selector):
            yield card


def _lookup_context_menu(video_url):
    contexturl = (
        utils.addon_sys
        + "?mode=" + str('hentai-moon.Lookupinfo')
        + "&url=" + urllib_parse.quote_plus(video_url)
    )
    return ('[COLOR deeppink]Lookup info[/COLOR]', 'RunPlugin({0})'.format(contexturl))


def _add_next_page(soup, current_url, mode):
    if not soup:
        return
    next_link = soup.find(lambda tag: tag.name == 'a' and tag.string and 'next' in tag.string.lower())
    next_url = ''
    if next_link:
        next_url = utils.safe_get_attr(next_link, 'href', default='')
        if not next_url:
            params = utils.safe_get_attr(next_link, 'data-parameters', default='')
            match = re.search(r'(from(?:_videos)?)=(\d+)', params)
            if match:
                query = urllib_parse.parse_qs(urllib_parse.urlparse(current_url).query)
                query[match.group(1)] = [match.group(2)]
                base = current_url.split('?')[0]
                next_url = "{0}?{1}".format(base, urllib_parse.urlencode(query, doseq=True))
    if next_url:
        next_url = urllib_parse.urljoin(site.url, next_url)
        next_page = _extract_page_number(next_url)
        label = "Next Page ({0})".format(next_page) if next_page else 'Next Page'
        site.add_dir(label, next_url, mode, site.img_next)


def _extract_page_number(url):
    query = urllib_parse.urlparse(url).query
    params = urllib_parse.parse_qs(query)
    for key in ('from', 'from_videos'):
        if key in params and params[key]:
            return params[key][0]
    match = re.search(r'(\d+)(?!.*\d)', url)
    return match.group(1) if match else ''
