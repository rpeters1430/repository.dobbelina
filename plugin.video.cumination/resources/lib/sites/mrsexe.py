"""
    Cumination
    Copyright (C) 2015 Whitecream
    Copyright (C) 2015 Fr40m1nd

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
from urllib.parse import urljoin

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('mrsexe', '[COLOR hotpink]Mr Sexe[/COLOR]', 'https://www.mrsexe.com/', 'mrsexe.png', 'mrsexe')

progress = utils.progress


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Classiques[/COLOR]', site.url + 'classiques/', 'List', '', '')
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + '?search=', 'Search', site.img_search)
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url, 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Stars[/COLOR]', site.url + 'filles/', 'Stars', '', '')
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, '')
    soup = utils.parse_html(listhtml)

    container = soup.select_one('ul.thumb-list') or soup.find('ul', class_=lambda c: c and 'thumb-list' in c)
    if not container:
        utils.eod()
        return

    for item in container.select('li'):
        link = item.select_one('a[href]')
        if not link:
            continue
        videopage = urljoin(site.url, utils.safe_get_attr(link, 'href'))
        img_tag = item.select_one('img')
        img = utils.safe_get_attr(img_tag, 'src', ['data-src', 'data-original', 'data-lazy'])
        if img and img.startswith('//'):
            img = 'https:' + img
        duration = utils.safe_get_text(item.select_one('.duration, .thumb-duration, .time'), default='')
        name = utils.cleantext(utils.safe_get_attr(link, 'title') or utils.safe_get_text(link, default=''))
        quality = 'hd' if 'hd' in (item.get('class') or []) else ''
        site.add_download_link(name, videopage, 'Playvid', img, name, duration=duration, quality=quality)

    next_link = soup.select_one('li.arrow a') or soup.select_one('a.next')
    if next_link:
        site.add_dir('Next Page', urljoin(site.url, utils.safe_get_attr(next_link, 'href')), 'List', site.img_next)

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


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, '')
    soup = utils.parse_html(cathtml)
    for opt in soup.select('option[value^="/cat"]'):
        catpage = urljoin(site.url, utils.safe_get_attr(opt, 'value'))
        name = utils.safe_get_text(opt, default='')
        site.add_dir(name, catpage, 'List', '')
    utils.eod()


@site.register()
def Stars(url):
    starhtml = utils.getHtml(url, '')
    soup = utils.parse_html(starhtml)
    container = soup.select_one('ul.thumb-list') or soup.find('ul', class_=lambda c: c and 'thumb-list' in c)
    if container:
        for item in container.select('li'):
            img_tag = item.select_one('img')
            img = utils.safe_get_attr(img_tag, 'src', ['data-src', 'data-original', 'data-lazy'])
            if img and img.startswith('//'):
                img = 'https:' + img
            link = item.select_one('a[href]')
            if not link:
                continue
            starpage = urljoin(site.url, utils.safe_get_attr(link, 'href'))
            name = utils.cleantext(utils.safe_get_attr(link, 'title') or utils.safe_get_text(link, default=''))
            vidcount = utils.safe_get_text(item.select_one('.vids, .videos, .count'), default='').strip()
            if vidcount:
                name = "{0}[COLOR orange] [COLOR deeppink][I]({1})[/I][/COLOR]".format(name, vidcount)
            site.add_dir(name, starpage, 'Stars', img)
    nextp = soup.select_one('li.arrow a[href*="suiv"]')
    if nextp:
        site.add_dir('Next Page', urljoin(site.url, utils.safe_get_attr(nextp, 'href')), 'Stars', site.img_next)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)
    clic_src = None
    clic_tag = soup.select_one('[src*="/inc/clic.php"]')
    if clic_tag:
        clic_src = utils.safe_get_attr(clic_tag, 'src')
    if not clic_src:
        return

    click_url = urljoin(site.url, clic_src)
    click_html = utils.getHtml(click_url, site.url)
    click_soup = utils.parse_html(click_html)
    sources = [utils.safe_get_attr(tag, 'src') for tag in click_soup.find_all(['source', 'a', 'video'], src=True)]
    sources = [src for src in sources if src and '.mp4' in src]
    if not sources:
        sources = re.findall(r"https?://[^'\"]+\.mp4[^'\"]*", click_html, re.IGNORECASE)
    if sources:
        utils.playvid(sources[-1], name, download)
