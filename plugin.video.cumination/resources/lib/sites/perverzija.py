"""
Cumination
Copyright (C) 2021 Team Cumination

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
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite(
    "perverzija",
    "[COLOR hotpink]Perverzija[/COLOR]",
    "https://www.perverzija.com/",
    "perverzija.png",
    "perverzija",
    category="Video Tubes",
    requires_flaresolverr=True,
)


@site.register(default_mode=True)
def Main():
    site.add_dir("[COLOR hotpink]Tags[/COLOR]", site.url + "tags/", "Tag", site.img_cat)
    site.add_dir(
        "[COLOR hotpink]Studios[/COLOR]", site.url + "studios/", "Studios", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Stars[/COLOR]", site.url + "stars/", "Stars", site.img_cat
    )
    site.add_dir(
        "[COLOR hotpink]Full Movies[/COLOR]",
        site.url + "full-movie/",
        "List",
        site.img_cat,
    )
    site.add_dir(
        "[COLOR hotpink]Search[/COLOR]", site.url + "?s=", "Search", site.img_search
    )
    List(site.url + "page/1/")


@site.register()
def List(url):
    listhtml, _ = utils.get_html_with_cloudflare_retry(url)
    if not listhtml:
        utils.eod()
        return

    soup = utils.parse_html(listhtml)

    container = soup.select_one(".video-listing-filter") or soup
    videos = container.select("div.item-thumbnail")

    for video in videos:
        link = video.select_one("a[href][title]")
        if not link:
            continue

        videourl = urllib_parse.urljoin(
            site.url, utils.safe_get_attr(link, "href", default="")
        )
        name = utils.cleantext(
            utils.safe_get_attr(
                link, "title", default=utils.safe_get_text(link, default="")
            )
        )
        if not videourl or not name:
            continue

        img_tag = video.select_one("img")
        img = utils.get_thumbnail(img_tag)
        duration = utils.safe_get_text(video.select_one(".time_dur"), default="")

        contextmenu = []
        contexturl = (
            utils.addon_sys
            + "?mode="
            + str("perverzija.Lookupinfo")
            + "&url="
            + urllib_parse.quote_plus(videourl)
        )
        contextmenu.append(
            ("[COLOR deeppink]Lookup info[/COLOR]", "RunPlugin(" + contexturl + ")")
        )

        site.add_download_link(
            name,
            videourl,
            "Play",
            img,
            name,
            noDownload=True,
            contextm=contextmenu,
            duration=duration,
        )

    pagination = soup.find(
        "a", attrs={"label": re.compile(r"Next", re.IGNORECASE)}
    ) or soup.select_one('a[rel="next"]')
    if pagination:
        pgtxt_elem = soup.find(class_=re.compile(r"\bpages\b"))
        pgtxt = utils.cleantext(utils.safe_get_text(pgtxt_elem, default=""))
        label = "Next Page..."
        if pgtxt:
            label += f" (Currently in {pgtxt})"
        next_url = urllib_parse.urljoin(
            site.url, utils.safe_get_attr(pagination, "href", default="")
        )
        site.add_dir(label, next_url, "List", site.img_next)
    utils.eod()


def _taxonomy(url, fragment):
    html, _ = utils.get_html_with_cloudflare_retry(url)
    if not html:
        utils.eod()
        return

    soup = utils.parse_html(html)

    seen = set()
    for link in soup.select(f'a[href*="{fragment}"]'):
        href = utils.safe_get_attr(link, "href", default="")
        name = utils.cleantext(utils.safe_get_text(link, default=""))
        if not href or not name or fragment not in href:
            continue

        key = (href, name)
        if key in seen:
            continue
        seen.add(key)

        caturl = (
            href if href.startswith("http") else urllib_parse.urljoin(site.url, href)
        )
        site.add_dir(name, caturl, "List", "")
    utils.eod()


@site.register()
def Tag(url):
    _taxonomy(url, "tag/")


@site.register()
def Studios(url):
    _taxonomy(url, "studio/")


@site.register()
def Stars(url):
    _taxonomy(url, "stars/")


@site.register()
def Lookupinfo(url):
    class PerverzijaLookup(utils.LookupInfo):
        def url_constructor(self, url):
            if "studio/" in url:
                return url
            if any(x in url for x in ["stars/", "tag/"]):
                return site.url + url

    lookup_list = [
        ("Studio", 'href="([^"]+)" rel="category tag">([^<]+)', ""),
        ("Tag", '(tag/[^"]+)" rel="tag">([^<]+)', ""),
        ("Actor", '(stars/[^"]+)" rel="tag">([^<]+)', ""),
    ]

    lookupinfo = PerverzijaLookup(site.url, url, "perverzija.List", lookup_list)
    lookupinfo.getinfo()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, "Search")
    else:
        url = "{0}{1}".format(url, keyword.replace(" ", "%20"))
        List(url)


class _PlaybackError(Exception):
    pass


def _fresh_player_text(url, referer, api=False):
    headers = {
        "User-Agent": utils.USER_AGENT,
        "Accept-Encoding": "identity",
        "Cache-Control": "no-cache",
    }
    if api:
        headers["X-XS-P"] = "1"
    result = utils._getHtml(url, referer, headers=headers)
    return result.decode("utf-8") if isinstance(result, bytes) else result


def _xtremestream_hls(iframeurl, iframehtml):
    boot = re.search(
        r"""\bXSFTK\s*\.\s*boot\s*\(\s*['"]([^'"]+)['"]\s*,\s*['"]([^'"]+)['"]""",
        iframehtml,
    )
    if boot:
        video_id, video_token = boot.groups()
        api_url = urllib_parse.urljoin(iframeurl, "/player/proto_api.php")
        query = {"data": video_id, "vt": video_token, "op": "castsign"}
        cast_token = _fresh_player_text(
            api_url + "?" + urllib_parse.urlencode(query), iframeurl, api=True
        ).strip()
        if not re.fullmatch(r"[A-Za-z0-9_+./=-]{16,512}", cast_token):
            raise _PlaybackError("Unable to create the XtremeStream playback session")
        query.update(op="castmaster", ct=cast_token)
        playlist_url = api_url + "?" + urllib_parse.urlencode(query)
    else:
        video_id = re.search(
            r"""\bvar\s+video_id\s*=\s*[`'"]([^`'"]+)""", iframehtml, re.IGNORECASE
        )
        loader = re.search(
            r"""\bvar\s+m3u8_loader_url\s*=\s*[`'"]([^`'"]+)""",
            iframehtml,
            re.IGNORECASE,
        )
        if not video_id or not loader:
            raise _PlaybackError("Unsupported XtremeStream player layout")
        playlist_url = (
            urllib_parse.urljoin(iframeurl, loader.group(1)) + video_id.group(1)
        )

    playlist = _fresh_player_text(playlist_url, iframeurl)
    if not playlist.lstrip("\ufeff\r\n ").startswith("#EXTM3U"):
        raise _PlaybackError("XtremeStream did not return a playable HLS playlist")

    if re.search(r"^#EXT-X-MEDIA:.*TYPE=AUDIO", playlist, re.IGNORECASE | re.MULTILINE):
        return playlist_url

    links = {}
    stream_info = None
    for line in playlist.splitlines():
        line = line.strip()
        if line.upper().startswith("#EXT-X-STREAM-INF:"):
            stream_info = line
        elif line and not line.startswith("#") and stream_info:
            resolution = re.search(r"RESOLUTION=\d+x(\d+)", stream_info, re.IGNORECASE)
            if resolution:
                links[resolution.group(1)] = urllib_parse.urljoin(playlist_url, line)
            stream_info = None
    if links:
        return utils.prefquality(links, sort_by=lambda x: int(x), reverse=True)
    if "#EXTINF:" in playlist:
        return playlist_url
    raise _PlaybackError("No playable XtremeStream qualities found")


def _hls_play_url(url, referer):
    if urllib_parse.urlsplit(url).scheme not in ("http", "https") or any(
        c in url for c in "|\r\n"
    ):
        raise _PlaybackError("Invalid XtremeStream stream URL")
    if ".m3u8" not in url.lower():
        url += ("&" if "?" in url else "?") + "filename=stream.m3u8"
    headers = {"User-Agent": utils.USER_AGENT, "Referer": referer}
    return url + "|" + urllib_parse.urlencode(headers)


@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download=download, IA_check="skip")
    try:
        videohtml, _ = utils.get_html_with_cloudflare_retry(url)
        if not videohtml:
            utils.notify("Perverzija", "No video player found")
            return

        soup = utils.parse_html(videohtml)
        iframe = soup.select_one(".player-embed iframe[src], iframe[src]")
        if not iframe:
            utils.notify("Perverzija", "No video player found")
            return

        iframeurl = urllib_parse.urljoin(
            url, utils.safe_get_attr(iframe, "src").replace("&amp;", "&")
        )
        host = (urllib_parse.urlsplit(iframeurl).hostname or "").lower()
        if "xtremestream" in host:
            vp.progress.update(25, "[CR]Loading video page[CR]")
            iframehtml = _fresh_player_text(iframeurl, url)
            vp.progress.update(50, "[CR]Looking for qualities[CR]")
            videourl = _xtremestream_hls(iframeurl, iframehtml)
            vp.progress.update(75, "[CR]Loading selected quality[CR]")
            vp.IA_check = "IA"
            vp.play_from_direct_link(_hls_play_url(videourl, iframeurl))
        elif vp.resolveurl.HostedMediaFile(iframeurl).valid_url():
            vp.play_from_link_to_resolve(iframeurl)
        else:
            utils.notify("Perverzija", "This video host is not supported")
    except _PlaybackError as exc:
        utils.kodilog("Perverzija: " + str(exc))
        utils.notify("Perverzija", str(exc))
    except Exception as exc:
        utils.kodilog("Perverzija playback failed ({})".format(type(exc).__name__))
        utils.notify("Perverzija", "Could not load the video stream. Please retry.")
    finally:
        vp.progress.close()
