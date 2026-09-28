"""Self-test site: behaves like a healthy site. Only installed into the
throwaway Kodi profile by `python -m scripts.kodi_e2e selftest`."""

import json

from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

BASE = "http://127.0.0.1:__PORT__/good/"

site = AdultSite("e2egood", "[COLOR hotpink]E2E Good[/COLOR]", BASE, None, None, category="Video Tubes")


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Categories[/COLOR]", BASE + "cats", "Categories", site.img_cat)
    site.add_dir("[COLOR hotpink]Search[/COLOR]", BASE + "search?q=", "Search", site.img_search)
    List(BASE + "list?page=1")


@site.register()
def List(url):
    data = json.loads(utils.getHtml(url))
    for v in data["videos"]:
        site.add_download_link(v["title"], v["url"], "Playvid", v["thumb"], v["title"])
    if data.get("next"):
        site.add_dir("Next Page ({})".format(data["page"] + 1), data["next"], "List", site.img_next)
    utils.eod()


@site.register()
def Categories(url):
    data = json.loads(utils.getHtml(url))
    for c in data["categories"]:
        site.add_dir(c["name"], c["url"], "List", c["thumb"])
    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        List(url + urllib_parse.quote_plus(keyword) + "&page=1")


@site.register()
def Playvid(url, name, download=None):
    vp = utils.VideoPlayer(name, download)
    vp.progress.update(25, "[CR]Loading video page[CR]")
    vp.play_from_direct_link(url)
