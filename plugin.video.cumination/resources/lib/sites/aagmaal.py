"""
Cumination Site Plugin
Copyright (C) 2020 Team Cumination

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
    "aagmaal",
    "[COLOR hotpink]Aag Maal[/COLOR]",
    "https://aagmaal.bz/",
    "aagmaal.png",
    "aagmaal",
    category="Specialty",
)


def _handle_pagination(soup, mode="List"):
    """Handle pagination across List, ListOTT, and OTT modes."""
    vp_nav = soup.select_one(".vp-pagi-wrap, .vp-pagination, nav.pagination, .pagination")
    if vp_nav:
        next_link = vp_nav.select_one("a.next, a.next-page, a.next.page-numbers")
        if next_link:
            next_url = utils.safe_get_attr(next_link, "href")
            if next_url:
                curr = vp_nav.select_one(".current, .active")
                curr_txt = utils.safe_get_text(curr, "").strip()
                last_txt = ""
                dots = vp_nav.select_one(".dots")
                if dots:
                    after_dots = dots.find_next_sibling("a")
                    if after_dots:
                        last_txt = utils.safe_get_text(after_dots, "").strip()
                if not last_txt:
                    page_nums = [
                        p
                        for p in vp_nav.select("a.page-numbers, span.page-numbers")
                        if utils.safe_get_text(p, "").strip().isdigit()
                    ]
                    if page_nums:
                        last_txt = utils.safe_get_text(page_nums[-1], "").strip()

                if last_txt and curr_txt:
                    pgtxt = "Currently in Page {0} of {1}".format(curr_txt, last_txt)
                elif curr_txt:
                    pgtxt = "Currently in Page {0}".format(curr_txt)
                else:
                    pgtxt = ""

                name = "[COLOR hotpink]Next Page...[/COLOR]" + (
                    " ({0})".format(pgtxt) if pgtxt else ""
                )
                site.add_dir(name, next_url, mode, site.img_next)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Categories[/COLOR]", site.url, "Categories", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]OTT[/COLOR]", site.url + "ott/", "OTT", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    for item in soup.select("article"):
        link = item.select_one("a.vp-card__thumb") or item.select_one("a[href]")
        if not link:
            continue

        videopage = utils.safe_get_attr(link, "href")
        if not videopage:
            continue

        img_tag = link.select_one("img")
        name = utils.safe_get_attr(img_tag, "alt") or utils.safe_get_attr(link, "title")
        if not name:
            name = utils.safe_get_text(item.select_one("h2, h3, .entry-title"))
        if not name:
            name = "Video"
        name = utils.cleantext(name)

        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])

        site.add_download_link(name, videopage, "Playvid", img, name)

    _handle_pagination(soup, "List")
    utils.eod()


@site.register()
def ListOTT(url):
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)

    for item in soup.select("article"):
        link = item.select_one("a.vp-card__thumb") or item.select_one("a[href]")
        if not link:
            continue

        videopage = utils.safe_get_attr(link, "href")
        if not videopage:
            continue

        img_tag = link.select_one("img")
        name = utils.safe_get_attr(img_tag, "alt") or utils.safe_get_attr(link, "title")
        if not name:
            name = utils.safe_get_text(item.select_one("h2, h3, .entry-title"))
        if not name:
            name = "Video"
        name = utils.cleantext(name)

        img = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"])

        site.add_download_link(name, videopage, "Playvid", img, name)

    _handle_pagination(soup, "ListOTT")
    utils.eod()


@site.register()
def OTT(url):
    otthtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(otthtml)

    cards = soup.select(".vp-tax-index-card, .vp-tax-card, a.vp-tax-index-card__thumb, article")
    seen_links = set()

    for card in cards:
        link = card if card.name == "a" else card.select_one("a.vp-tax-index-card__thumb, a[href]")
        if not link:
            continue

        catpage = utils.safe_get_attr(link, "href")
        if not catpage or catpage in seen_links:
            continue
        seen_links.add(catpage)

        img_tag = card.select_one("img") or link.select_one("img")
        thumb = utils.safe_get_attr(img_tag, "src", ["data-src", "data-original"]) if img_tag else ""
        name = utils.safe_get_attr(img_tag, "alt") if img_tag else ""
        if not name:
            name = utils.safe_get_text(card.select_one("h2, h3, .title, a"))

        # Extract video count if present
        vids = ""
        count_tag = card.select_one("span.count, .vp-tax-count, span")
        if count_tag:
            digits = "".join(filter(str.isdigit, utils.safe_get_text(count_tag, "")))
            if digits:
                vids = digits

        if not vids:
            count_match = re.search(r"(\d+)\s*(?:video|vids)?", card.get_text())
            if count_match:
                vids = count_match.group(1)

        name = utils.cleantext(name)
        if vids:
            name_display = "{0} [COLOR cyan][I][{1} video(s)][/I][/COLOR]".format(name, vids)
        else:
            name_display = name

        site.add_dir(name_display, catpage, "ListOTT", thumb)

    _handle_pagination(soup, "OTT")
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videourl = ""

    videopage = utils.getHtml(url, site.url)
    soup = utils.parse_html(videopage)

    links = {}

    # 1. Download server cards / buttons (.vp-dl-server + .vp-dl-btn)
    for server in soup.select(".vp-dl-server"):
        server_name = utils.safe_get_text(server, "").strip()
        next_elem = server.find_next_sibling()
        if next_elem:
            btn = next_elem.select_one("a.vp-dl-btn[href], a[href]") or (
                next_elem if next_elem.name == "a" and next_elem.has_attr("href") else None
            )
            if btn:
                href = utils.safe_get_attr(btn, "href")
                if href and vp.resolveurl.HostedMediaFile(href):
                    links[server_name or href] = href

    # 2. Numbered links or download buttons in content area
    if not links:
        content = soup.select_one(".vp-video-post-content, .entry-content, #content")
        if content:
            for a in content.select("a[href]"):
                link_url = utils.safe_get_attr(a, "href")
                if link_url and vp.resolveurl.HostedMediaFile(link_url):
                    link_title = utils.safe_get_attr(a, "title") or utils.safe_get_text(a)
                    if not link_title or len(link_title) < 3:
                        prev = a.find_previous(string=True)
                        if prev:
                            link_title = prev.strip().split("\n")[-1].strip()

                    if not link_title:
                        link_title = link_url.split("//")[-1].split("/")[0]

                    links[link_title] = link_url

    # 3. Regex fallback for .vp-dl-server or numbered patterns
    if not links:
        pat1 = re.compile(
            r'''class="vp-dl-server">([^<]+)</div>\s*<p><a\s*class="vp-dl-btn"\s*href="([^"]+)''',
            re.DOTALL | re.IGNORECASE,
        )
        pat2 = re.compile(
            r'''<br\s*/>\s*([\d]+)\.\s*<a\s*href="([^"]+)''',
            re.DOTALL | re.IGNORECASE,
        )
        found_links = pat1.findall(videopage) or pat2.findall(videopage)
        if found_links:
            for host, link in found_links:
                if vp.resolveurl.HostedMediaFile(link):
                    links[host] = link

    # 4. Fallback to any external links
    if not links:
        for a in soup.select('a.external[href], a[class*="external"][href], a[href*="http"]'):
            link_url = utils.safe_get_attr(a, "href")
            if link_url and vp.resolveurl.HostedMediaFile(link_url):
                links[link_url] = link_url

    if links:
        videourl = utils.selector("Select link", links)

    if not videourl:
        iframe = soup.select_one(
            "article iframe[data-src], iframe[data-src], article iframe[src], iframe[src]"
        )
        if iframe:
            videourl = utils.safe_get_attr(iframe, "data-src") or utils.safe_get_attr(iframe, "src")

    if not videourl:
        for pattern in [
            r'<iframe[^>]*\s+loading="lazy"\s+src="([^"]+)"',
            r'<iframe[^>]*\s+src="([^"]+)"',
            r'<article.+?iframe\s+data-src="([^"]+)"',
        ]:
            match = re.search(pattern, videopage, re.DOTALL | re.IGNORECASE)
            if match:
                videourl = match.group(1)
                break

    if not videourl:
        utils.notify("Oh Oh", "No Videos found")
        vp.progress.close()
        return

    vp.play_from_link_to_resolve(videourl)


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(cathtml)

    cat_links = []
    for h3 in soup.select("h3"):
        if "categories" in utils.safe_get_text(h3, "").lower():
            ul = h3.find_next_sibling("ul")
            if ul:
                for li in ul.select("li a[href]"):
                    catpage = utils.safe_get_attr(li, "href")
                    name = utils.cleantext(utils.safe_get_text(li))
                    if catpage and name:
                        cat_links.append((name, catpage))
            break

    if not cat_links:
        for a in soup.select("ul.menu a[href], nav a[href], .menu a[href]"):
            catpage = utils.safe_get_attr(a, "href")
            name = utils.cleantext(utils.safe_get_text(a))
            if catpage and name and len(name) > 2:
                if not any(
                    x in catpage
                    for x in ["dmca", "contact", "18-usc", "sample-page", "page/"]
                ):
                    cat_links.append((name, catpage))

    seen = set()
    unique_links = []
    for name, catpage in cat_links:
        if catpage not in seen:
            seen.add(catpage)
            unique_links.append((name, catpage))

    for name, catpage in sorted(unique_links, key=lambda x: x[0].lower()):
        site.add_dir(name, catpage, "List")

    utils.eod()


@site.register()
def Search(url, keyword=None):
    searchUrl = url
    if not keyword:
        site.search_dir(url, "Search")
    else:
        title = keyword.replace(" ", "+")
        searchUrl = searchUrl + title
        List(searchUrl)
