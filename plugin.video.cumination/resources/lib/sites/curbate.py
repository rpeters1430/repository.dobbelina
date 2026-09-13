"""
Cumination
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

from __future__ import annotations

import re
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "curbate",
    "[COLOR hotpink]Curbate[/COLOR]",
    "https://curbate.tv/",
    "curbate.png",
    "curbate",
    category="Cams & Live",
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Popular[/COLOR]", site.url + "videos?sort=popular", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Novelties[/COLOR]", site.url + "videos?sort=novelties", "List", site.img_cat)
    site.add_dir("[COLOR hotpink]Models[/COLOR]", site.url + "models?sort=popular", "Models", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", site.url + "videos", "Search", site.img_search)
    List(site.url + "videos")
    utils.eod()


def _clean_title(href, model_name):
    slug = href.rstrip("/").split("/")[-1]
    cleaned_slug = re.sub(r"-\d+$", "", slug)
    slug_title = " ".join(cleaned_slug.split("-")).strip().title()
    if model_name and model_name.lower() in slug_title.lower():
        return slug_title
    if model_name:
        return "{}: {}".format(model_name.strip().title(), slug_title)
    return slug_title or "Video"


def _extract_next_page(soup, current_url):
    pag = soup.find(class_="pagination")
    if not pag:
        return None, None

    pages = pag.find(class_="pages")
    if pages:
        active = pages.find(class_="active")
        if active:
            parent_span = active.parent
            if parent_span:
                next_span = parent_span.find_next_sibling("span")
                if next_span:
                    next_a = next_span.find("a", href=True)
                    if next_a:
                        href = utils.safe_get_attr(next_a, "href")
                        if href:
                            next_url = urllib_parse.urljoin(site.url, href)
                            parsed = urllib_parse.urlparse(next_url)
                            qs = urllib_parse.parse_qs(parsed.query)
                            page_num = qs.get("page", [""])[0]
                            if qs.get("query") == ["*"] or qs.get("query") == ["**"]:
                                qs.pop("query")
                            clean_qs = urllib_parse.urlencode(qs, doseq=True)
                            final_url = urllib_parse.urlunparse((
                                parsed.scheme,
                                parsed.netloc,
                                parsed.path,
                                parsed.params,
                                clean_qs,
                                parsed.fragment,
                            ))
                            return final_url, page_num or "Next"

    return None, None


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    for card in soup.select(".video"):
        a = card.find("a", href=True)
        if not a:
            continue
        href = utils.safe_get_attr(a, "href")
        if not href or "/videos/" not in href:
            continue
        video_url = urllib_parse.urljoin(site.url, href)

        title_el = card.select_one(".video__title")
        model_name = title_el.get_text(strip=True) if title_el else ""
        title = _clean_title(href, model_name)

        img = card.select_one("img.lazy") or card.find("img")
        thumb = ""
        if img:
            thumb = (
                utils.safe_get_attr(img, "data-src")
                or utils.safe_get_attr(img, "src")
                or ""
            )

        dur_el = card.select_one(".video__data")
        dur_text = dur_el.get_text(strip=True) if dur_el else ""

        site.add_download_link(
            title,
            video_url,
            "Playvid",
            thumb,
            duration=dur_text,
        )

    next_url, next_page = _extract_next_page(soup, url)
    if next_url:
        site.add_dir("Next Page ({})".format(next_page), next_url, "List", site.img_next)

    utils.eod()


@site.register()
def Models(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    for card in soup.select(".actor_small"):
        a = card.find("a", href=True)
        if not a:
            continue
        href = utils.safe_get_attr(a, "href")
        if not href or "/models/" not in href:
            continue
        model_url = urllib_parse.urljoin(site.url, href)

        name_el = card.select_one(".actor__name")
        name = name_el.get_text(strip=True) if name_el else href.rstrip("/").split("/")[-1].title()

        img = card.select_one("img.lazy") or card.find("img")
        thumb = ""
        if img:
            thumb = (
                utils.safe_get_attr(img, "data-src")
                or utils.safe_get_attr(img, "src")
                or ""
            )

        info_el = card.select_one(".actor__info")
        desc = info_el.get_text(separator=" - ", strip=True) if info_el else ""

        site.add_dir(name, model_url, "List", thumb, desc=desc)

    next_url, next_page = _extract_next_page(soup, url)
    if next_url:
        site.add_dir("Next Page ({})".format(next_page), next_url, "Models", site.img_next)

    utils.eod()

@site.register()
def Search(url, keyword=None):
    if not keyword:
        keyword = utils._get_keyboard(heading=utils.i18n("search"))
    if not keyword:
        return
    search_url = urllib_parse.urljoin(site.url, "videos?query={}&page=1".format(urllib_parse.quote(keyword)))
    List(search_url)

@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url, site.url)
    if not html:
        return

    soup = utils.parse_html(html)

    # Check for direct embed container (ratio-inner / iframe-source)
    for el in soup.find_all(attrs={"src": True}):
        src = utils.safe_get_attr(el, "src")
        if not src or "googletagmanager" in src or "xhadapt" in src:
            continue
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = urllib_parse.urljoin(site.url, src)

        if any(d in src.lower() for d in utils.DOODSTREAM_DOMAINS):
            stream_url = vp._solve_doodstream(src)
            if stream_url:
                vp.play_from_direct_link(stream_url)
                return

        if vp.play_from_link_to_resolve(src):
            return

    for video in soup.find_all(["video", "source"]):
        src = utils.safe_get_attr(video, "src")
        if src:
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = urllib_parse.urljoin(site.url, src)
            vp.play_from_direct_link(src + "|Referer=" + url)
            return

    for a in soup.find_all("a", href=True):
        href = utils.safe_get_attr(a, "href")
        if href and not any(h in href.lower() for h in ("curbate.tv", "google", "traffic", "banner", "javascript:")):
            if vp.play_from_link_to_resolve(href):
                return
