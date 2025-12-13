from plugin.video.cumination.resources.lib.soup_spec import SoupSiteSpec, SiteGenre
from plugin.video.cumination.resources.lib.constants import RES_SUCCESS
from plugin.video.cumination.resources.lib.soup_utils import parse_html, find_tag_with_text, get_tag_text, get_attr, strip_html_tags, find_all_tags, find_tag
from plugin.video.cumination.resources.lib.models import Episode, Video
from plugin.video.cumination.resources.lib.utils import generate_xhash, normalize_url
import re

class KbjFan(SoupSiteSpec):
    DOMAIN = 'kbjfan.com'
    BASE_URL = 'https://www.kbjfan.com'
    SITE_NAME = 'KBJFan'
    GENRES = [SiteGenre.ASIAN_JAV]

    LISTING_PATH = '/'
    SEARCH_PATH = '/'

    def parse_video_list(self, html: str, url: str) -> tuple[list[Video], str | None]:
        soup = parse_html(html)
        videos = []
        
        # Selector for video items: <posts class="posts-item ...">
        video_items = soup.find_all('posts', class_='posts-item')
        
        for item in video_items:
            # Anchor tag/Thumbnail
            thumb_div = item.find('div', class_='item-thumbnail')
            if not thumb_div:
                continue
            
            link_tag = thumb_div.find('a')
            if not link_tag:
                continue
                
            video_url = normalize_url(get_attr(link_tag, 'href'))
            if not video_url:
                continue
                
            # Thumbnail
            img_tag = thumb_div.find('img')
            thumbnail = get_attr(img_tag, 'data-src') or get_attr(img_tag, 'src')
            thumbnail = normalize_url(thumbnail)

            # Title
            heading_tag = item.find('h3', class_='item-heading')
            title = get_tag_text(heading_tag) if heading_tag else 'Unknown Title'
            
            # Date
            date_span = item.find('span', class_='ml6')
            date = get_tag_text(date_span)

            # Views
            meta_view = item.find('item', class_='meta-view')
            views = get_tag_text(meta_view)

            video_id = generate_xhash(video_url)

            videos.append(
                Video(
                    site=self.SITE_NAME,
                    title=title,
                    url=video_url,
                    image=thumbnail,
                    id=video_id,
                    date=date,
                    views=views
                )
            )

        # Pagination logic
        next_page_link = None
        # Look for standard WP pagination or explicit next link
        pagination = soup.find('div', class_='pagination') or soup.find('div', class_='pagenav')
        if pagination:
             next_tag = pagination.find('a', class_='next') or find_tag_with_text(pagination, 'a', 'Next')
             if next_tag:
                 next_page_link = normalize_url(get_attr(next_tag, 'href'))

        return videos, next_page_link

    def parse_video_page(self, html: str, url: str) -> Video:
        soup = parse_html(html)
        
        # Title
        title_tag = soup.find('h1', class_='article-title')
        title = get_tag_text(title_tag) or 'Unknown Title'
        
        # Video Source Extraction
        video_src = None
        
        # Priority 1: .new-dplayer element video-url attribute
        dplayer = soup.find('div', class_='new-dplayer')
        if dplayer:
            video_src = get_attr(dplayer, 'video-url')
        
        # Priority 2: .switch-video active link
        if not video_src:
            active_switch = soup.find('a', class_='switch-video active')
            if active_switch:
                video_src = get_attr(active_switch, 'video-url')

        if video_src:
            video_src = normalize_url(video_src)

        return Video(
            site=self.SITE_NAME,
            title=title,
            url=url,
            id=generate_xhash(url),
            video_src=video_src
        )
