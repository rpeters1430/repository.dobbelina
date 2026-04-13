"""
    Cumination site scraper
    Copyright (C) 2026 Team Cumination

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
import xbmc
import xbmcgui
from resources.lib import utils
from resources.lib.adultsite import AdultSite


site = AdultSite(
    "cloudbate",
    "[COLOR hotpink]Cloudbate[/COLOR]",
    "https://www.cloudbate.com/",
    "cloudbate.png",
    "cloudbate",
    category="Cam Models",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Girls[/COLOR]",
        site.url + "categories/girls/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Trans[/COLOR]",
        site.url + "categories/trans/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Couples[/COLOR]",
        site.url + "categories/couples/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search (models)[/COLOR]",
        site.url + "search/{0}/",
        "Search",
        site.img_search,
    )
    List(site.url + "latest-updates/")
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)

    # Modern BS4 implementation
    soup = utils.parse_html(listhtml)

    # Content area check
    content = soup.select_one(".row-videos, .list-videos, .row")
    if not content:
        content = soup

    items_added = 0
    # The site uses .item containers for videos, but fixtures might use .video-block
    for item in content.select(".item, .video-block"):
        try:
            # Video link can contain /video/ or /videos/
            link = item.select_one('a[href*="/video/"], a[href*="/videos/"]')
            if not link:
                continue
            videopage = utils.safe_get_attr(link, "href")
            if not videopage.startswith("http"):
                videopage = urllib_parse.urljoin(site.url, videopage)

            # Skip model links if accidentally caught (though /video/ should be specific)
            if "/models/" in videopage:
                continue

            name = utils.safe_get_attr(link, "title")
            if not name:
                name = utils.safe_get_text(link)
            name = utils.cleantext(name)

            img_tag = item.select_one("img")
            img = utils.safe_get_attr(img_tag, "data-webp", ["data-src", "src"])
            if img and not img.startswith("http"):
                img = urllib_parse.urljoin(site.url, img)

            duration_tag = item.select_one(".duration")
            duration = utils.safe_get_text(duration_tag)

            cm = []
            quoted_videopage = urllib_parse.quote_plus(videopage)
            cm.append(
                (
                    "[COLOR deeppink]Lookup info[/COLOR]",
                    "RunPlugin({}?mode=cloudbate.Lookupinfo&url={})".format(
                        utils.addon_sys, quoted_videopage
                    ),
                )
            )
            cm.append(
                (
                    "[COLOR deeppink]Related videos[/COLOR]",
                    "RunPlugin({}?mode=cloudbate.Related&url={})".format(
                        utils.addon_sys, quoted_videopage
                    ),
                )
            )

            site.add_download_link(
                name, videopage, "Playvid", img, name, duration=duration, contextm=cm
            )
            items_added += 1
        except Exception as e:
            utils.kodilog("Cloudbate parse error: {}".format(e))
            continue

    if items_added == 0:
        if 'There is no data in this list.' in listhtml:
             utils.notify(msg='No videos found!')
        return

    # Pagination
    next_link = soup.select_one('a.next.page-link')
    if next_link:
        next_url = utils.safe_get_attr(next_link, 'href')
        if next_url:
            if not next_url.startswith('http'):
                next_url = urllib_parse.urljoin(site.url, next_url)
            
            # Extract current page number for label
            # e.g. /latest-updates/02/ -> 2
            match_np = re.search(r'/0*(\d+)/', next_url)
            np = match_np.group(1) if match_np else ""
            
            # Find last page number if possible
            last_page = ""
            for pg_link in soup.select('.page-item a.page-link'):
                pg_text = utils.safe_get_text(pg_link)
                if pg_text.isdigit():
                    last_page = pg_text

            label = 'Next Page ({})'.format(np)
            if last_page:
                label += ' of {}'.format(last_page)
                
            site.add_dir(label, next_url, 'List', site.img_next, contextm='cloudbate.GotoPage', lp=last_page)

    utils.eod()


@site.register()
def GotoPage(url, np, lp=None):
    dialog = xbmcgui.Dialog()
    pg = dialog.numeric(0, 'Enter Page number')
    if pg:
        if lp and int(lp) > 0 and int(pg) > int(lp):
            utils.notify(msg='Out of range!')
            return
        # Replace page number in URL: /latest-updates/01/ -> /latest-updates/5/
        # Matches /01/, /1/, /001/ etc.
        url = re.sub(r'/0*(\d+)/', '/{}/'.format(pg), url, count=1)
        contexturl = (utils.addon_sys + "?mode=" + "cloudbate.List&url=" + urllib_parse.quote_plus(url))
        xbmc.executebuiltin('Container.Update(' + contexturl + ')')


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    vpage = utils.getHtml(url, site.url)
    if "kt_player('kt_player'" in vpage:
        vp.progress.update(60, "[CR]{0}[CR]".format("kt_player detected"))
        vp.play_from_kt_player(vpage, url)


@site.register()
def Search(url, keyword=None):
    def SrcList(url):
        listhtml = utils.getHtml(url, site.url)
        soup = utils.parse_html(listhtml)
        
        models = []
        for item in soup.select('li.lists'):
            link = item.select_one('a[title]')
            if link:
                m_url = utils.safe_get_attr(link, 'href')
                m_name = utils.safe_get_attr(link, 'title')
                if m_url and m_name:
                    if not m_url.startswith('http'):
                        m_url = urllib_parse.urljoin(site.url, m_url)
                    models.append((m_name, m_url))

        if not models:
            utils.notify(msg='No models found!')
            return
            
        sources = {name: m_url for name, m_url in models}
        if len(sources) == 1:
            List(models[0][1])
        else:
            model_url = utils.selector("Select Model", sources)
            if model_url:
                List(model_url)

    if not keyword:
        site.search_dir(url, 'Search')
    else:
        # url is 'https://www.cloudbate.com/search/{0}/'
        SrcList(url.format(keyword.replace(' ', '-')))


@site.register()
def Related(url):
    contexturl = (utils.addon_sys + "?mode=" + str('cloudbate.List') + "&url=" + urllib_parse.quote_plus(url))
    xbmc.executebuiltin('Container.Update(' + contexturl + ')')


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Model", r'href="([^"]+models/[^"]+)">([^<]+)<', ''),
        ("Category", r'href="([^"]+categories/[^"]+)">([^<]+)<', ''),
        ("Tag", r'href="([^"]+tags/[^"]+)">([^<]+)</a>', '')]
    lookupinfo = utils.LookupInfo(site.url, url, 'cloudbate.List', lookup_list)
    lookupinfo.getinfo()
