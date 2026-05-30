"""
    Cumination site scraper
    Copyright (C) 2026 Team Cumination

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
import xbmc
import xbmcgui
from resources.lib import utils
from resources.lib.adultsite import AdultSite


site = AdultSite('pornditt', '[COLOR hotpink]Pornditt[/COLOR]', 'https://v.pornditt.com/', 'pornditt.png', 'pornditt', category="Video Tubes")


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/{0}/', 'Search', site.img_search)
    List(site.url + 'latest-updates/')
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)

    if 'There is no data in this list.' in listhtml.split('class="thumbs albums-thumbs')[0]:
        utils.notify(msg='No videos found!')
        return

    soup = utils.parse_html(listhtml)

    cm = []
    cm_lookupinfo = utils.addon_sys + "?mode=pornditt.Lookupinfo&url="
    cm.append(('[COLOR deeppink]Lookup info[/COLOR]', 'RunPlugin({})'.format(cm_lookupinfo)))
    cm_related = utils.addon_sys + "?mode=pornditt.Related&url="
    cm.append(('[COLOR deeppink]Related videos[/COLOR]', 'RunPlugin({})'.format(cm_related)))

    selectors = {
        'items': 'div.item',
        'url': {'selector': 'a[href]', 'attr': 'href'},
        'title': {'selector': 'a[title]', 'attr': 'title'},
        'thumbnail': {'selector': 'img', 'attr': 'data-original'},
        'duration': {'selector': '.duration', 'text': True},
        'quality': {'selector': '.is-hd', 'text': True},
    }
    utils.soup_videos_list(site, soup, selectors, play_mode='Playvid', contextm=cm)

    next_link = soup.select_one('.next a[href], a.next[href]')
    if next_link:
        next_url = utils.safe_get_attr(next_link, 'href')
        if next_url:
            next_url = urllib_parse.urljoin(site.url, next_url)
            site.add_dir('Next Page', next_url, 'List', site.img_next)

    utils.eod()


@site.register()
def GotoPage(url, np, lp=None):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, 'Enter Page number')
    if pg:
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg='Out of range!')
            return
        url = re.sub(r'/0*{}/'.format(np), r'/{}/'.format(pg), url, flags=re.IGNORECASE)
        contexturl = (utils.addon_sys + "?mode=" + "pornditt.List&url=" + urllib_parse.quote_plus(url))
        xbmc.executebuiltin('Container.Update(' + contexturl + ')')


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    vpage = utils.getHtml(url, site.url)
    if "kt_player('kt_player'" in vpage:
        vp.progress.update(60, "[CR]{0}[CR]".format("kt_player detected"))
        vp.play_from_kt_player(vpage, url)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        List(url.format(keyword.replace(' ', '-')))


@site.register()
def Related(url):
    contexturl = (utils.addon_sys + "?mode=" + str('pornditt.List') + "&url=" + urllib_parse.quote_plus(url))
    xbmc.executebuiltin('Container.Update(' + contexturl + ')')


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Actor", r'class="btn gold" href="{}(models/[^"]+)">.+?</svg></i>([^<]+)<'.format(site.url), ''),
        ("Tag", r'<a href="{}(tags/[^"]+)">([^<]+)</a>'.format(site.url), '')]
    lookupinfo = utils.LookupInfo(site.url, url, 'pornditt.List', lookup_list)
    lookupinfo.getinfo()
