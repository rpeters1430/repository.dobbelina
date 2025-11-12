'''
    Cumination
    Copyright (C) 2021 Team Cumination

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

from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('peekvids', '[COLOR hotpink]PeekVids[/COLOR]', 'https://www.peekvids.com/', 'https://www.peekvids.com/img/logo.png', 'peekvids')


def _add_pagination(soup, mode):
    next_link = None
    for selector in ('.pagination a.next', '.pagination .next a', 'a[rel="next"]'):
        next_link = soup.select_one(selector)
        if next_link:
            break

    if not next_link:
        return

    next_url = utils.safe_get_attr(next_link, 'href')
    if not next_url:
        return

    next_url = urllib_parse.urljoin(site.url, next_url)
    label = ''
    if '=' in next_url:
        label = next_url.split('=')[-1]
    elif '/' in next_url.rstrip('/'):
        label = next_url.rstrip('/').split('/')[-1]

    site.add_dir('[COLOR hotpink]Next Page...[/COLOR] ({0})'.format(label), next_url, mode, site.img_next)


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'categories', 'Cat', site.img_cat)
    site.add_dir('[COLOR hotpink]Channels[/COLOR]', site.url + 'channels', 'Channels', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'videos?q=', 'Search', site.img_search)
    List(site.url + 'Trending-Porn')


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    cards = soup.select('.card.video, .card.not_show, article.card.video, article.card.not_show')
    if not cards:
        cards = soup.select('.card')

    for card in cards:
        link = card.select_one('a[href]')
        if not link:
            continue

        videopage = utils.safe_get_attr(link, 'href')
        if not videopage:
            continue
        videopage = urllib_parse.urljoin(site.url, videopage)

        name = utils.safe_get_attr(link, 'title') or utils.safe_get_text(link)
        name = utils.cleantext(name)
        if not name:
            continue

        img_tag = card.select_one('img')
        img = utils.safe_get_attr(img_tag, 'data-src', ['data-original', 'data-thumbnail', 'src'])
        if img and img.startswith('//'):
            img = 'https:' + img

        duration_tag = card.select_one('.info, .meta__duration, .duration, .card__duration, .video-duration, .time')
        duration = utils.safe_get_text(duration_tag)

        hd = ''
        quality_tag = card.select_one('.quality, .hd, .label-hd, .badge, .video-quality, .is_hd, .tag')
        if quality_tag:
            quality_text = utils.safe_get_text(quality_tag).upper()
            quality_classes = ' '.join(quality_tag.get('class', []))
            if 'HD' in quality_text or 'HD' in quality_classes.upper():
                hd = 'HD'

        site.add_download_link(name, videopage, 'Play', img, name, duration=duration, quality=hd)

    _add_pagination(soup, 'List')

    utils.eod()


@site.register()
def Cat(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    category_items = soup.select('.categories-list li, .categories li, ul.categories li')
    if not category_items:
        category_items = soup.select('ul li')
    for item in category_items:
        link = item.select_one('a[href]')
        count = item.select_one('span')
        if not link or not count:
            continue

        catpage = utils.safe_get_attr(link, 'href')
        if not catpage:
            continue
        catpage = urllib_parse.urljoin(site.url, catpage)

        name = utils.cleantext(utils.safe_get_attr(link, 'title') or utils.safe_get_text(link))
        if not name:
            continue

        vids_text = utils.safe_get_text(count)
        vids = ''.join(ch for ch in vids_text if ch.isdigit() or ch == ',')
        display_count = vids if vids else vids_text
        if not display_count:
            continue
        name = '{0} [COLOR hotpink]{1} Videos[/COLOR]'.format(name, display_count)

        site.add_dir(name, catpage, 'List', '')

    utils.eod()


@site.register()
def Channels(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    channels_container = soup.select_one('.popular_channels') or soup
    channel_cards = channels_container.select('.card')

    for card in channel_cards:
        link = card.select_one('a[href]')
        if not link:
            continue

        chpage = utils.safe_get_attr(link, 'href')
        if not chpage:
            continue
        chpage = urllib_parse.urljoin(site.url, chpage)

        name = utils.cleantext(utils.safe_get_attr(link, 'title') or utils.safe_get_text(link))
        if not name:
            continue

        vids_tag = card.select_one('.videos, .video-count, .channel-videos, [class*="videos"]')
        vids_text = utils.safe_get_text(vids_tag)
        vids = ''.join(ch for ch in vids_text if ch.isdigit() or ch == ',')
        if vids:
            name = '{0} [COLOR hotpink]{1} Videos[/COLOR]'.format(name, vids)

        img_tag = card.select_one('img')
        img = utils.safe_get_attr(img_tag, 'data-src', ['data-original', 'src'])
        if img and img.startswith('//'):
            img = 'https:' + img

        site.add_dir(name, chpage, 'List', img)

    _add_pagination(soup, 'Channels')

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url = "{0}{1}/".format(url, keyword.replace(' ', '+'))
        List(url)


@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    videopage = utils.getHtml(url, site.url)
    soup = utils.parse_html(videopage)
    sources = []
    for source in soup.select('source[src]'):
        src = utils.safe_get_attr(source, 'src')
        if src:
            sources.append(src)
    if sources:
        videourl = utils.prefquality(sources, reverse=True)
        if videourl:
            vp.play_from_direct_link(videourl.replace('&amp;', '&'))
