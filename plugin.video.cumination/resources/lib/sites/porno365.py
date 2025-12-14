'''
    Cumination
    Copyright (C) 2022 Team Cumination

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

import xbmc
import xbmcgui
from urllib.parse import urljoin

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite('porno365', "[COLOR hotpink]Porno365[/COLOR]", 'http://m.porno365.pics/', 'http://m.porno365.pics/settings/l8.png', 'porno365')
porn365_headers = utils.base_hdrs.copy()
porn365_headers.update({'User-Agent': 'Mozilla/5.0 (Android 7.0; Mobile; rv:54.0) Gecko/54.0 Firefox/54.0'})


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'categories', 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Pornstars[/COLOR]', site.url + 'models', 'Models', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/?q=', 'Search', site.img_search)
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url, headers=porn365_headers)
    if '404 :(</h1>' in html:
        utils.notify(msg='Nothing found')
        utils.eod()
        return

    soup = utils.parse_html(html)
    items = soup.select('li[id] .image') or soup.select('a.image')

    for link in items:
        videopage = urljoin(site.url, utils.safe_get_attr(link, 'href'))
        name = utils.cleantext(utils.safe_get_attr(link, 'alt') or utils.safe_get_text(link, default=''))
        img_tag = link.select_one('img')
        img = utils.safe_get_attr(img_tag, 'src', ['data-src', 'data-original'])
        duration = utils.safe_get_text(link.select_one('.duration'), default='')
        site.add_download_link(name, videopage, 'Playvid', img, name, duration=duration, contextm='porno365.Related')

    next_link = soup.select_one('a.next_link')
    if next_link:
        np_url = urljoin(site.url, utils.safe_get_attr(next_link, 'href'))
        np_num = utils.safe_get_text(next_link, default='').strip()
        site.add_dir('Next Page ({})'.format(np_num or ''), np_url, 'List', site.img_next, contextm='porno365.GotoPage')

    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, 'Enter Page number')
    if pg:
        url = url.replace('/{}'.format(np), '/{}'.format(pg))
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg='Out of range!')
            return
        contexturl = (utils.addon_sys + "?mode=" + str(list_mode) + "&url=" + urllib_parse.quote_plus(url))
        xbmc.executebuiltin('Container.Update(' + contexturl + ')')


@site.register()
def Related(url):
    contexturl = (utils.addon_sys + "?mode=" + str('porno365.List') + "&url=" + urllib_parse.quote_plus(url))
    xbmc.executebuiltin('Container.Update(' + contexturl + ')')


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url = "{0}{1}=".format(url, keyword.replace(' ', '%20'))
        List(url)


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, headers=porn365_headers)
    soup = utils.parse_html(cathtml)
    for card in soup.select('.categories-list-div a[href]'):
        caturl = utils.fix_url(utils.safe_get_attr(card, 'href'), site.url)
        img_tag = card.select_one('img')
        img = utils.fix_url(utils.safe_get_attr(img_tag, 'src', ['data-src', 'data-original']), site.url)
        name = utils.cleantext(utils.safe_get_attr(img_tag, 'alt') or utils.safe_get_text(card, default=''))
        count = utils.safe_get_text(card.select_one('.text'), default='').strip()
        if count:
            name = name + '[COLOR hotpink] ({} videos)[/COLOR]'.format(count)
        site.add_dir(name, caturl, 'List', img)
    utils.eod()


@site.register()
def Models(url):
    cathtml = utils.getHtml(url, headers=porn365_headers)
    soup = utils.parse_html(cathtml)
    for card in soup.select('.item_model'):
        caturl = utils.safe_get_attr(card.select_one('a[href]'), 'href')
        img = utils.safe_get_attr(card.select_one('img'), 'src', ['data-src', 'data-original'])
        count = utils.safe_get_text(card.select_one('.cnt_span'), default='').strip()
        name = utils.cleantext(utils.safe_get_text(card.select_one('.model_eng_name'), default=''))
        if count:
            name = name + '[COLOR hotpink] ({} videos)[/COLOR]'.format(count)
        site.add_dir(name, caturl, 'List', img)
    next_link = soup.select_one('a.next_link')
    if next_link:
        np_url = urljoin(site.url, utils.safe_get_attr(next_link, 'href'))
        np_num = utils.safe_get_text(next_link, default='').strip()
        site.add_dir('Next Page ({})'.format(np_num or ''), np_url, 'Models', site.img_next, contextm='porno365.GotoPage')
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download, direct_regex='meta property="og:video" content="([^"]+)">')
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videohtml = utils.getHtml(url, site.url, headers=porn365_headers)
    vp.play_from_html(videohtml)
