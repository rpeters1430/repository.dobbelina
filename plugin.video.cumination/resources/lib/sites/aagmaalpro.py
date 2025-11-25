'''
    Cumination Site Plugin
    Copyright (C) 2020 Team Cumination

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
import pickle
import binascii
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('aagmaalpro', '[COLOR hotpink]Aag Maal Pro[/COLOR]', 'https://aagmaal.delhi.in/', 'aagmaalpro.png', 'aagmaalpro')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'categories/', 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + '?s=', 'Search', site.img_search)
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    # Find all article items
    items = soup.select('article')

    for item in items:
        link = item.select_one('a')
        if not link:
            continue

        videopage = utils.safe_get_attr(link, 'href')
        if not videopage:
            continue

        img_tag = item.select_one('img')
        img = utils.safe_get_attr(img_tag, 'src', ['data-src', 'data-original'])

        # Duration
        duration_tag = item.select_one('span.duration, div.duration, time.duration')
        duration = utils.safe_get_text(duration_tag, '')
        # Remove icon if present
        if duration:
            duration = re.sub(r'<i.+?/i>', '', duration).strip()

        # Name from header span
        header = item.select_one('header, div.header, div[class*="header"]')
        if header:
            name_tag = header.select_one('span')
            if name_tag:
                name = utils.safe_get_text(name_tag)
            else:
                name = utils.safe_get_text(header)
        else:
            name = utils.safe_get_attr(link, 'title', ['aria-label'])

        if not name:
            continue

        name = utils.cleantext(name)
        site.add_download_link(name, videopage, 'Playvid', img, name, duration=duration)

    # Pagination
    pagination = soup.select_one('div.pagination, nav.pagination')
    if pagination:
        current = pagination.select_one('span.current, a.current')
        if current:
            # Look for Next link
            next_link = None
            for link in pagination.select('a'):
                if 'Next' in utils.safe_get_text(link):
                    next_link = link
                    break

            if next_link:
                np_url = utils.safe_get_attr(next_link, 'href')
                currpg = utils.safe_get_text(current)

                # Find Last link
                last_link = None
                for link in pagination.select('a'):
                    if 'Last' in utils.safe_get_text(link):
                        last_link = link
                        break

                if last_link:
                    last_url = utils.safe_get_attr(last_link, 'href')
                    if last_url:
                        lastpg = last_url.rstrip('/').split('/')[-1]
                        pgtxt = 'Currently in Page {0} of {1}'.format(currpg, lastpg)
                    else:
                        pgtxt = 'Currently in {0}'.format(currpg)
                else:
                    pgtxt = 'Currently in {0}'.format(currpg)

                site.add_dir('[COLOR hotpink]Next Page...[/COLOR] ({0})'.format(pgtxt), np_url, 'List', site.img_next)
            else:
                # Look for inactive next link
                inactive_link = current.find_next_sibling('a', class_='inactive')
                if inactive_link:
                    np_url = utils.safe_get_attr(inactive_link, 'href')
                    currpg = utils.safe_get_text(current)
                    pgtxt = 'Currently in {0}'.format(currpg)
                    site.add_dir('[COLOR hotpink]Next Page...[/COLOR] ({0})'.format(pgtxt), np_url, 'List', site.img_next)

    utils.eod()


@site.register()
def List2(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    # Find all article items
    items = soup.select('article')

    for item in items:
        title_div = item.select_one('div.title, h2.title, div[class*="title"]')
        if not title_div:
            continue

        link = title_div.select_one('a')
        if not link:
            continue

        iurl = utils.safe_get_attr(link, 'href')
        name = utils.safe_get_text(link)

        if not iurl or not name:
            continue

        img_tag = item.select_one('img')
        img = utils.safe_get_attr(img_tag, 'src', ['data-src', 'data-original'])

        name = utils.cleantext(name)
        site.add_download_link(name, iurl, 'Playvid', img, name)

    # Pagination
    pagination = soup.select_one('div.pagination, nav.pagination')
    if pagination:
        current = pagination.select_one('span.current, a.current')
        if current:
            next_link = current.find_next_sibling('a')
            if next_link:
                purl = utils.safe_get_attr(next_link, 'href')
                if purl:
                    pages_tag = pagination.select_one('span.pages')
                    pgtxt = 'Currently in {0}'.format(utils.safe_get_text(pages_tag, ''))
                    site.add_dir('[COLOR hotpink]Next Page...[/COLOR] ({0})'.format(pgtxt), purl, 'List2', site.img_next)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videourl = ''
    links = []

    if url.startswith('http'):
        videopage = utils.getHtml(url, site.url)
        vidsec = re.search(r'class="video-description">(.+?)<div id="video-author">', videopage, re.DOTALL)
        if vidsec:
            links = re.compile(r'''title="[^\d]+(\d+)"\s*href="(https?://([^.]+)[^"]+)''', re.DOTALL | re.IGNORECASE).findall(vidsec.group(1))
    else:
        links = pickle.loads(binascii.unhexlify(url))

    if links:
        links = {host + ' ' + no: link for no, link, host in links if vp.resolveurl.HostedMediaFile(link)}
        videourl = utils.selector('Select link', links)
    else:
        r = re.search(r'<iframe\s*loading="lazy"\s*src="([^"]+)', videopage)
        if r:
            videourl = r.group(1)
        else:
            r = re.search(r'<iframe.+?src="(http[^"]+)', videopage)
            if r:
                videourl = r.group(1)

    if not videourl:
        utils.notify('Oh Oh', 'No Videos found')
        vp.progress.close()
        return

    vp.play_from_link_to_resolve(videourl)


@site.register()
def Categories(url):
    categories = []

    while url:
        cathtml = utils.getHtml(url, site.url)
        soup = utils.parse_html(cathtml)

        # Find all article items
        items = soup.select('article')

        for item in items:
            link = item.select_one('a')
            if not link:
                continue

            catpage = utils.safe_get_attr(link, 'href')
            if not catpage:
                continue

            img_tag = item.select_one('img')
            img = utils.safe_get_attr(img_tag, 'src', ['data-src', 'data-original'])

            # Get title/name
            title_tag = item.select_one('div.title, h2.title, span.title, div[class*="title"]')
            if title_tag:
                name = utils.safe_get_text(title_tag)
            else:
                name = utils.safe_get_attr(link, 'title', ['aria-label'])

            if not name:
                continue

            categories.append((catpage, img, name))

        # Check for next page
        pagination = soup.select_one('div.pagination, nav.pagination')
        if pagination:
            current = pagination.select_one('span.current, a.current')
            if current:
                inactive_link = current.find_next_sibling('a', class_='inactive')
                if inactive_link:
                    url = utils.safe_get_attr(inactive_link, 'href')
                else:
                    url = False
            else:
                url = False
        else:
            url = False

    # Sort and display categories
    for catpage, img, name in sorted(categories, key=lambda item: item[2].lower()):
        name = utils.cleantext(name)
        site.add_dir(name, catpage, 'List', img)

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
