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

import json
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "speedporn",
    "[COLOR hotpink]SpeedPorn[/COLOR]",
    "https://speedporn.net/",
    "speedporn.png",
    "speedporn",
    category="Video Tubes",
)

TAXONOMIES = (
    ("Genres", "watch-free-moivies-by-genres/"),
    ("Pornstars", "watch-free-moivies-by-pornstars/"),
    ("Studios", "watch-free-moivies-by-studios/"),
    ("Directors", "watch-free-moivies-by-directors/"),
    ("Years", "watch-free-moivies-by-release-years/"),
)

FILTERS = (
    ("Most Viewed", "most-viewed"),
    ("Longest", "longest"),
    ("Top Rated", "popular"),
)


@site.register(default_mode=True)
def Main():
    for title, path in TAXONOMIES:
        site.add_dir(
            "[COLOR hotpink]{}[/COLOR]".format(title),
            site.url + path,
            "Categories",
            site.img_cat,
        )
    for title, key in FILTERS:
        site.add_dir(
            "[COLOR hotpink]{}[/COLOR]".format(title),
            site.url + "all-movies/?filter=" + key,
            "List",
            site.img_cat,
        )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url + "all-movies/")
    utils.eod()


def _contextmenu(video_url, name):
    contexturl = (
        utils.addon_sys
        + "?mode=speedporn.Lookupinfo&url="
        + urllib_parse.quote_plus(video_url)
    )
    return [("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + contexturl + ")")]


def _add_next_page(soup, mode):
    next_link = soup.select_one("nav.pg a.next.page-numbers[href]")
    if not next_link:
        return
    next_url = urllib_parse.urljoin(site.url, utils.safe_get_attr(next_link, "href"))
    last_nr = ""
    numbers = [
        utils.safe_get_text(a).replace(",", "")
        for a in soup.select("nav.pg a.page-numbers:not(.next)")
    ]
    numbers = [n for n in numbers if n.isdigit()]
    if numbers:
        last_nr = "/" + numbers[-1]
    current = utils.safe_get_text(soup.select_one("nav.pg .page-numbers.current"))
    label = "Next Page"
    if current.replace(",", "").isdigit():
        label = "Next Page ({}{})".format(int(current.replace(",", "")) + 1, last_nr)
    site.add_dir(label, next_url, mode, site.img_next)


@site.register()
def List(url):
    listhtml = utils.getHtml(url, site.url)
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)
    spec = {
        "items": "article.card",
        # Extra card--x entries sit inside a <template> for client-side
        # injection (with a JS ad redirect in data-u); list only visible cards.
        "filter": lambda item: item.find_parent("template") is None,
        "url": {"selector": "a.card__th", "attr": "href"},
        "title": {
            "selector": ".card__t a",
            "text": True,
            "fallback_selectors": ["a.card__th img"],
        },
        "thumbnail": {
            "selector": "img.card__img",
            "attr": "src",
            "fallback_attrs": ["data-src"],
        },
        "duration": {"selector": ".card__dur", "text": True},
    }
    result = utils.soup_videos_list(site, soup, spec, contextm=_contextmenu)
    if not result["items"] and "?s=" in url:
        utils.notify("SpeedPorn", "No results found")

    _add_next_page(soup, "List")
    utils.eod()


@site.register()
def Categories(url):
    cathtml = utils.getHtml(url, site.url)
    if not cathtml:
        utils.eod()
        return

    soup = utils.parse_html(cathtml)
    # Genres render as chips; pornstars/studios/directors/years as tcards.
    # Scope both to the main grid so the "Recent Searches" footer chips are skipped.
    for item in soup.select(".tgrid a.tcard[href], .chips--lg a.chip[href]"):
        link = urllib_parse.urljoin(site.url, utils.safe_get_attr(item, "href"))
        count_el = item.select_one("small")
        count = utils.safe_get_text(count_el).replace(" movies", "")
        name_el = item.select_one("b")
        if name_el:
            name = utils.safe_get_text(name_el)
        else:
            if count_el:
                count_el.extract()
            name = utils.safe_get_text(item)
        name = utils.cleantext(name)
        if not name:
            continue
        if count:
            name += " [COLOR deeppink]({})[/COLOR]".format(count)
        img = utils.safe_get_attr(item.select_one("img"), "src", ["data-src"])
        site.add_dir(name, link, "List", img or site.img_cat)

    _add_next_page(soup, "Categories")
    utils.eod()


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    videopage = utils.getHtml(url, site.url)
    if not videopage:
        vp.progress.close()
        return

    soup = utils.parse_html(videopage)
    links = []
    servers_el = soup.select_one("[data-servers]")
    if servers_el:
        try:
            servers = json.loads(utils.safe_get_attr(servers_el, "data-servers"))
        except ValueError:
            servers = []
        for server in servers:
            src = server.get("u", "") if isinstance(server, dict) else ""
            if src.startswith("//"):
                src = "https:" + src
            if src.startswith("http") and src not in links:
                links.append(src)

    if not links:
        vp.progress.close()
        utils.notify("SpeedPorn", "No server links found")
        return

    def _is_dood(link):
        return any(d in link.lower() for d in utils.DOODSTREAM_DOMAINS)

    # DoodStream mirrors resolve reliably via the custom solver; try that first.
    for link in links:
        if _is_dood(link):
            stream_url = vp._solve_doodstream(link)
            if stream_url:
                vp.play_from_direct_link(stream_url)
                return

    links.sort(key=lambda link: 0 if _is_dood(link) else 1 if "lulu" in link else 2)
    vp.play_from_link_list(links)


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        List(url + urllib_parse.quote_plus(keyword))


@site.register()
def Lookupinfo(url):
    lookup_list = [
        ("Actor", r'href="[^"]*/(pornstars/[^"]+)"[^>]*>([^<]+)</a>', ""),
        ("Director", r'href="[^"]*/(directors/[^"]+)"[^>]*>([^<]+)</a>', ""),
        ("Studio", r'href="[^"]*/(director/[^"]+)"[^>]*>([^<]+)</a>', ""),
        ("Genre", r'href="[^"]*/(genres/[^"]+)"[^>]*>([^<]+)</a>', ""),
    ]
    utils.LookupInfo(site.url, url, "speedporn.List", lookup_list).getinfo()
