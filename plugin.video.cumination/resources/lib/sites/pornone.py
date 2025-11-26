'''
    Cumination
    Copyright (C) 2015 Whitecream

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

site = AdultSite('pornone', '[COLOR hotpink]PornOne[/COLOR]', 'https://pornone.com/', 'pornone.png', 'pornone')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'categories/', 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search?q=', 'Search', site.img_search)
    List(site.url + 'newest/')
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    # Find all video items
    video_items = soup.select('a.popbop, .video-item')

    for item in video_items:
        try:
            # Get the video link
            videopage = utils.safe_get_attr(item, 'href')
            if not videopage:
                continue

            # Make absolute URL if needed
            if not videopage.startswith('http'):
                videopage = site.url[:-1] + videopage if videopage.startswith('/') else site.url + videopage

            # Get image and title
            img_tag = item.select_one('img')
            img = utils.safe_get_attr(img_tag, 'data-src', ['src'])
            name = utils.safe_get_attr(img_tag, 'alt', default='Video')
            name = utils.cleantext(name.strip())

            # Get duration
            duration_tag = item.select_one('[class*="duration"], .time')
            if not duration_tag:
                # Try to find duration in item's text
                for text in item.stripped_strings:
                    if ':' in text and any(c.isdigit() for c in text):
                        duration = text.strip()
                        break
                else:
                    duration = ''
            else:
                duration = utils.safe_get_text(duration_tag).strip()

            # Check for HD
            hd = ''
            if 'HD Video' in str(item):
                hd = 'HD'

            site.add_download_link(name, videopage, 'Playvid', img, name, duration=duration, quality=hd)

        except Exception as e:
            utils.kodilog("Error parsing video item: " + str(e))
            continue

    # Handle pagination - try multiple methods
    next_url = None
    next_page_num = ''

    # Method 1: Look for <link rel="next"> (HTML5 pagination hint)
    next_link = soup.select_one('link[rel="next"]')
    if next_link:
        next_url = utils.safe_get_attr(next_link, 'href')
        utils.kodilog('pornone: Found pagination via link[rel="next"]: {}'.format(next_url))

    # Method 2: Look for pagination UI elements (more reliable)
    if not next_url:
        pagination = soup.select_one('.pagination, [class*="pag"]')
        if pagination:
            next_button = pagination.select_one('a[class*="next"], a:contains("Next"), a:contains(">")')
            if next_button:
                next_url = utils.safe_get_attr(next_button, 'href')
                utils.kodilog('pornone: Found pagination via next button: {}'.format(next_url))

    # Method 3: Look for numbered page links and find the highest page number + 1
    if not next_url:
        # Extract current page number from URL
        current_page_match = re.search(r'/(\d+)[/\?]', url)
        if current_page_match:
            current_page = int(current_page_match.group(1))
            # Construct next page URL by incrementing page number
            next_url = re.sub(r'/(\d+)([/\?])', r'/{}\2'.format(current_page + 1), url)
            utils.kodilog('pornone: Constructed next page URL from current page {}: {}'.format(current_page, next_url))

    if next_url:
        # Make absolute URL if needed
        if not next_url.startswith('http'):
            next_url = site.url[:-1] + next_url if next_url.startswith('/') else site.url + next_url

        # Extract page number for display
        page_nums = re.findall(r'/(\d+)[/\?]', next_url)
        next_page_num = page_nums[-1] if page_nums else ''

        # Validate that next page URL is different from current URL to prevent loops
        if next_url != url:
            site.add_dir('[COLOR hotpink]Next Page...[/COLOR] ({0})'.format(next_page_num), next_url, 'List', site.img_next)
        else:
            utils.kodilog('pornone: Next page URL same as current URL - pagination loop detected and prevented')

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    html = utils.getHtml(url, site.url)
    sources = re.compile(r'''<source\s*src="([^"]+)".+?label="([^"]+)''', re.DOTALL | re.IGNORECASE).findall(html)
    sources = {quality: videourl for videourl, quality in sources}
    videourl = utils.selector('Select quality', sources, setting_valid='qualityask', sort_by=lambda x: int(x[:-1]), reverse=True)
    if videourl:
        vp.play_from_direct_link(videourl)
    else:
        vp.progress.close()
        return


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)

    # Find all category items
    category_items = soup.select('a.popbop')

    for item in category_items:
        try:
            # Get the category link
            catpage = utils.safe_get_attr(item, 'href')
            if not catpage:
                continue

            # Make absolute URL if needed
            catpage = site.url[:-1] + catpage if catpage.startswith('/') else catpage

            # Get image and name
            img_tag = item.select_one('img')
            name = utils.safe_get_attr(img_tag, 'alt', default='Category')
            image = utils.safe_get_attr(img_tag, 'data-src', ['src'])

            # Clean up category name
            name = utils.cleantext(name.replace('Video category ', ''))

            site.add_dir(name, catpage, 'List', image)

        except Exception as e:
            utils.kodilog("Error parsing category item: " + str(e))
            continue

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
