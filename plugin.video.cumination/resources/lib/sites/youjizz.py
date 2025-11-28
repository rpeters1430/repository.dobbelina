'''
    Cumination
    Copyright (C) 2024 Team Cumination

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
import json
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('youjizz', '[COLOR hotpink]YouJizz[/COLOR]', 'https://www.youjizz.com/', 'youjizz.png', 'youjizz')
cookiehdr = {'Cookie': 'age_verified=1'}


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'srch.php?search=', 'Search', site.img_search)
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'tags', 'Categories', site.img_cat)
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url, cookiehdr)

    if not listhtml or 'Error Page Not Found' in listhtml:
        utils.eod()
        return

    # Parse HTML with BeautifulSoup
    soup = utils.parse_html(listhtml)

    # Extract video items - YouJizz uses class="video-thumb"
    video_items = soup.select('.video-thumb')

    for item in video_items:
        try:
            # Get the link element
            link = item.select_one('a.frame.video')
            if not link:
                continue

            # Extract video URL
            video_url = utils.safe_get_attr(link, 'href')
            if not video_url:
                continue

            # Make absolute URL if needed
            if video_url.startswith('/'):
                video_url = site.url[:-1] + video_url

            # Extract title from the title section
            title_link = item.select_one('.video-title a')
            title = utils.safe_get_text(title_link) if title_link else ''
            if not title:
                # Fallback to image alt attribute
                img_tag = item.select_one('img.lazy')
                title = utils.safe_get_attr(img_tag, 'alt') if img_tag else 'Video'

            # Extract thumbnail image
            img_tag = item.select_one('img.lazy')
            img = utils.safe_get_attr(img_tag, 'data-original', ['src'])
            # Handle protocol-relative URLs
            if img and img.startswith('//'):
                img = 'https:' + img

            # Extract duration
            duration_tag = item.select_one('.time')
            if duration_tag:
                duration = utils.safe_get_text(duration_tag).replace('\xa0', ' ').strip()
                # Remove the clock icon text if present
                duration = re.sub(r'[^\d:]', '', duration)
            else:
                duration = ''

            # Add video to list
            site.add_download_link(title, video_url, 'Playvid', img, '', duration=duration)

        except Exception as e:
            # Log error but continue processing other videos
            utils.kodilog("YouJizz: Error parsing video item: " + str(e))
            continue

    # Extract pagination (Next Page link)
    # YouJizz uses numbered pagination links
    pagination = soup.select('.pagination li a')
    current_page = 1

    # Try to find current page number
    for page_link in pagination:
        if 'current' in page_link.get('class', []):
            try:
                current_page = int(utils.safe_get_text(page_link))
            except (ValueError, TypeError):
                pass
            break

    # Look for next page link
    next_num = current_page + 1
    for page_link in pagination:
        page_text = utils.safe_get_text(page_link)
        if page_text == str(next_num) or 'Next' in page_text or 'next' in page_text:
            next_url = utils.safe_get_attr(page_link, 'href')
            if next_url and next_url != 'javascript:;':
                # Build next page URL
                if next_url.startswith('/'):
                    next_url = site.url[:-1] + next_url
                site.add_dir('Next Page ({})'.format(next_num), next_url, 'List', site.img_next)
                break

    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        from six.moves import urllib_parse
        title = urllib_parse.quote_plus(keyword)
        searchUrl = searchUrl + title
        List(searchUrl)


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url, cookiehdr)

    if not cathtml:
        utils.eod()
        return

    soup = utils.parse_html(cathtml)

    # YouJizz uses simple <li> elements with links to tags
    # Find all links that point to /tags/
    tag_links = soup.select('li a[href*="/tags/"]')

    entries = []
    seen_tags = set()  # Prevent duplicates

    for tag_link in tag_links:
        try:
            catpage = utils.safe_get_attr(tag_link, 'href')
            if not catpage or catpage in seen_tags:
                continue

            seen_tags.add(catpage)

            if catpage.startswith('/'):
                catpage = site.url[:-1] + catpage

            # Extract tag name (text content of link)
            name = utils.safe_get_text(tag_link)

            # Skip empty or very short names
            if not name or len(name) < 2:
                continue

            # Skip tags that are just numbers or special characters
            if name.strip().isdigit() or name.strip() in ['&nbsp;', '...']:
                continue

            # Clean up the name
            name = name.strip()

            entries.append((name, catpage, '', name.lower()))

        except Exception as e:
            utils.kodilog("YouJizz: Error parsing tag: " + str(e))
            continue

    # Sort alphabetically
    entries.sort(key=lambda item: item[3])

    # Limit to reasonable number of tags (top 200)
    for display_name, catpage, img, _ in entries[:200]:
        site.add_dir(display_name, catpage, 'List', '', '')

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url, cookiehdr)
    if not html:
        vp.play_from_link_to_resolve(url)
        return

    src = _extract_best_source(html)
    if src:
        # Use the page URL as referer to satisfy CDN checks
        vp.play_from_direct_link("{0}|Referer={1}".format(src, url))
    else:
        vp.play_from_link_to_resolve(url)


def _extract_best_source(html):
    match = re.search(r'mediaDefinition\"?\\s*:\\s*(\\[.*?\\])', html, re.DOTALL)
    candidates = []
    if match:
        try:
            items = json.loads(match.group(1).replace('\\/', '/'))
            for item in items:
                url = item.get('videoUrl') or item.get('videoUrlMain')
                if not url:
                    continue
                quality = item.get('quality') or item.get('defaultQuality') or ''
                candidates.append((str(quality), url))
        except Exception:
            pass

    if not candidates:
        # Fallback: look for quality/url pairs used by Aylo inline JSON
        for quality, src in re.findall(r'"(?:quality|label)"\s*:\s*"?(\d{3,4})p?"?.*?"(?:videoUrl|src|url)"\s*:\s*"([^"]+)', html, re.IGNORECASE | re.DOTALL):
            candidates.append((quality, src.replace('\\/', '/')))

    if not candidates:
        for src in re.findall(r'<source[^>]+src=[\"\\\']([^\"\\\']+)', html, re.IGNORECASE):
            if any(ext in src for ext in ('.mp4', '.m3u8')):
                candidates.append(('', src.replace('\\/', '/')))
        for src in re.findall(r'https?://[^"\\\']+\.(?:mp4|m3u8)[^"\\\']*', html, re.IGNORECASE):
            candidates.append(('', src.replace('\\/', '/')))

    if not candidates:
        return ''

    def score(item):
        label = item[0]
        digits = ''.join(ch for ch in label if ch.isdigit())
        return int(digits) if digits else 0

    best = sorted(candidates, key=score, reverse=True)[0][1]
    if best.startswith('//'):
        best = 'https:' + best
    return best
