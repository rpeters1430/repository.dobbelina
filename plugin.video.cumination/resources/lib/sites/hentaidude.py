"""
    Cumination
    Copyright (C) 2020 Whitecream

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

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.sites.soup_spec import SoupSiteSpec


def _title_with_episode(title, item):
    episode = utils.safe_get_text(item.select_one('.btn-link'), default='')
    if episode:
        return f"{title} [COLOR pink][I]{episode}[/I][/COLOR]"
    return title

site = AdultSite(
    "hentaidude",
    "[COLOR hotpink]Hentaidude[/COLOR]",
    "https://hentaidude.xxx/",
    "https://hentaidude.xxx/wp-content/uploads/2021/03/Hentai-Dude.png",
    "hentaidude",
)


VIDEO_LIST_SPEC = SoupSiteSpec(
    selectors={
        "items": [".page-item-detail", ".tab-thumb"],
        "url": {"selector": "a", "attr": "href"},
        "title": {
            "selector": "a",
            "attr": "title",
            "text": True,
            "clean": True,
            "fallback_selectors": [".post-title", None],
            "transform": _title_with_episode,
        },
        "thumbnail": {
            "selector": "img",
            "attr": "src",
            "fallback_attrs": ["data-src", "data-original"],
        },
        "description": {"selector": ".btn-link", "text": True, "clean": True},
        "pagination": {
            "selectors": [
                {"query": 'link[rel="next"]', "scope": "soup"},
                {"query": "a.page-numbers.next, a.next", "scope": "soup"},
            ],
            "attr": "href",
            "label": "Next Page",
            "mode": "List",
        },
    },
    play_mode="EpList",
)


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Uncensored[/COLOR]', site.url + 'genre/uncensored-hentai/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]3D[/COLOR]', site.url + 'genre/3d-hentai/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Anal[/COLOR]', site.url + 'genre/anal/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]BBw[/COLOR]', site.url + 'genre/bbw/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]BDSM[/COLOR]', site.url + 'genre/bdsm/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Femdom[/COLOR]', site.url + 'genre/femdom/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Furry[/COLOR]', site.url + 'genre/furry/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Futanari[/COLOR]', site.url + 'genre/gender-bender-heantai/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Harem[/COLOR]', site.url + 'genre/harem/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Horror[/COLOR]', site.url + 'genre/horror/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Incest[/COLOR]', site.url + 'genre/incest-hentai/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]MILF[/COLOR]', site.url + 'genre/milf/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Monster[/COLOR]', site.url + 'genre/monster/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Romance[/COLOR]', site.url + 'genre/romance/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]School[/COLOR]', site.url + 'genre/hentai-school/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Shota[/COLOR]', site.url + 'genre/shota/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Shotacon[/COLOR]', site.url + 'genre/shotocon/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Softcore[/COLOR]', site.url + 'genre/softcore/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Tentacle[/COLOR]', site.url + 'genre/tentacle/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Tsundere[/COLOR]', site.url + 'genre/tsundere/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Teen[/COLOR]', site.url + 'genre/teen-hentai/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Young[/COLOR]', site.url + 'genre/young-hentai/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Yuri[/COLOR]', site.url + 'genre/yuri/page/1/?m_orderby=latest', 'List', site.img_cat, 1)
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'page/1/?s=', 'Search', site.img_search)
    List(site.url + 'page/1/?m_orderby=latest')


@site.register()
def List(url, page=1):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml or 'Page not found' in listhtml or 'No matches found.' in listhtml:
        utils.notify('Notify', 'No videos found')
        return

    soup = utils.parse_html(listhtml)
    VIDEO_LIST_SPEC.run(site, soup, base_url=site.url)
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        url += keyword.replace(' ', '+') + '&post_type=wp-manga'
        List(url, 1)


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download=download)
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    thumb_meta = soup.select_one('meta[itemprop="thumbnailUrl"]')
    if thumb_meta:
        thumb_url = utils.safe_get_attr(thumb_meta, 'content', default='')
        thumb_parts = thumb_url.rstrip('/').split('/')
        if len(thumb_parts) >= 2:
            stream_id = thumb_parts[-2]
            if not stream_id:
                vp.progress.close()
                utils.notify('Oh Oh', 'No Videos found')
                return
            videourl = f'https://master-lengs.org/api/v3/hh/{stream_id}/master.m3u8'
            vp.play_from_direct_link(videourl)
            return

    iframe = soup.select_one('iframe[src]')
    if iframe:
        vp.play_from_link_to_resolve(utils.safe_get_attr(iframe, 'src', default=''))
        return

    vp.progress.close()
    utils.notify('Oh Oh', 'No Videos found')


@site.register()
def EpList(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.notify('Notify', 'No episodes found')
        return

    for chapter in soup.select('[data-chapter]'):
        link = chapter.select_one('a[href]')
        if not link:
            continue

        episode = utils.safe_get_text(chapter.select_one('div'), default='').strip()
        chapter_num = chapter.get('data-chapter')
        episode_name = episode or (f"Episode {chapter_num}" if chapter_num else utils.safe_get_attr(link, 'href', default=''))
        img = utils.safe_get_attr(chapter.select_one('img'), 'src', ['data-src', 'data-original'])
        site.add_download_link(episode_name,
                               utils.safe_get_attr(link, 'href', default=''), 'Playvid', img)

    utils.eod()
