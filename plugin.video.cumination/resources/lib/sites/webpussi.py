from plugin.video.cumination.resources.lib.soup_spec import SoupSiteSpec, SiteGenre
from plugin.video.cumination.resources.lib.constants import RES_SUCCESS
from plugin.video.cumination.resources.lib.soup_utils import parse_html, find_tag_with_text, get_tag_text, get_attr, strip_html_tags, find_all_tags, find_tag
from plugin.video.cumination.resources.lib.models import Episode, Video
from plugin.video.cumination.resources.lib.utils import generate_xhash, normalize_url
import re

class Webpussi(SoupSiteSpec):
    DOMAIN = 'webpussi.com'
    BASE_URL = 'https://www.webpussi.com'
    SITE_NAME = 'Webpussi'
    GENRES = [SiteGenre.CAM_MODELS]

    LISTING_PATH = '/latest-updates/'
    SEARCH_PATH = '/search/'

    def parse_video_list(self, html: str, url: str) -> tuple[list[Video], str | None]:
        soup = parse_html(html)
        videos = []
        
        # Selector for video items
        # <div class="item">
        video_items = soup.find_all('div', class_='item')
        
        for item in video_items:
            # Anchor tag
            link_tag = item.find('a')
            if not link_tag:
                continue
                
            video_url = normalize_url(get_attr(link_tag, 'href'))
            if not video_url or '/videos/' not in video_url:
                continue
                
            title = get_attr(link_tag, 'title')
            
            # Thumbnail
            img_tag = item.find('img')
            thumbnail = get_attr(img_tag, 'data-original') or get_attr(img_tag, 'src')
            if thumbnail and 'base64' in thumbnail:
                 thumbnail = get_attr(img_tag, 'data-original')
            thumbnail = normalize_url(thumbnail)

            # Duration
            duration_tag = item.find('div', class_='duration')
            duration = get_tag_text(duration_tag)
            
            # Views (KVS typically puts views in <div class="views">)
            views_tag = item.find('div', class_='views')
            views = get_tag_text(views_tag)

            # Rating
            rating_tag = item.find('div', class_='rating')
            rating = get_tag_text(rating_tag)

            video_id = generate_xhash(video_url)

            videos.append(
                Video(
                    site=self.SITE_NAME,
                    title=title,
                    url=video_url,
                    image=thumbnail,
                    id=video_id,
                    duration=duration,
                    views=views,
                    rating=rating
                )
            )

        # Pagination
        # <li class="next"><a href="...">Next</a></li>
        next_page_link = None
        next_li = soup.find('li', class_='next')
        if next_li:
            next_a = next_li.find('a')
            if next_a:
                next_page_link = normalize_url(get_attr(next_a, 'href'))

        return videos, next_page_link

    def parse_video_page(self, html: str, url: str) -> Video:
        soup = parse_html(html)
        
        # Title
        title_tag = soup.find('h1')
        title = get_tag_text(title_tag) or 'Unknown Title'
        
        # Video Source Extraction from flashvars
        # var flashvars = { ... video_url: '...', ... };
        video_src = None
        flashvars_match = re.search(r'flashvars\s*=\s*({.*?});', html, re.DOTALL)
        if flashvars_match:
            flashvars_str = flashvars_match.group(1)
            # Extract video_url
            # video_url: 'function/0/https://...'
            url_match = re.search(r"video_url\s*:\s*'([^']+)'", flashvars_str)
            if url_match:
                raw_url = url_match.group(1)
                # Strip function/0/ prefix if present
                if raw_url.startswith('function/0/'):
                    video_src = raw_url.replace('function/0/', '')
                else:
                    video_src = raw_url

        return Video(
            site=self.SITE_NAME,
            title=title,
            url=url,
            id=generate_xhash(url),
            video_src=video_src
        )
