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

from resources.lib import utils
from resources.lib.adultsite import AdultSite


site = AdultSite('luxuretv', '[COLOR hotpink]LuxureTV[/COLOR]', 'https://luxuretv.com/', 'https://luxuretv.com/images/logo.png', 'luxuretv')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'channels/', 'Cat', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'searchgate/videos/', 'Search', site.img_search)
    List(site.url)


@site.register()
def List(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    # Find all video content items
    content_items = soup.select('.content, [class*="content"]')
    for item in content_items:
        try:
            # Get video link
            link = item.select_one('a[href][title]')
            if not link:
                continue

            video = utils.safe_get_attr(link, 'href')
            if not video:
                continue

            name = utils.safe_get_attr(link, 'title')
            if not name:
                name = utils.safe_get_text(link, '').strip()
            name = utils.cleantext(name)

            # Get image
            img_tag = item.select_one('img[src]')
            img = utils.safe_get_attr(img_tag, 'src', ['data-src']) if img_tag else ''

            # Get duration from time element
            time_tag = item.select_one('.time')
            duration = ''
            if time_tag:
                # Check for <b> tag inside time, or get text directly
                b_tag = time_tag.select_one('b')
                duration = utils.safe_get_text(b_tag if b_tag else time_tag, '').strip()

            site.add_download_link(name, video, 'Play', img, name, duration=duration)
        except Exception as e:
            utils.log('luxuretv List: Error processing video - {}'.format(e))
            continue

    # Pagination - find "Suivante" (Next) link
    pagination = soup.select_one('.pagination')
    if pagination:
        next_link = pagination.find('a', string=lambda text: text and 'Suivante' in text if text else False)
        if next_link:
            next_href = utils.safe_get_attr(next_link, 'href')
            if next_href:
                # Build full next page URL
                base_url = url.split('page')[0] if 'page' in url else url
                next_url = base_url + next_href
                # Extract page number for display
                page_num = next_url.split('page')[-1].split('.')[0] if 'page' in next_url else ''
                site.add_dir('[COLOR hotpink]Next Page...[/COLOR] ({0})'.format(page_num), next_url, 'List', site.img_next)

    utils.eod()


@site.register()
def Cat(url):
    listhtml = utils.getHtml(url)
    soup = utils.parse_html(listhtml)

    # Find all channel content items
    channel_items = soup.select('.content-channel, [class*="content-channel"]')
    for item in channel_items:
        try:
            # Get image
            img_tag = item.select_one('img[src]')
            img = utils.safe_get_attr(img_tag, 'src', ['data-src']) if img_tag else ''

            # Get category link and name
            link = item.select_one('a[href]')
            if not link:
                continue

            catpage = utils.safe_get_attr(link, 'href')
            if not catpage:
                continue

            name = utils.safe_get_text(link, '').strip()
            if not name:
                continue

            site.add_dir(name, catpage, 'List', img)
        except Exception as e:
            utils.log('luxuretv Cat: Error processing category - {}'.format(e))
            continue

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url = "{0}{1}/".format(url, keyword.replace(' ', '-'))
        List(url)


@site.register()
def Play(url, name, download=None):
    listhtml = utils.getHtml(url, url)
    soup = utils.parse_html(listhtml)

    # Find video source tag
    source_tag = soup.select_one('source[src]')
    if source_tag:
        videourl = utils.safe_get_attr(source_tag, 'src')
        if videourl:
            vp = utils.VideoPlayer(name, download=download)
            vp.play_from_direct_link(videourl)
            return

    utils.notify('Oh oh', 'No video found')
