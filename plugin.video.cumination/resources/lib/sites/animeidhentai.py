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
    "animeid",
    "[COLOR hotpink]Animeid Hentai[/COLOR]",
    "https://animeidhentai.com/",
    "ah.png",
    "animeid",
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
        "[COLOR hotpink]Genres[/COLOR]", site.url, "animeidhentai_genres", site.img_cat
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
    listhtml = utils.getHtml(url, site.url)
    soup = utils.parse_html(listhtml)
    if not soup:
        utils.notify("Notify", "No videos found")
        return

    for article in soup.select("article"):
        link = article.select_one("a.link-co[href]") or article.select_one("a[href]")
        title = utils.safe_get_text(article.select_one(".link-co") or link, default="")
        if not link or not title:
            continue

        thumbnail = utils.safe_get_attr(article.select_one("img"), "src", ["data-src"])
        meta_block = article.find(attrs={"class": re.compile(r"\bmgr\b")})
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

        site.add_download_link(
            f"{clean_title}{year}",
            video_url,
            "animeidhentai_play",
            thumbnail,
            plot,
            quality=quality,
        )

    next_link = soup.select_one('link[rel="next"]') or soup.select_one(
        "a.next.page-numbers"
    )
    if next_link:
        href = utils.safe_get_attr(next_link, "href", default="")
        if href:
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
        name = utils.cleantext(
            utils.safe_get_text(article.select_one(".link-co"), default="")
        )
        count = utils.safe_get_text(article.select_one(".fwb"), default="")
        link = utils.safe_get_attr(article.select_one("a[href]"), "href", default="")
        thumb = utils.safe_get_attr(article.select_one("img"), "src", ["data-src"])

        if not name or not link:
            continue

        label = f"{name} [COLOR cyan]{count} Videos[/COLOR]" if count else name
        entries.append((label, link, thumb))

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
    videopage = utils.getHtml(url, site.url)
    soup = utils.parse_html(videopage)

    iframe = soup.select_one("iframe[src]") if soup else None
    if iframe:
        videourl = utils.safe_get_attr(iframe, "src", default="")
        if "nhplayer.com" in videourl:
            videopage = utils.getHtml(videourl, site.url)
            inner_soup = utils.parse_html(videopage)
            if inner_soup:
                source = inner_soup.select_one("li[data-id]")
                videourl = utils.safe_get_attr(source, "data-id", default="")
                if videourl and videourl.startswith("/"):
                    videourl = "https://nhplayer.com" + videourl
                    videohtml = utils.getHtml(videourl, site.url)
                    vp.direct_regex = r'file:\s*"([^"]+)"'
                    vp.play_from_html(videohtml)
                    vp.progress.close()
                    return
            vp.progress.close()
            utils.notify("Oh oh", "Couldn't find a playable link")
            return

        vp.play_from_link_to_resolve(videourl)
        return

    vp.progress.close()
    utils.notify("Oh oh", "Couldn't find a playable link")
