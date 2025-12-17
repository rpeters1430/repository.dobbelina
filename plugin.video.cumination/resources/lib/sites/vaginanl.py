"""
    Cumination
    Copyright (C) 2023 Whitecream

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
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('vaginanl', '[COLOR hotpink]Vagina.nl[/COLOR] [COLOR orange](Dutch)[/COLOR]', 'https://vagina.nl/', 'https://c749a9571b.mjedge.net/img/logo-default.png', 'vaginanl')


@site.register(default_mode=True)
def main(url):
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'categories', 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'sexfilms/search?q=', 'Search', site.img_search)
    List(url + 'sexfilms/newest')


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml or "Geen zoekresultaten gevonden" in listhtml or "Nothing found" in listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    if not soup:
        utils.eod()
        return

    cards = soup.select('div.card')

    for card in cards:
        link = card.select_one('a[href]')
        if not link:
            continue

        videourl = urllib_parse.urljoin(site.url, utils.safe_get_attr(link, 'href', default=''))
        title = utils.safe_get_attr(link, 'title', default='')
        if not title:
            title = utils.safe_get_attr(card.select_one('img'), 'alt', default='') or utils.safe_get_text(
                card.select_one('.title, .card-title'), default=''  # type: ignore[arg-type]
            )
        title = utils.cleantext(title)

        if not videourl or not title:
            continue

        thumb = utils.safe_get_attr(card.select_one('img'), 'data-src', ['src', 'data-original'], default='')
        if thumb:
            thumb = urllib_parse.urljoin(site.url, thumb)

        duration = utils.safe_get_text(card.select_one('.duration, .video-duration, .time'), default='')

        site.add_download_link(title, videourl, 'Playvid', thumb, title, duration=duration)

    next_link = soup.select_one('a.next[rel="next"], li.next a[rel="next"], a.next.page-numbers, a[rel="next"].page-numbers')
    if next_link:
        href = urllib_parse.urljoin(site.url, utils.safe_get_attr(next_link, 'href', default=''))
        page_match = re.search(r'(?:page=|/page/)(\d+)', href)
        last_page = ''
        page_numbers = [int(num) for num in re.findall(r'\b(\d+)\b', utils.safe_get_text(soup.select_one('.pagination') or soup, default=''))]
        if page_numbers:
            last_page = str(max(page_numbers))

        if href:
            suffix = ''
            if page_match:
                suffix = f" ({page_match.group(1)}"
                if last_page:
                    suffix += f"/{last_page}"
                suffix += ')'
            site.add_dir(f"Next Page{suffix}", href, 'List', site.img_next)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    vp.play_from_site_link(url)


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        title = keyword.replace(' ', '%20')
        searchUrl = searchUrl + title
        utils.kodilog(searchUrl)
        List(searchUrl)


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)

    if not soup:
        utils.eod()
        return

    cards = soup.select('div.card')

    for card in cards:
        link = card.select_one('a[href]')
        if not link:
            continue

        caturl = urllib_parse.urljoin(site.url, utils.safe_get_attr(link, 'href', default=''))
        name = utils.safe_get_attr(card.select_one('img'), 'alt', default='') or utils.safe_get_text(
            card.select_one('.title, .card-title'), default=''  # type: ignore[arg-type]
        )

        if not caturl or not name:
            continue

        img = utils.safe_get_attr(card.select_one('img'), 'data-src', ['src', 'data-original'], default='')
        if img:
            img = urllib_parse.urljoin(site.url, img)

        site.add_dir(utils.cleantext(name), caturl, 'List', img)

    utils.eod()
