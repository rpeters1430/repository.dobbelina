"""
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
"""

from resources.lib import utils
from resources.lib.adultsite import AdultSite
from six.moves import urllib_parse

site = AdultSite(
    "ask4porn",
    "[COLOR orange]Ask4Porn[/COLOR]",
    "https://www.tap4porn.cc/",
    "ask4porn.png",
    "ask4porn",
    category="Video Tubes",
    requires_flaresolverr=True,
)


@site.register(default_mode=True)
def Main(url):
    site.add_dir("Newest", site.url + "videos", "List", "")
    site.add_dir("Best", site.url + "videos?filter=popular", "List", "")
    site.add_dir("Most Viewed", site.url + "videos?filter=most-viewed", "List", "")
    site.add_dir("Longest", site.url + "videos?filter=longest", "List", "")
    site.add_dir("Random", site.url + "videos?filter=random", "List", "")
    site.add_dir("Studios", site.url + "studios", "Studios", "")
    site.add_dir("Girls", site.url + "pornstars", "Girls", "")
    site.add_dir("Search", site.url, "Search", site.img_search)
    utils.eod()


@site.register()
def List(url):
    html, used_fs = utils.get_html_with_cloudflare_retry(url)
    soup = utils.parse_html(html)

    selectors = {
        "items": ["a.video-card", ".video-card", "article.thumb-block", ".thumb-block"],
        "url": {"selector": ":self", "attr": "href", "fallback_selectors": ["a"]},
        "title": {"selector": [".video-card-title", "span.title", "h2", ".title"], "text": True},
        "thumbnail": {"selector": "img", "attr": "src", "fallback_attrs": ["data-src"]},
        "duration": {"selector": ["span.video-card-duration", "span.duration"], "text": True},
        "pagination": {
            "selector": ["div.pagination a", ".pagination a", "a.page-link"],
            "text_matches": ["next", ">", "»"],
            "attr": "href",
        },
    }

    utils.soup_videos_list(site, soup, selectors)
    utils.eod()


@site.register()
def Studios(url):
    html, _ = utils.get_html_with_cloudflare_retry(url)
    soup = utils.parse_html(html)

    for item in soup.select("a.netflix-category-link"):
        href = utils.safe_get_attr(item, "href")
        name = utils.safe_get_text(item.select_one(".netflix-category-name"))
        img = utils.safe_get_attr(item.select_one("img"), "src")
        if name and href:
            site.add_dir(name, urllib_parse.urljoin(site.url, href), "List", img)

    for a_tag in soup.find_all("a"):
        text = utils.safe_get_text(a_tag)
        if ("next" in text.lower() or "»" in text) and "/page/" in (utils.safe_get_attr(a_tag, "href") or ""):
            site.add_dir("Next Page", urllib_parse.urljoin(site.url, utils.safe_get_attr(a_tag, "href")), "Studios", site.img_next)
            break

    utils.eod()


@site.register()
def Categories(url):
    html, _ = utils.get_html_with_cloudflare_retry(url)
    soup = utils.parse_html(html)

    for item in soup.select("a.netflix-tag-link"):
        href = utils.safe_get_attr(item, "href")
        name = utils.safe_get_text(item.select_one(".netflix-tag-name"))
        img = utils.safe_get_attr(item.select_one("img"), "src")
        if name and href:
            site.add_dir(name, urllib_parse.urljoin(site.url, href), "List", img)

    utils.eod()


@site.register()
def Girls(url):
    html, _ = utils.get_html_with_cloudflare_retry(url)
    soup = utils.parse_html(html)

    for item in soup.select("a.netflix-actor-link"):
        href = utils.safe_get_attr(item, "href")
        name = utils.safe_get_text(item.select_one(".netflix-actor-name"))
        img = utils.safe_get_attr(item.select_one("img"), "src")
        if name and href:
            site.add_dir(name, urllib_parse.urljoin(site.url, href), "List", img)

    for a_tag in soup.find_all("a"):
        href = utils.safe_get_attr(a_tag, "href") or ""
        text = utils.safe_get_text(a_tag)
        if (">" in text or "next" in text.lower() or "»" in text) and "/page/" in href:
            site.add_dir("Next Page", urllib_parse.urljoin(site.url, href), "Girls", site.img_next)
            break

    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download, IA_check="skip")
    
    slug = url.rstrip("/").split("/")[-1]
    if slug:
        api_url = urllib_parse.urljoin(site.url, "api/extract?slug=" + slug)
        api_json, _ = utils.get_html_with_cloudflare_retry(api_url, site.url)
        if api_json:
            import json
            try:
                soup = utils.parse_html(api_json)
                text_data = soup.get_text().strip() if soup else api_json.strip()
                data = json.loads(text_data)
                if isinstance(data, dict) and data:
                    for quality in ["1080p", "720p", "480p", "360p", "240p"]:
                        if quality in data and data[quality]:
                            stream_url = data[quality]
                            vp.play_from_direct_link(stream_url)
                            return
                    first_val = next(iter(data.values()))
                    if first_val and isinstance(first_val, str) and first_val.startswith("http"):
                        vp.play_from_direct_link(first_val)
                        return
            except Exception as e:
                utils.kodilog("Ask4Porn extract API error: {}".format(e))

    html, _ = utils.get_html_with_cloudflare_retry(url)
    vp.play_from_html(html, url)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        search_url = site.url + "?s=" + urllib_parse.quote(keyword)
        List(search_url)
