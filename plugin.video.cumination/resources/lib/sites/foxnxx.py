'''
    Cumination
    Copyright (C) 2024 Team Cumination

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
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite('foxnxx', "[COLOR hotpink]Foxnxx[/COLOR]", 'https://foxnxx.com/', 'foxnxx.png', 'foxnxx')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/', 'Search', site.img_search)
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if "Can't Found '" in html:
        utils.notify(msg='Nothing found')
        utils.eod()
        return

    soup = utils.parse_html(html)

    # Context menu
    cm = []
    cm_lookupinfo = (utils.addon_sys + "?mode=" + str('foxnxx.Lookupinfo') + "&url=")
    cm.append(('[COLOR deeppink]Lookup info[/COLOR]', 'RunPlugin(' + cm_lookupinfo + ')'))
    cm_related = (utils.addon_sys + "?mode=" + str('foxnxx.Related') + "&url=")
    cm.append(('[COLOR deeppink]Related videos[/COLOR]', 'RunPlugin(' + cm_related + ')'))

    # Parse video items
    items = soup.select('.thumb')
    for item in items:
        link = item.select_one('a')
        if not link:
            continue

        videopage = utils.safe_get_attr(link, 'href')
        if not videopage:
            continue

        img_tag = item.select_one('img')
        img = utils.safe_get_attr(img_tag, 'data-src', ['src'])

        # Get name from link title or img alt
        name = utils.safe_get_attr(link, 'title')
        if not name:
            name = utils.safe_get_text(link, '').strip()

        timer_tag = item.select_one('.timer')
        duration = utils.safe_get_text(timer_tag, '')

        if name:
            site.add_download_link(name, videopage, 'Playvid', img, name, duration=duration, contextm=cm)

    # Pagination - find active page and next page
    active_page = soup.find('li', class_='active')
    if active_page:
        next_li = active_page.find_next_sibling('li')
        if next_li:
            next_link = next_li.select_one('a')
            if next_link:
                next_url = utils.safe_get_attr(next_link, 'href')
                next_page_num = utils.safe_get_text(next_link, '')

                # Get last page number
                last_page_num = ''
                pagination_ul = active_page.find_parent('ul')
                if pagination_ul:
                    last_li = pagination_ul.find_all('li')[-1]
                    if last_li:
                        last_link = last_li.select_one('a')
                        if last_link:
                            last_page_num = utils.safe_get_text(last_link, '')

                if next_url:
                    cm_gotopage = []
                    if last_page_num:
                        cm_gotopage_url = (utils.addon_sys + "?mode=foxnxx.GotoPage&list_mode=foxnxx.List&url=" +
                                          urllib_parse.quote_plus(next_url) + "&np=" + next_page_num + "&lp=" + last_page_num)
                        cm_gotopage.append(('[COLOR violet]Goto Page[/COLOR]', 'RunPlugin(' + cm_gotopage_url + ')'))
                    site.add_dir('Next Page ({})'.format(next_page_num), next_url, 'List', site.img_next, contextm=cm_gotopage)

    utils.eod()


@site.register()
def GotoPage(list_mode, url, np, lp):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, 'Enter Page number')
    if pg:
        url = url.replace('{}.html'.format(np), '{}.html'.format(pg))
        if int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg='Out of range!')
            return
        contexturl = (utils.addon_sys + "?mode=" + str(list_mode) + "&url=" + urllib_parse.quote_plus(url))
        xbmc.executebuiltin('Container.Update(' + contexturl + ')')


@site.register()
def Related(url):
    contexturl = (utils.addon_sys + "?mode=" + str('foxnxx.List') + "&url=" + urllib_parse.quote_plus(url))
    xbmc.executebuiltin('Container.Update(' + contexturl + ')')


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url = "{0}{1}.html".format(url, keyword.replace(' ', '-'))
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videohtml = utils.getHtml(url)
    match = re.compile(r'class="embed-responsive-item"\s*src="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(videohtml)
    if match:
        embedurl = match[0]
        embedurl = 'https:' + embedurl if embedurl.startswith('//') else embedurl
        embedhtml = utils.getHtml(embedurl, url)
        vp.play_from_html(embedhtml)
        # match = re.compile(r'<a id="overlay-link" href="([^"#]+)', re.DOTALL | re.IGNORECASE).findall(embedhtml)
        # if match:
        #     hqurl = match[0]
        #     hqurl = 'https:' + hqurl if hqurl.startswith('//') else hqurl
        #     videohtml = utils.getHtml(hqurl, embedurl)
        #     match = re.compile(r'<iframe src="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(videohtml)
        #     if match:
        #         videourl = match[0]
        #         videourl = 'https:' + videourl if videourl.startswith('//') else videourl
        #         vp.play_from_link_to_resolve(videourl)
        # else:
        #     params = embedurl.split('/')
        #     quality = params[-1]
        #     utils.kodilog('Video quality: {}'.format(quality))
        #     qualities = []
        #     if 1 & int(quality):
        #         qualities.append('360')
        #     if 2 & int(quality):
        #         qualities.append('480')
        #     if 4 & int(quality):
        #         qualities.append('720')
        #     if 8 & int(quality):
        #         qualities.append('1080')

        #     id = params[-2][::-1]
        #     base = params[-4]
        #     sources = {q: 'https://{0}/vid/{1}/{2}'.format(base, id, q) for q in qualities}
        #     videolink = utils.prefquality(sources, sort_by=lambda x: int(x), reverse=True)
        #     if videolink:
        #         vp.play_from_direct_link(videolink + '|Referer={0}'.format(embedurl))


@site.register()
def Lookupinfo(url):
    # Fetch page and parse with BeautifulSoup
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)

    # Find all tags
    tag_links = soup.select('.tagsstyle a[href*="/tags/"]')

    tags_info = []
    for link in tag_links:
        tag_url = utils.safe_get_attr(link, 'href')
        tag_name = utils.safe_get_text(link, '')
        if tag_url and tag_name:
            if not tag_url.startswith('http'):
                tag_url = site.url + tag_url.lstrip('/')
            tags_info.append(('Tag', tag_url, tag_name))

    # Use the LookupInfo utility to display the tags
    if tags_info:
        # Create lookup_list in the format expected by LookupInfo
        # For BeautifulSoup-based parsing, we can pass pre-parsed data
        lookup_list = [("Tag", r'class="tagsstyle"><a href="(/tags/[^"]+)">([^<]+)</a>', '')]
        lookupinfo = utils.LookupInfo(site.url, url, 'foxnxx.List', lookup_list)
        lookupinfo.getinfo()
