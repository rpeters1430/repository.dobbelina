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
import xbmc
import xbmcgui
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('taboofantazy', '[COLOR hotpink]TabooFantazy[/COLOR]', 'https://www.taboofantazy.com/', 'taboofantazy.png', 'taboofantazy')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'categories/', 'Cat', site.img_cat)
    site.add_dir('[COLOR hotpink]Tags[/COLOR]', site.url + 'tags/', 'Tags', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + '?s=', 'Search', site.img_search)
    List(site.url + '?filter=latest')


@site.register()
def List(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    if not soup:
        utils.eod()
        return

    # Find all video articles
    articles = soup.find_all('article', attrs={'video-uid': True})

    for article in articles:
        link = article.find('a', href=True, title=True)
        if not link:
            continue

        videourl = utils.safe_get_attr(link, 'href')
        name = utils.safe_get_attr(link, 'title')

        if not videourl or not name:
            continue

        name = utils.cleantext(name)

        # Get thumbnail
        img_tag = link.find('img')
        img = utils.safe_get_attr(img_tag, 'data-src', fallback_attrs=['src'])

        # Check for HD badge
        hd_badge = article.find('span', class_='hd-badge')
        hd = 'HD' if hd_badge and 'HD' in utils.safe_get_text(hd_badge, default='') else ''

        # Create context menu
        contextmenu = []
        contexturl = (utils.addon_sys
                      + "?mode=" + str('taboofantazy.Lookupinfo')
                      + "&url=" + urllib_parse.quote_plus(videourl))
        contextmenu.append(('[COLOR deeppink]Lookup info[/COLOR]', 'RunPlugin(' + contexturl + ')'))

        site.add_download_link(name, videourl, 'Play', img, name, contextm=contextmenu, quality=hd)

    # Handle pagination
    pagination = soup.find('div', class_='pagination')
    if pagination:
        next_link = pagination.find('a', string=re.compile('Next', re.IGNORECASE))
        if next_link:
            next_url = utils.safe_get_attr(next_link, 'href')
            if next_url:
                # Extract page number
                page_match = re.search(r'/page/(\d+)', next_url)
                page_num = page_match.group(1) if page_match else ''

                # Find last page
                last_link = pagination.find('a', string=re.compile('Last', re.IGNORECASE))
                last_page = ''
                if last_link:
                    last_url = utils.safe_get_attr(last_link, 'href')
                    last_match = re.search(r'/page/(\d+)', last_url)
                    last_page = last_match.group(1) if last_match else ''

                # Add next page with goto context menu
                contextmenu = []
                if page_num and last_page:
                    contexturl = (utils.addon_sys
                                  + "?mode=taboofantazy.GotoPage"
                                  + "&list_mode=taboofantazy.List"
                                  + "&url=" + urllib_parse.quote_plus(url)
                                  + "&np=" + page_num
                                  + "&lp=" + last_page)
                    contextmenu.append(('[COLOR violet]Goto Page[/COLOR]', 'RunPlugin(' + contexturl + ')'))

                site.add_dir('[COLOR hotpink]Next Page[/COLOR]', next_url, 'List', site.img_next, contextm=contextmenu)

    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, 'Enter Page number')
    if pg:
        url = url.replace('/page/{}'.format(np), '/page/{}'.format(pg))
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg='Out of range!')
            return
        contexturl = (utils.addon_sys + "?mode=" + str(list_mode) + "&url=" + urllib_parse.quote_plus(url))
        xbmc.executebuiltin('Container.Update(' + contexturl + ')')


@site.register()
def Cat(url):
    cathtml = utils.getHtml(url)
    soup = utils.parse_html(cathtml)

    if not soup:
        utils.eod()
        return

    # Find all category articles
    articles = soup.find_all('article', id=re.compile(r'post'))

    for article in articles:
        link = article.find('a', href=True, title=True)
        if not link:
            continue

        caturl = utils.safe_get_attr(link, 'href')
        name = utils.safe_get_attr(link, 'title')

        if not caturl or not name:
            continue

        name = utils.cleantext(name)

        # Get thumbnail
        img_tag = link.find('img', class_=True)
        img = utils.safe_get_attr(img_tag, 'src', fallback_attrs=['data-src'])

        site.add_dir(name, caturl, 'List', img)

    # Handle pagination for categories
    current_page = soup.find('span', class_='current')
    if current_page:
        # Find next page link after current
        next_sibling = current_page.find_next_sibling('a', href=True)
        if next_sibling:
            next_url = utils.safe_get_attr(next_sibling, 'href')
            if next_url and '/categories/' in next_url:
                site.add_dir('[COLOR hotpink]Next Page[/COLOR]', next_url, 'Cat', site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url = "{0}{1}".format(url, keyword.replace(' ', '%20'))
        List(url)


@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download=download, regex=r'itemprop="embedURL"\s*content="([^"]+)"')
    vp.play_from_site_link(url)


@site.register()
def Tags(url):
    listhtml = utils.getHtml(url, url)
    soup = utils.parse_html(listhtml)

    if not soup:
        utils.eod()
        return

    # Find all tag links
    tag_links = soup.find_all('a', href=re.compile(r'/tag/'))

    for link in tag_links:
        tagpage = utils.safe_get_attr(link, 'href')
        aria_label = utils.safe_get_attr(link, 'aria-label')

        if not tagpage or not aria_label:
            continue

        name = utils.cleantext(aria_label)

        # Build full URL if needed
        if not tagpage.startswith('http'):
            tagpage = site.url + tagpage.lstrip('/')

        site.add_dir(name, tagpage, 'List', '')

    utils.eod()


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Cat", r'(category/[^"]+)"\s*class="label"\s*title="([^"]+)"', ''),
        ("Tag", r'(tag/[^"]+)"\s*class="label"\s*title="([^"]+)"', ''),
        ("Actor", r'(actor[^"]+)"\s*title="([^"]+)"', '')
    ]

    lookupinfo = utils.LookupInfo(site.url, url, 'taboofantazy.List', lookup_list)
    lookupinfo.getinfo()
