"""
Cumination
Copyright (C) 2026 Team Cumination

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import annotations

import re
import time
from six.moves import urllib_parse

from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "watchmdh",
    "[COLOR hotpink]WatchMDH[/COLOR]",
    "https://watchdirty.is/",
    "watchmdh.png",
    "watchmdh",
)


@site.register(default_mode=True)
def Main():
    site.add_dir(
        "[COLOR hotpink]Site status[/COLOR]",
        site.url,
        "SiteStatus",
        site.img_cat,
        Folder=False,
    )
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)
    for item in soup.select(".item"):
        link = item.select_one("a[href]")
        if not link:
            continue

        video_url = utils.safe_get_attr(link, "href")
        if not video_url:
            continue
        video_url = urllib_parse.urljoin(site.url, video_url)

        name = utils.cleantext(
            utils.safe_get_attr(link, "title") or utils.safe_get_text(link)
        )
        if not name:
            continue

        img_tag = link.select_one("img")
        thumb = utils.get_thumbnail(img_tag)
        if thumb:
            thumb = urllib_parse.urljoin(site.url, thumb)

        duration = utils.safe_get_text(item.select_one(".duration"))
        quality = utils.safe_get_text(item.select_one(".is-hd, .quality"))

        contextm = [
            (
                "[COLOR violet]Related videos[/COLOR]",
                "RunPlugin({}?mode=watchmdh.List&url={})".format(
                    utils.addon_sys, urllib_parse.quote_plus(video_url)
                ),
            )
        ]
        site.add_download_link(
            name,
            video_url,
            "Playvid",
            thumb,
            name,
            duration=duration,
            quality=quality,
            contextm=contextm,
        )

    next_link = soup.select_one(".pagination a.next, .pagination a[data-block-id]")
    if next_link:
        block_id = utils.safe_get_attr(next_link, "data-block-id")
        params = utils.safe_get_attr(next_link, "data-parameters")
        next_url = ""
        if block_id and params:
            params_qs = params.replace(";", "&").replace(":", "=")
            params_qs = re.sub(
                r"from_videos=(\d+)",
                lambda m: "from_videos={}".format(int(m.group(1)) + 1),
                params_qs,
            )
            next_url = "{}?mode=async&function=get_block&block_id={}&{}&_={}".format(
                site.url + "latest-updates/",
                block_id,
                params_qs,
                int(time.time() * 1000),
            )
        else:
            href = utils.safe_get_attr(next_link, "href")
            if href:
                next_url = urllib_parse.urljoin(site.url, href)

        if next_url:
            contextm = [
                (
                    "[COLOR violet]Goto Page #[/COLOR]",
                    "RunPlugin({}?mode=watchmdh.List&url={})".format(
                        utils.addon_sys, urllib_parse.quote_plus(next_url)
                    ),
                )
            ]
            site.add_dir(
                "[COLOR hotpink]Next Page...[/COLOR]",
                next_url,
                "List",
                site.img_next,
                contextm=contextm,
            )

    utils.eod()


@site.register()
def SiteStatus(url):
    utils.notify(
        "WatchMDH",
        "Site currently redirects/age-gates and may not provide list pages.",
    )
