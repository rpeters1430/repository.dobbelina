'''
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
'''

import re
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('iflix', '[COLOR hotpink]Iflix[/COLOR]', 'http://www.incestflix.com/', 'http://inc-8rother.incestflix.com/img/wwwincestflixcom.png', 'iflix')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Sub-genres, Sub-fetishes, Themes[/COLOR]', site.url + 'alltags/sub', 'tags', site.img_cat)
    site.add_dir('[COLOR hotpink]Relations[/COLOR]', site.url + 'alltags/relations', 'tags', site.img_cat)
    site.add_dir('[COLOR hotpink]Ethnicities, Nationalities, Sects & Religious Groups[/COLOR]', site.url + 'alltags/ethn', 'tags', site.img_cat)
    site.add_dir('[COLOR hotpink]General, Other, Not Categorized[/COLOR]', site.url + 'alltags/general', 'tags', site.img_cat)
    site.add_dir('[COLOR hotpink]Actresses, Performers[/COLOR]', site.url + 'alltags/actresses', 'tags', site.img_cat)
    List(site.url + 'page/1')
    utils.eod()


@site.register()
def List(url):
    utils.kodilog(url)
    try:
        listhtml = utils.getHtml(url, '', timeout=30)
    except Exception as e:
        utils.kodilog('iflix List error: {}'.format(str(e)))
        utils.eod()
        return

    soup = utils.parse_html(listhtml)

    # Find all video links
    video_links = soup.select('a[id="videolink"]')
    if not video_links:
        utils.kodilog('iflix: No video links found')
        utils.eod()
        return

    for link in video_links:
        videopage = utils.safe_get_attr(link, 'href', default='')
        if not videopage:
            continue

        videopage = 'http:' + videopage if videopage.startswith('//') else videopage

        # Get title from text-heading div or text-overlay span
        title_div = link.select_one('.text-heading')
        if not title_div:
            title_span = link.select_one('.text-overlay span')
            name = utils.safe_get_text(title_span, '')
        else:
            name = utils.safe_get_text(title_div, '')

        name = utils.cleantext(name)
        if not name:
            continue

        # Extract thumbnail from background-image style
        img_div = link.select_one('.img-overflow')
        img = ''
        if img_div:
            style = utils.safe_get_attr(img_div, 'style', default='')
            # Extract URL from "background: url(...)" style
            match = re.search(r'url\(([^\)]+)\)', style)
            if match:
                img = match.group(1).strip()
                img = 'http:' + img if img.startswith('//') else img

        contextmenu = []
        contexturl = (utils.addon_sys + "?mode=iflix.Lookupinfo&url=" + urllib_parse.quote_plus(videopage))
        contextmenu.append(('[COLOR deeppink]Lookup info[/COLOR]', 'RunPlugin(' + contexturl + ')'))

        site.add_download_link(name, videopage, 'Playvid', img, name, contextm=contextmenu)

    # Handle pagination
    page = int(url.split('/')[-1])
    npage = page + 1
    # Check if next page link exists in the pager
    pager = soup.select_one('#incflix-pager')
    if pager:
        next_page_link = pager.select_one('a[href*="/page/{0}"]'.format(npage))
        if next_page_link:
            npage_url = url.replace('page/{0}'.format(page), 'page/{0}'.format(npage))
            site.add_dir('Next Page ({0})'.format(npage), npage_url, 'List', site.img_next)

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")

    try:
        video_page = utils.getHtml(url, site.url, timeout=30)
    except Exception as e:
        utils.kodilog('iflix Playvid error: {}'.format(str(e)))
        vp.progress.close()
        utils.notify('Error', 'Unable to load video page')
        return

    soup = utils.parse_html(video_page)

    # Find the source tag
    source_tag = soup.select_one('source[src]')
    if source_tag:
        videourl = utils.safe_get_attr(source_tag, 'src', default='')
        if videourl:
            videourl = 'http:' + videourl if videourl.startswith('//') else videourl
            vp.play_from_direct_link(videourl)
        else:
            vp.progress.close()
            utils.notify('Oh Oh', 'No video source found')
    else:
        vp.progress.close()
        utils.notify('Oh Oh', 'No Videos found')


@site.register()
def tags(url):
    what = url.split('/')[-1]
    url = '/'.join(url.split('/')[:-1])

    try:
        listhtml = utils.getHtml(url, '', timeout=30)
    except Exception as e:
        utils.kodilog('iflix tags error: {}'.format(str(e)))
        utils.eod()
        return

    soup = utils.parse_html(listhtml)

    # Find the appropriate section based on the 'what' parameter
    section_content = None
    if what == 'sub':
        # Find content between "Themes</h1>" and next "<h1>"
        themes_h1 = soup.find('h1', string=re.compile('Themes', re.IGNORECASE))
        if themes_h1:
            section_content = themes_h1.find_next_sibling()
    elif what == 'relations':
        relations_h1 = soup.find('h1', string=re.compile('Relations', re.IGNORECASE))
        if relations_h1:
            section_content = relations_h1.find_next_sibling()
    elif what == 'ethn':
        religious_h1 = soup.find('h1', string=re.compile('Religious Groups', re.IGNORECASE))
        if religious_h1:
            section_content = religious_h1.find_next_sibling()
    elif what == 'general':
        not_cat_h1 = soup.find('h1', string=re.compile('Not Categorized', re.IGNORECASE))
        if not_cat_h1:
            section_content = not_cat_h1.find_next_sibling()
    elif what == 'actresses':
        performers_h1 = soup.find('h1', string=re.compile('Performers', re.IGNORECASE))
        if performers_h1:
            # For actresses, get the parent div content
            section_content = performers_h1.find_parent()

    if not section_content:
        # Fallback: search in entire page
        section_content = soup

    # Find all tag links with studiolink id
    tag_links = section_content.select('span[id^="studiolink"]')

    for span in tag_links:
        link = span.find_parent('a')
        if not link:
            continue

        tagpage = utils.safe_get_attr(link, 'href', default='')
        if not tagpage:
            continue

        name_html = span.decode_contents() if hasattr(span, 'decode_contents') else str(span)
        name = utils.cleantext(name_html.strip()).replace('<b>', '[COLOR red][B]').replace('</b>', '[/B][/COLOR]')

        tagpage = 'http:' + tagpage if tagpage.startswith('//') else tagpage
        site.add_dir(name, tagpage + '/page/1', 'List', '')

    utils.eod()


@site.register()
def Lookupinfo(url):
    class SiteLookup(utils.LookupInfo):
        def url_constructor(self, url):
            url = 'http:' + url if url.startswith('//') else url
            return url + '/page/1'

    lookup_list = [
        ("Tag", r"<a class='studiolink\d+' href='([^']+)'>([^<]+)</a>", '')
    ]

    lookupinfo = SiteLookup(site.url, url, 'iflix.List', lookup_list)
    lookupinfo.getinfo()
