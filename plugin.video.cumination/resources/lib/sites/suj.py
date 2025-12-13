from plugin.video.cumination.resources.lib.soup_spec import SoupSiteSpec, SiteGenre
from plugin.video.cumination.resources.lib.constants import RES_SUCCESS
from plugin.video.cumination.resources.lib.soup_utils import parse_html, find_tag_with_text, get_tag_text, get_attr, strip_html_tags, find_all_tags, find_tag
from plugin.video.cumination.resources.lib.models import Episode, Video
from plugin.video.cumination.resources.lib.utils import generate_xhash, normalize_url
import re

class Suj(SoupSiteSpec):
    DOMAIN = 'pc.suj.mobi'
    BASE_URL = 'https://pc.suj.mobi'
    SITE_NAME = 'SUJ.MOBI'
    GENRES = [SiteGenre.GENERAL_STREAMING]

    LISTING_PATH = '/scenes'
    SEARCH_PATH = '/search'
    
    # Example video URL: https://pc.suj.mobi/scene/zhenschiny_v_odezhde_delajut_minet_muzhchinam_video_3862
    SCENE_URL_REGEX = re.compile(r'/scene/[^/]+_video_(\d+)')

    def parse_video_list(self, html: str, url: str) -> tuple[list[Video], str | None]:
        soup = parse_html(html)
        videos = []
        
        # Find all video thumbnail blocks
        # Example structure: <div class="col-sm-6 col-md-3"><div class="thumbnail thumb-video showScenes ">...</div></div>
        video_blocks = soup.find_all('div', class_=re.compile(r'col-sm-6 col-md-3'))
        
        for block in video_blocks:
            anchor = block.find('a', class_='showV')
            if not anchor:
                continue

            video_url = normalize_url(get_attr(anchor, 'href'))
            if not video_url:
                continue

            title_tag = anchor.find('span', class_='pV')
            title = strip_html_tags(title_tag.text if title_tag else 'Unknown Title').strip()

            thumbnail_tag = anchor.find('img', class_='lazyload thumb_side_scroller')
            thumbnail = normalize_url(get_attr(thumbnail_tag, 'data-src') or get_attr(thumbnail_tag, 'src'))

            duration_tag = anchor.find('span', class_='scenetime')
            duration = strip_html_tags(duration_tag.text) if duration_tag else None
            
            views_tag = anchor.find('span', class_='views')
            views = strip_html_tags(views_tag.text) if views_tag else None

            video_id_match = self.SCENE_URL_REGEX.search(video_url)
            video_id = video_id_match.group(1) if video_id_match else generate_xhash(video_url)

            videos.append(
                Video(
                    site=self.SITE_NAME,
                    title=title,
                    url=video_url,
                    image=thumbnail,
                    id=video_id,
                    duration=duration,
                    views=views
                )
            )
        
        # Next page logic (assuming standard pagination or "More Videos" link)
        # Check for "Ещё видео" (More videos) link or standard pagination
        next_page_link = None
        more_videos_div = soup.find('div', class_='more_videos')
        if more_videos_div:
            more_videos_anchor = more_videos_div.find('a')
            if more_videos_anchor and "Ещё видео" in more_videos_anchor.get_text(strip=True):
                next_page_link = normalize_url(get_attr(more_videos_anchor, 'href'))
        
        # If no explicit "More videos" link, try to find standard pagination
        if not next_page_link:
            pagination_ul = soup.find('ul', class_='pagination')
            if pagination_ul:
                # Find the 'next' button, typically indicated by a specific class or text
                next_li = find_tag_with_text(pagination_ul, 'a', '»') # Or check for arrow
                if next_li:
                    next_page_link = normalize_url(get_attr(next_li, 'href'))

        return videos, next_page_link

    def parse_video_page(self, html: str, url: str) -> Video:
        soup = parse_html(html)
        
        # Extract video details from a single video page
        # This part needs to be implemented after understanding the video page structure.
        # For now, return a placeholder or incomplete Video object.
        
        # Example: Title
        title_tag = soup.find('h1', class_='text-left') 
        title = strip_html_tags(title_tag.text).strip() if title_tag else 'Unknown Video Title'
        
        # Example: Description
        description_tag = soup.find('div', class_='text-description')
        description = strip_html_tags(description_tag.text).strip() if description_tag else None

        # Example: Video Source URL (This is usually more complex, might be in a script tag or iframe)
        # This needs a deeper dive into the video page.
        # Placeholder for now:
        video_source_url = None
        
        # Attempt to find the video player and extract source
        video_tag = soup.find('video', id='player') # Assuming a <video> tag with id 'player'
        if video_tag:
            source_tag = video_tag.find('source')
            if source_tag:
                video_source_url = normalize_url(get_attr(source_tag, 'src'))
        
        if not video_source_url:
            # Look for iframe or script containing video URL
            iframe = soup.find('iframe', {'src': re.compile(r'//lv\.sujcloud\.com/player\.php')})
            if iframe:
                video_source_url = normalize_url(get_attr(iframe, 'src'))

        video_id_match = self.SCENE_URL_REGEX.search(url)
        video_id = video_id_match.group(1) if video_id_match else generate_xhash(url)

        return Video(
            site=self.SITE_NAME,
            title=title,
            url=url,
            id=video_id,
            description=description,
            video_src=video_source_url
        )

    # TODO: Implement additional methods for categories, search, etc.
