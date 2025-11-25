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
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('aagmaal', '[COLOR hotpink]Aag Maal[/COLOR]', 'https://aagmaal.gay/', 'aagmaal.png', 'aagmaal')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url, 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + '?s=', 'Search', site.img_search)
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    # Find all recent items
    items = soup.select('div.recent-item, article.recent-item')

    for item in items:
        link = item.select_one('a')
        if not link:
            continue

        videopage = utils.safe_get_attr(link, 'href')
        if not videopage:
            continue

        # Get name, removing any span tags
        name_text = utils.safe_get_text(link)
        # Remove span content if present
        for span in link.find_all('span'):
            span.decompose()
        name = utils.safe_get_text(link)
        if not name:
            name = name_text
        name = utils.cleantext(name)

        img_tag = item.select_one('img')
        img = utils.safe_get_attr(img_tag, 'src', ['data-src', 'data-original'])

        site.add_download_link(name, videopage, 'Playvid', img, name)

    # Pagination
    pagination = soup.select_one('div.pagination, nav.pagination')
    if pagination:
        current = pagination.select_one('span.current, a.current')
        if current:
            next_link = current.find_next_sibling('a')
            if next_link:
                next_url = utils.safe_get_attr(next_link, 'href')
                if next_url:
                    pages_tag = pagination.select_one('span.pages')
                    pgtxt = 'Currently in {0}'.format(utils.safe_get_text(pages_tag, ''))
                    site.add_dir('[COLOR hotpink]Next Page...[/COLOR] {0}'.format(pgtxt), next_url, 'List', site.img_next)

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
                    site.add_dir('[COLOR hotpink]Next Page...[/COLOR] {0}'.format(pgtxt), purl, 'List2', site.img_next)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videourl = ''

    videopage = utils.getHtml(url, site.url)
    links = re.compile(r'''href="([^"]+)"\s*class="external.+?blank">.*?(?://|\.)([^/]+)''', re.DOTALL | re.IGNORECASE).findall(videopage)
    if links:
        links = {host: link for link, host in links if vp.resolveurl.HostedMediaFile(link)}
        videourl = utils.selector('Select link', links)
    else:
        r = re.search(r'<iframe\s*loading="lazy"\s*src="([^"]+)', videopage)
        if r:
            videourl = r.group(1)

    if not videourl:
        utils.notify('Oh Oh', 'No Videos found')
        vp.progress.close()
        return

    vp.play_from_link_to_resolve(videourl)


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)

    # Find all category/tag links
    tag_links = soup.select('a.tag, a[class*="tag"]')

    for link in tag_links:
        catpage = utils.safe_get_attr(link, 'href')
        name = utils.safe_get_attr(link, 'aria-label', ['label', 'title'])

        if not catpage or not name:
            # Try getting name from text content
            if catpage and not name:
                name = utils.safe_get_text(link)
            if not catpage or not name:
                continue

        name = utils.cleantext(name)
        site.add_dir(name, catpage, 'List2')

    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        title = keyword.replace(' ', '+')
        searchUrl = searchUrl + title
        List2(searchUrl)
