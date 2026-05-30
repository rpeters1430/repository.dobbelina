"""
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
"""

import re
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('hypnotube', '[COLOR hotpink]HypnoTube[/COLOR]', 'https://hypnotube.com/', 'hypnotube.webp', 'hypnotube', category='Specialty')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Trending[/COLOR]', site.url + 'most-viewed/month/', 'List', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/', 'Search', site.img_search)
    List(site.url + 'videos/page1.html')


@site.register()
def List(url):
    soup = utils.parse_html(utils.getHtml(url))
    for item in soup.select('[class*="item-inner-col"]'):
        link = item.select_one('a[href*="/video/"][title]')
        if not link:
            continue
        video_url = utils.safe_get_attr(link, 'href')
        name = utils.cleantext(utils.safe_get_attr(link, 'title'))
        img = utils.safe_get_attr(item.select_one('img'), 'src')
        duration_tag = item.select_one('.time')
        duration = utils.safe_get_text(duration_tag).strip() if duration_tag else ''
        display_name = name + (f' [COLOR yellow]({duration})[/COLOR]' if duration else '')
        site.add_download_link(display_name, video_url, 'Playvid', img, name)

    next_link = soup.select_one("a[title='Next'][href]")
    if next_link:
        np = utils.safe_get_attr(next_link, 'href')
        page_match = re.search(r'page(\d+)', np)
        nextpage = page_match.group(1) if page_match else ''
        label = f'Next Page... ({nextpage})' if nextpage else 'Next Page...'
        site.add_dir(label, site.url + 'videos/' + np, 'List', site.img_next)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url += keyword.replace(' ', '+')
        List(url + '/')


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.play_from_site_link(url, url)
