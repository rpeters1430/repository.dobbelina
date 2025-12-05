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
from resources.lib.sites.soup_spec import SoupSiteSpec

site = AdultSite(
    'hentaihavenc',
    '[COLOR hotpink]Hentaihaven[/COLOR]',
    'https://hentaihaven.co/',
    'hh.png',
    'hentaihavenco'
)


VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        'items': 'a.a_item',
        'url': {'attr': 'href'},
        'title': {'selector': '.video_title', 'text': True, 'clean': True},
        'thumbnail': {'selector': 'img', 'attr': 'data-src', 'fallback_attrs': ['src']},
        'pagination': {
            'selector': 'a.page-link',
            'text_matches': ['next'],
            'attr': 'href',
            'label': '[COLOR hotpink]Next Page[/COLOR]',
            'mode': 'List'
        }
    },
    play_mode='Playvid'
)


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
    if not soup:
        utils.notify('Notify', 'No videos found')
        return

    VIDEO_LIST_SPEC.run(site, soup, base_url=site.url)
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, site.url)
    soup = utils.parse_html(videopage)
    iframe = soup.select_one('iframe[src]')
    if iframe:
        surl = utils.safe_get_attr(iframe, 'src', default='')
        if 'nhplayer.com' in surl:
            videopage = utils.getHtml(surl, site.url)
            soup = utils.parse_html(videopage)
            data_id_li = soup.select_one('li[data-id]')
            if data_id_li:
                surl = data_id_li['data-id']
                if surl.startswith('/'):
                    surl = 'https://nhplayer.com' + surl
                videohtml = utils.getHtml(surl, site.url)
                file_script = utils.parse_html(videohtml)
                # BeautifulSoup can't parse JavaScript, so we scan script tags with regex for the file URL.
                match = None
                if file_script:
                    for script in file_script.find_all("script", string=True):
                        if script.string:
                            match = re.search(r'file:\s*"([^"]+)"', script.string)
                            if match:
                                break
                if match:
                    vp.play_from_direct_link(match.group(1))
                    vp.progress.close()
                    return
            else:
                vp.progress.close()
                utils.notify('Oh oh', 'Couldn\'t find a playable link')
        else:
            vp.play_from_link_to_resolve(surl)
            return

    vp.progress.close()
    utils.notify('Oh oh', 'Couldn\'t find a playable link')
    return


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    if not soup:
        utils.eod()
        return

    for item in soup.select('a.cat_item'):
        catpage = utils.safe_get_attr(item, 'href', default='')
        bg_style = utils.safe_get_attr(item.select_one('.cat_bg'), 'style', default='')
        image_match = re.search(r"url\(([^)]+)\)", bg_style)
        image = image_match.group(1) if image_match else ''
        name = utils.cleantext(utils.safe_get_text(item.select_one('.cat_ttl'), default=''))
        desc = utils.safe_get_text(item.select_one('.cat_dsc'), default='')
        count = utils.safe_get_text(item.select_one('.cat_count'), default='').strip()

        if not catpage or not name:
            continue

        if count:
            name += " [COLOR orange][I]{0} videos[/I][/COLOR]".format(count)
        site.add_dir(name, site.url[:-1] + catpage, 'List', site.url[:-1] + image, desc=desc)
    utils.eod()


@site.register()
def Series(url, section=None):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)
    if not soup:
        utils.eod()
        return

    for item in soup.select('a.vc_item'):
        series_url = utils.safe_get_attr(item, 'href', default='')
        name = utils.cleantext(utils.safe_get_text(item.select_one('.vcat_title'), default=''))
        img = utils.safe_get_attr(item.select_one('.vcat_poster img'), 'data-src', ['src'])
        if not series_url or not name:
            continue
        site.add_dir(name, site.url[:-1] + series_url, 'List', site.url[:-1] + img)

    next_page_link = soup.find('a', class_='page-link', string=lambda t: t and 'Next' in t)
    if next_page_link:
        page_num_match = re.search(r'page=(\d+)', utils.safe_get_attr(next_page_link, 'href', default=''))
        page_label = f" ({page_num_match.group(1)})" if page_num_match else ''
        site.add_dir(f'[COLOR hotpink]Next Page[/COLOR]{page_label}', site.url[:-1] + utils.safe_get_attr(next_page_link, 'href', default=''), 'Series', site.img_next)

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
