"""Self-test site with planted defects (the kinds seen in real retests):
junk titles, dead/placeholder thumbnails, no Next Page, blank and empty
category folders, a crashing category, empty search and a video that never
resolves. Only installed into the throwaway profile by the self-test."""

import json

from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

BASE = "http://127.0.0.1:__PORT__/broken/"

site = AdultSite("e2ebroken", "[COLOR hotpink]E2E Broken[/COLOR]", BASE, None, None, category="Video Tubes")


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", BASE + "cats", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", BASE + "search?q=", "Search", site.img_search)
    List(BASE + "list")


@site.register()
def List(url):
    data = json.loads(utils.getHtml(url))
    for v in data["videos"]:
        site.add_download_link(v["title"], v["url"], "Playvid", v["thumb"], "")
    utils.eod()


@site.register()
def Categories(url):
    data = json.loads(utils.getHtml(url))
    for c in data["categories"]:
        site.add_dir(c["name"], c["url"], c.get("mode", "List"), c["thumb"])
    utils.eod()


@site.register()
def Crash(url):
    raise ValueError("selftest: simulated scraper crash")


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        List(url + urllib_parse.quote_plus(keyword))


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    html = utils.getHtml(url)
    vp.play_from_html(html, url)
