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

import re
from resources.lib import utils, jsunpack
from resources.lib.adultsite import AdultSite

site = AdultSite('missav', '[COLOR hotpink]Miss AV[/COLOR]', 'https://missav.ws/', 'missav.png', 'missav')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Actress List[/COLOR]', site.url + 'en/actresses', 'Models', site.img_cat)
    site.add_dir('[COLOR hotpink]Amateur[/COLOR]', 'Amateur', 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Uncensored[/COLOR]', 'Uncensored', 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Chinese AV[/COLOR]', 'Madou', 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'en/search/', 'Search', site.img_search)
    List(site.url + 'en/new?page=1')
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    soup = utils.parse_html(html)

    # Find all video items with @mouseenter attribute
    items = soup.select('div[\\@mouseenter], div[x-on\\:mouseenter]')
    for item in items:
        try:
            # Get image
            img_tag = item.select_one('img[data-src]')
            if not img_tag:
                continue
            img = utils.safe_get_attr(img_tag, 'data-src', ['src'])

            # Get info from img alt
            info = utils.safe_get_attr(img_tag, 'alt', default='')
            info = utils.cleantext(info)

            # Get video link
            link = item.select_one('a[href][alt]')
            if not link:
                continue
            videopage = utils.safe_get_attr(link, 'href')
            if not videopage:
                continue

            # Get name from link alt
            name = utils.safe_get_attr(link, 'alt', default='')
            if not name:
                name = utils.safe_get_text(link, '').strip()

            # Get duration from span
            duration_tag = item.select_one('span')
            duration = ''
            if duration_tag:
                duration_text = utils.safe_get_text(duration_tag, '').strip()
                # Extract time format (e.g., "01:23:45")
                duration = utils.cleantext(duration_text) if ':' in duration_text else ''

            site.add_download_link(name, videopage, 'Playvid', img, info, duration=duration, noDownload=True, fanart=img)
        except Exception as e:
            utils.log('missav List: Error processing video - {}'.format(e))
            continue

    # Pagination - find "next" link and last page number
    next_link = soup.select_one('a[rel="next"][href]')
    if next_link:
        npurl = utils.safe_get_attr(next_link, 'href')
        # Extract current page from next URL
        np_match = re.search(r'page=(\d+)', npurl) if npurl else None
        np = np_match.group(1) if np_match else ''

        # Find last page number - look for page links before "next"
        page_links = soup.select('a[aria-label*="Go to page"]')
        lp = ''
        for page_link in page_links:
            page_text = utils.safe_get_text(page_link, '').strip()
            if page_text.isdigit():
                lp = page_text

        if npurl:
            site.add_dir('[COLOR hotpink]Next Page...[/COLOR] {0}/{1}'.format(np, lp) if lp else 'Next Page ({0})'.format(np),
                        npurl, 'List', site.img_next)

    utils.eod()


@site.register()
def Models(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)

    # Find all list items with model info
    list_items = soup.select('li')
    for item in list_items:
        try:
            # Get image
            img_tag = item.select_one('img[src]')
            if not img_tag:
                continue
            img = utils.safe_get_attr(img_tag, 'src', ['data-src'])

            # Get model link
            link = item.select_one('a[href]')
            if not link:
                continue
            caturl = utils.safe_get_attr(link, 'href')
            if not caturl:
                continue

            # Get model name from truncate element
            name_tag = item.select_one('.truncate')
            if not name_tag:
                continue
            name = utils.safe_get_text(name_tag, '').strip()
            name = utils.cleantext(name)
            if not name:
                continue

            # Get video count from nord10 element
            count_tag = item.select_one('.nord10')
            count = utils.safe_get_text(count_tag, '').strip() if count_tag else ''

            if count:
                name = name + ' [COLOR hotpink]({0})[/COLOR]'.format(count)

            site.add_dir(name, caturl, 'List', img)
        except Exception as e:
            utils.log('missav Models: Error processing model - {}'.format(e))
            continue

    # Pagination - find "next" link and last page number
    next_link = soup.select_one('a[rel="next"][href]')
    if next_link:
        npurl = utils.safe_get_attr(next_link, 'href')
        # Extract current page from next URL
        np_match = re.search(r'page=(\d+)', npurl) if npurl else None
        np = np_match.group(1) if np_match else ''

        # Find last page number - look for page links before "next"
        page_links = soup.select('a[aria-label*="Go to page"]')
        lp = ''
        for page_link in page_links:
            page_text = utils.safe_get_text(page_link, '').strip()
            if page_text.isdigit():
                lp = page_text

        if npurl:
            site.add_dir('[COLOR hotpink]Next Page...[/COLOR] {0}/{1}'.format(np, lp), npurl, 'Models', site.img_next)

    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(site.url + 'en/')
    soup = utils.parse_html(html)

    # Find the span section with x-show attribute matching the category
    section = soup.find('span', attrs={'x-show': lambda x: x and url.lower() in x.lower() if x else False})
    if not section:
        # Try finding by x-cloak attribute with x-show
        sections = soup.select('span[x-cloak][x-show]')
        for sec in sections:
            x_show = utils.safe_get_attr(sec, 'x-show', default='')
            if url.lower() in x_show.lower():
                section = sec
                break

    if section:
        # Find all links within this section
        links = section.select('a[href]')
        for link in links:
            try:
                caturl = utils.safe_get_attr(link, 'href')
                if not caturl:
                    continue

                name = utils.safe_get_text(link, '').strip()
                name = utils.cleantext(name)
                if not name:
                    continue

                site.add_dir(name, caturl, 'List', '')
            except Exception as e:
                utils.log('missav Categories: Error processing category - {}'.format(e))
                continue

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url = url + keyword.replace(' ', '%2B')
        List(url)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    video_page = utils.getHtml(url, site.url)

    packed = re.compile(r'(eval\(function\(p,a,c,k,e,d\)[^\n]+)', re.DOTALL | re.IGNORECASE).search(video_page)
    if packed:
        packed = jsunpack.unpack(packed.group(1)).replace('\\', '')
        source = re.compile(r"source\s*=\s*'([^']+)", re.DOTALL | re.IGNORECASE).search(packed)
        if source:
            vp.play_from_direct_link('{0}|Referer={1}'.format(source.group(1), site.url))
        else:
            vp.progress.close()
            utils.notify('Oh Oh', 'No Videos found')
            return
    else:
        vp.progress.close()
        utils.notify('Oh Oh', 'No Videos found')
        return
