"""
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
"""

import re
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('hentaihavenc', '[COLOR hotpink]Hentaihaven[/COLOR]', 'https://hentaihaven.co/', 'hh.png', 'hentaihavenco')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'genres/', 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Series[/COLOR]', site.url + 'series/', 'Series', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/?q=', 'Search', site.img_search)
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)
    for item in soup.select('a.a_item'):
        videopage = item['href']
        img = item.select_one('img')['data-src']
        name = item.select_one('.video_title').text
        name = utils.cleantext(name)
        site.add_download_link(name, site.url[:-1] + videopage, 'Playvid', site.url[:-1] + img, name)

    next_page_link = None
    for page_link in soup.select("a.page-link"):
        if page_link.text == 'Next':
            next_page_link = page_link
            break
            
    if next_page_link:
        page_num_match = re.search(r'page=(\d+)', next_page_link['href'])
        if page_num_match:
            page_num = page_num_match.group(1)
            site.add_dir('[COLOR hotpink]Next Page[/COLOR] ({0})'.format(page_num), site.url[:-1] + next_page_link['href'], 'List', site.img_next)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, site.url)
    soup = utils.parse_html(videopage)
    iframe = soup.select_one('iframe[src*="nhplayer.com"]')
    if iframe:
        surl = iframe['src']
        if 'nhplayer.com' in surl:
            videopage = utils.getHtml(surl, site.url)
            soup = utils.parse_html(videopage)
            data_id_li = soup.select_one('li[data-id]')
            if data_id_li:
                surl = data_id_li['data-id']
                if surl.startswith('/'):
                    surl = 'https://nhplayer.com' + surl
                videohtml = utils.getHtml(surl, site.url)
                match = re.search(r'file:\s*"([^"]+)"', videohtml)
                if match:
                    vp.play_from_direct_link(match.group(1))
                    vp.progress.close()
                    return
            else:
                vp.progress.close()
                utils.notify('Oh oh', 'Couldn\'t find a playable link')
        else:
            vp.play_from_link_to_resolve(surl)
    else:
        vp.progress.close()
        utils.notify('Oh oh', 'Couldn\'t find a playable link')
    return


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    for item in soup.select('a.cat_item'):
        catpage = item['href']
        style = item.select_one('.cat_bg')['style']
        image_match = re.search(r"url\(([^)]+)\)", style)
        image = image_match.group(1) if image_match else ''
        name = item.select_one('.cat_ttl').text
        desc = item.select_one('.cat_dsc').text
        count = item.select_one('.cat_count').text.strip()
        
        name = utils.cleantext(name)
        if count:
            name += " [COLOR orange][I]{0} videos[/I][/COLOR]".format(count)
        site.add_dir(name, site.url[:-1] + catpage, 'List', site.url[:-1] + image, desc=desc)
    utils.eod()


@site.register()
def Series(url, section=None):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    for item in soup.select('a.vc_item'):
        series_url = item['href']
        name = item.select_one('.vcat_title').text
        img = item.select_one('.vcat_poster img')['data-src']
        site.add_dir(name, site.url[:-1] + series_url, 'List', site.url[:-1] + img)
    
    next_page_link = None
    for page_link in soup.select("a.page-link"):
        if page_link.text == 'Next':
            next_page_link = page_link
            break
            
    if next_page_link:
        page_num_match = re.search(r'page=(\d+)', next_page_link['href'])
        if page_num_match:
            page_num = page_num_match.group(1)
            site.add_dir('[COLOR hotpink]Next Page[/COLOR] ({0})'.format(page_num), site.url[:-1] + next_page_link['href'], 'Series', site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        title = keyword.replace(' ', '+')
        searchUrl = searchUrl + title
        List(searchUrl)
