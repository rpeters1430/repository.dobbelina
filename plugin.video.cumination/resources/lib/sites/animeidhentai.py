"""
Cumination
Copyright (C) 2018 Whitecream

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

site = AdultSite(
    "animeidhentai",
    "[COLOR hotpink]Animeid Hentai[/COLOR]",
    "https://animeidhentai.com/",
    "ah.png",
    "animeidhentai",
    category="Hentai & Anime",
)


@site.register(default_mode=True)
def animeidhentai_main():
    site.add_dir(
        "[COLOR hotpink]Uncensored[/COLOR]",
        "{0}genre/hentai-uncensored/".format(site.url),
        "animeidhentai_list",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Genres[/COLOR]", site.url + "genres/", "animeidhentai_genres", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Trending[/COLOR]",
        "{0}trending/".format(site.url),
        "animeidhentai_list",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Years[/COLOR]", "{0}?s=".format(site.url), "Years", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]",
        "{0}?s=".format(site.url),
        "animeidhentai_search",
        site.img_search,
    )
    animeidhentai_list("{0}?s=".format(site.url))


@site.register()
def animeidhentai_list(url):
    # Ensure URL is absolute
    if url.startswith("/"):
        url = site.url.rstrip("/") + url

    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.notify("Notify", "No videos found")
        return

    # Try to parse via Next.js RSC payload first
    videos_found = False
    
    import json
    all_text = ""
    for s in soup.select("script"):
        content = s.string or ""
        if "self.__next_f.push" in content:
            for m in re.finditer(r'self\.__next_f\.push\(\[\d+,\s*(["\'])(.*?)\1\s*\]\)', content):
                js_str = m.group(2)
                try:
                    unescaped = bytes(js_str, "utf-8").decode("unicode_escape")
                    all_text += unescaped
                except Exception:
                    cleaned = js_str.replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '\n')
                    all_text += cleaned

    video_records = []
    for m in re.finditer(r'"slug"\s*:\s*"([^"]+)"', all_text):
        slug_val = m.group(1)
        pos = m.start()
        start_pos = all_text.rfind('{', 0, pos)
        while start_pos != -1:
            end_pos = all_text.find('}', pos)
            while end_pos != -1:
                candidate = all_text[start_pos:end_pos+1]
                try:
                    data = json.loads(candidate)
                    if isinstance(data, dict) and "slug" in data and "title" in data:
                        if data["slug"] not in [v["slug"] for v in video_records]:
                            video_records.append(data)
                        break
                except Exception:
                    pass
                end_pos = all_text.find('}', end_pos + 1)
            if len(video_records) > 0 and video_records[-1]["slug"] == slug_val:
                break
            start_pos = all_text.rfind('{', 0, start_pos)

    for v in video_records:
        title = v.get("title", "")
        slug_val = v.get("slug", "")
        if not title or not slug_val:
            continue
            
        videos_found = True
        
        # Format title
        is_uncensored = not v.get("censored", True) or "uncensored" in title.lower()
        clean_title = re.sub(
            r"uncensored", "", utils.cleantext(title), flags=re.IGNORECASE
        ).strip()
        if is_uncensored:
            clean_title = f"{clean_title} [COLOR hotpink][I]Uncensored[/I][/COLOR]"
            
        year_val = v.get("year")
        year_str = f" [COLOR blue]({year_val})[/COLOR]" if year_val else ""
        
        quality = "HD" if v.get("quality") == "720p" else ("FHD" if v.get("quality") == "1080p" else "")
        plot = utils.cleantext(v.get("description", ""))
        
        # Thumbnail
        thumb = v.get("thumb") or v.get("cover")
        if thumb and thumb.startswith("/"):
            thumb = site.url.rstrip("/") + thumb
            
        video_url = site.url + slug_val
        
        site.add_download_link(
            f"{clean_title}{year_str}",
            video_url,
            "animeidhentai_play",
            thumb,
            plot,
            quality=quality,
        )

    # Fallback to older HTML parsing (keeps mock fixtures working!)
    if not videos_found:
        for article in soup.select("article"):
            link = article.select_one("a.lnk-blk[href]") or article.select_one("a[href]")
            if not link:
                continue
                
            title_tag = article.select_one(".ttl, .title, h2, h3")
            if title_tag:
                title = utils.safe_get_text(title_tag, default="")
            else:
                title = utils.safe_get_attr(link, "aria-label") or utils.safe_get_attr(link, "title")
                
            if not title:
                img_tag = article.select_one("img")
                title = utils.safe_get_attr(img_tag, "alt")
                
            if not title or title.lower() in ["play now", "play", "watch now"]:
                continue

            thumbnail = utils.safe_get_attr(article.select_one("img"), "src", ["data-src"])
            meta_block = article.select_one(".meta") or article.find(attrs={"class": re.compile(r"\bmgr\b")})
            meta_text = utils.safe_get_text(meta_block, default="")

            quality = ""
            meta_lower = meta_text.lower()
            if "1080" in meta_lower:
                quality = "FHD"
            elif "hd" in meta_lower or "720" in meta_lower:
                quality = "HD"

            is_uncensored = "uncensored" in title.lower()
            clean_title = re.sub(
                r"uncensored", "", utils.cleantext(title), flags=re.IGNORECASE
            ).strip()
            if is_uncensored:
                clean_title = f"{clean_title} [COLOR hotpink][I]Uncensored[/I][/COLOR]"

            year_match = re.search(r"(19|20)\d{2}", meta_text)
            year = f" [COLOR blue]({year_match.group(0)})[/COLOR]" if year_match else ""

            plot = utils.cleantext(
                utils.safe_get_text(article.select_one(".description"), default="")
            )
            video_url = utils.safe_get_attr(link, "href", default="")
            if not video_url:
                continue
                
            if video_url.startswith("/"):
                video_url = site.url.rstrip("/") + video_url

            site.add_download_link(
                f"{clean_title}{year}",
                video_url,
                "animeidhentai_play",
                thumbnail,
                plot,
                quality=quality,
            )

    # Next page pagination
    pager = soup.select_one(".pager")
    if pager:
        p_links = pager.select("a[href*='page=']")
        current_page = 1
        page_match = re.search(r"[?&]page=(\d+)", url)
        if page_match:
            current_page = int(page_match.group(1))
            
        next_page = current_page + 1
        for a in p_links:
            href = utils.safe_get_attr(a, "href", default="")
            if f"page={next_page}" in href:
                if href.startswith("/"):
                    href = site.url.rstrip("/") + href
                site.add_dir(
                    f"Next Page ({next_page})",
                    href,
                    "animeidhentai_list",
                    site.img_next
                )
                break
    else:
        # Fallback to legacy pagination parsing
        next_link = soup.select_one('link[rel="next"]') or soup.select_one(
            "a.next.page-numbers"
        )
        if next_link:
            href = utils.safe_get_attr(next_link, "href", default="")
            if href:
                if href.startswith("/"):
                    href = site.url.rstrip("/") + href
                page_match = re.search(r"page/(\d+)", href)
                label_suffix = f" ({page_match.group(1)})" if page_match else ""
                site.add_dir(
                    f"Next Page{label_suffix}", href, "animeidhentai_list", site.img_next
                )

    utils.eod()


@site.register()
def animeidhentai_search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "animeidhentai_search")
    else:
        title = keyword.replace(" ", "+")
        url += title
        animeidhentai_list(url)


@site.register()
def animeidhentai_genres(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.notify("Notify", "No genres found")
        return

    entries = []
    for article in soup.select("article"):
        # The genre name is usually in .ttl or img alt on the /genres/ page
        title_tag = article.select_one(".ttl, .title, h2, h3")
        name = utils.safe_get_text(title_tag, default="")
        if not name:
            img_tag = article.select_one("img")
            name = utils.safe_get_attr(img_tag, "alt")
            
        count = utils.safe_get_text(article.select_one(".fwb"), default="")
        link_tag = article.select_one("a[href*='/genre/']")
        link = utils.safe_get_attr(link_tag, "href", default="")
        thumb = utils.safe_get_attr(article.select_one("img"), "src", ["data-src"])

        if not name or not link:
            continue

        label = f"{name} [COLOR cyan]{count} Videos[/COLOR]" if count else name
        entries.append((label, link, thumb))

    if not entries:
        # Fallback to any genre links
        for a in soup.select("a[href*='/genre/']"):
            name = utils.cleantext(utils.safe_get_text(a))
            link = utils.safe_get_attr(a, "href")
            if name and link and name.lower() not in ["view more", "play now", "watch now"]:
                entries.append((name, link, ""))

    for label, link, thumb in sorted(entries, key=lambda x: x[0].lower()):
        site.add_dir(label, link, "animeidhentai_list", thumb)
    utils.eod()


@site.register()
def Years(url):
    yearhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(yearhtml)
    if not soup:
        utils.notify("Notify", "No years found")
        return

    years = [
        item.get("data-name")
        for item in soup.select('input[name="years"][data-name]')
        if item.get("data-name")
    ]
    if years:
        year = utils.selector("Select link", years, reverse=True)
        if year:
            animeidhentai_list(f"{site.url}year/{year}/")


@site.register()
def animeidhentai_play(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    
    # If the URL is already an nhplayer URL, resolve it directly!
    if "nhplayer.com" in url:
        resolved = utils.resolve_nhplayer(url, site.url)
        if resolved:
            vp.play_from_direct_link(resolved)
            vp.progress.close()
            return
            
        # Legacy fallback
        videopage = utils.getHtml(url, site.url)
        inner_soup = utils.parse_html(videopage)
        if inner_soup:
            source = inner_soup.select_one("li[data-id]")
            if source:
                surl = utils.safe_get_attr(source, "data-id", default="")
                if surl.startswith("/"):
                    surl = "https://nhplayer.com" + surl
                videohtml = utils.getHtml(surl, site.url)
                match = re.search(r'file:\s*"([^"]+)"', videohtml or "")
                if match:
                    vp.play_from_direct_link(match.group(1))
                    vp.progress.close()
                    return
        vp.progress.close()
        utils.notify("Oh oh", "Couldn't resolve nhplayer link")
        return

    videopage = utils.getHtml(url, site.url)
    soup = utils.parse_html(videopage)
    if not soup:
        vp.progress.close()
        utils.notify("Oh oh", "Couldn't parse video page")
        return

    # Extract embedUrl from RSC payload on the video page
    embed_url = None
    import json
    all_text = ""
    for s in soup.select("script"):
        content = s.string or ""
        if "self.__next_f.push" in content:
            for m in re.finditer(r'self\.__next_f\.push\(\[\d+,\s*(["\'])(.*?)\1\s*\]\)', content):
                js_str = m.group(2)
                try:
                    unescaped = bytes(js_str, "utf-8").decode("unicode_escape")
                    all_text += unescaped
                except Exception:
                    cleaned = js_str.replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '\n')
                    all_text += cleaned
                    
    slug = url.rstrip("/").split("/")[-1]
    for m in re.finditer(r'"slug"\s*:\s*"' + re.escape(slug) + r'"', all_text):
        pos = m.start()
        start_pos = all_text.rfind('{', 0, pos)
        while start_pos != -1:
            end_pos = all_text.find('}', pos)
            while end_pos != -1:
                candidate = all_text[start_pos:end_pos+1]
                try:
                    data = json.loads(candidate)
                    if isinstance(data, dict) and data.get("slug") == slug:
                        embed_url = data.get("embedUrl")
                        break
                except Exception:
                    pass
                end_pos = all_text.find('}', end_pos + 1)
            if embed_url:
                break
            start_pos = all_text.rfind('{', 0, start_pos)

    if not embed_url:
        # Fallback to search for any nhplayer link in the page
        nh_match = re.search(r'https?://[a-zA-Z0-9\.-]*nhplayer\.com/v/[^\s"\']+', videopage or "")
        if nh_match:
            embed_url = nh_match.group(0)

    if embed_url:
        resolved = utils.resolve_nhplayer(embed_url, url)
        if resolved:
            vp.play_from_direct_link(resolved)
            vp.progress.close()
            return
            
        # Legacy fallback
        v_html = utils.getHtml(embed_url, url)
        inner_soup = utils.parse_html(v_html)
        if inner_soup:
            source = inner_soup.select_one("li[data-id]")
            if source:
                surl = utils.safe_get_attr(source, "data-id", default="")
                if surl.startswith("/"):
                    surl = "https://nhplayer.com" + surl
                videohtml = utils.getHtml(surl, url)
                match = re.search(r'file:\s*"([^"]+)"', videohtml or "")
                if match:
                    vp.play_from_direct_link(match.group(1))
                    vp.progress.close()
                    return
            
    # Try legacy iframe fallback if nhplayer solve fails or wasn't found in RSC
    iframes = soup.select("iframe[src]")
    iframe = None
    for ifr in iframes:
        src = utils.safe_get_attr(ifr, "src", default="").lower()
        if any(x in src for x in ["nhplayer", "player", "embed", "video", "stream"]):
            iframe = ifr
            break
            
    if not iframe and iframes:
        iframe = iframes[0]

    if iframe:
        videourl = utils.safe_get_attr(iframe, "src", default="")
        if "nhplayer.com" in videourl:
            resolved = utils.resolve_nhplayer(videourl, url)
            if resolved:
                vp.play_from_direct_link(resolved)
                vp.progress.close()
                return
                
            # Legacy fallback
            v_html = utils.getHtml(videourl, url)
            inner_soup = utils.parse_html(v_html)
            if inner_soup:
                source = inner_soup.select_one("li[data-id]")
                if source:
                    surl = utils.safe_get_attr(source, "data-id", default="")
                    if surl.startswith("/"):
                        surl = "https://nhplayer.com" + surl
                    videohtml = utils.getHtml(surl, url)
                    match = re.search(r'file:\s*"([^"]+)"', videohtml or "")
                    if match:
                        vp.play_from_direct_link(match.group(1))
                        vp.progress.close()
                        return

        vp.play_from_link_to_resolve(videourl)
        return

    vp.progress.close()
    utils.notify("Oh oh", "Couldn't find an iframe with video")
