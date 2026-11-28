"""
Cumination
Copyright (C) 2016 Whitecream

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

import os.path
import sys
import socket
import importlib
import importlib.util
import six

from kodi_six import xbmc, xbmcplugin, xbmcvfs

from resources.lib import basics
from resources.lib.url_dispatcher import URL_Dispatcher
from resources.lib import utils
from resources.lib import favorites
from resources.lib import pin
from resources.lib.adultsite import AdultSite
from resources.lib.sites import *  # noqa

socket.setdefaulttimeout(60)

addon = basics.addon
addon_get_setting = addon.getSetting
content = "movies" if addon_get_setting("content") == "0" else "videos"
xbmcplugin.setContent(basics.addon_handle, content)
TRANSLATEPATH = xbmcvfs.translatePath if six.PY3 else xbmc.translatePath
progress = utils.progress
dialog = utils.dialog

url_dispatcher = URL_Dispatcher("main")

custom_site_import_results = {"loaded": [], "failed": []}


def _safe_child_path(base_dir, filename):
    base = os.path.realpath(TRANSLATEPATH(base_dir))
    # Normalize backslashes to forward slashes for cross-platform traversal protection
    filename = filename.replace("\\", "/")
    candidate = os.path.realpath(os.path.join(base, filename))
    if candidate != base and candidate.startswith(base + os.sep):
        return candidate
    raise ValueError("Path escapes expected directory")


def _record_custom_site_result(result_type, module_name, **details):
    custom_site_import_results[result_type].append({"module": module_name, **details})


def _handle_custom_site_failure(module_name, error, dependency=None):
    error_kind = "dependency" if dependency else "site"
    title = favorites.get_custom_site_title_by_module(module_name)
    readable_title = title or module_name
    utils.kodilog(
        "Custom site import failed [{0}] {1}: {2}".format(
            error_kind, module_name, error
        ),
        xbmc.LOGERROR,
    )
    favorites.disable_custom_site_by_module(module_name)
    message_lines = [
        "[B]{0}[/B]".format(readable_title),
        utils.i18n("custom_msg"),
    ]
    if dependency:
        message_lines.append(
            "Missing dependency: [COLOR red]{0}[/COLOR]".format(dependency)
        )
    else:
        message_lines.append("Import error detected inside the site module.")
    message_lines.append(
        "The site has been disabled; reinstall or fix the issue to re-enable it."
    )
    utils.textBox(utils.i18n("disable_custom"), "[CR]".join(message_lines))
    _record_custom_site_result(
        "failed",
        module_name,
        title=title,
        error=str(error),
        dependency=dependency,
        error_kind=error_kind,
    )


def _import_custom_site(module_name, safe_base):
    """Import a single custom site module using an explicit file path.

    Avoids adding the custom-sites directory to sys.path (which would let any
    module in that directory be imported by name from elsewhere).  Instead we
    resolve the full path, verify it stays within the allowed directory, and
    load the module directly via importlib machinery.
    """
    candidate = os.path.realpath(
        os.path.join(safe_base, module_name + ".py")
    )
    if not candidate.startswith(safe_base + os.sep):
        raise ImportError(
            "Rejected custom site '{}': path outside customSitesDir".format(module_name)
        )
    if not os.path.isfile(candidate):
        raise ImportError(
            "Custom site module not found: {}".format(candidate)
        )
    spec = importlib.util.spec_from_file_location(module_name, candidate)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)


def load_custom_sites():
    custom_site_import_results["loaded"].clear()
    custom_site_import_results["failed"].clear()
    if addon_get_setting("custom_sites") != "true":
        return custom_site_import_results

    safe_base = os.path.realpath(basics.customSitesDir)
    for module_name in favorites.enabled_custom_sites():
        try:
            _import_custom_site(module_name, safe_base)
        except ImportError as error:
            dependency = getattr(error, "name", None)
            missing_dependency = (
                dependency if dependency and dependency != module_name else None
            )
            _handle_custom_site_failure(
                module_name, error, dependency=missing_dependency
            )
        except Exception as error:
            _handle_custom_site_failure(module_name, error)
        else:
            _record_custom_site_result("loaded", module_name)
    return custom_site_import_results


# load_custom_sites() moved to __main__ block for testability


@url_dispatcher.register()
def custom_sites_health():
    enabled_sites = favorites.enabled_custom_sites()
    if not enabled_sites:
        utils.textBox("Custom site health", "No custom sites are enabled.")
        return

    loaded_sites_data = custom_site_import_results.get("loaded", [])
    failed_sites = custom_site_import_results.get("failed", [])
    loaded_modules = {site["module"] for site in loaded_sites_data}
    failed_modules = {failure["module"] for failure in failed_sites}
    message_lines = []

    if loaded_modules:
        message_lines.append("[B]Loaded custom sites[/B]")
        for module_name in sorted(loaded_modules):
            title = (
                favorites.get_custom_site_title_by_module(module_name) or module_name
            )
            message_lines.append("• {0}".format(title))

    if failed_sites:
        message_lines.append("[B]Failed to load[/B]")
        for failure in sorted(failed_sites, key=lambda x: x["module"]):
            title = failure.get("title") or favorites.get_custom_site_title_by_module(
                failure["module"]
            )
            descriptor = (
                failure["dependency"] if failure.get("dependency") else "import error"
            )
            message_lines.append(
                "• {0} ({1})".format(title or failure["module"], descriptor)
            )

    untouched = sorted(
        [
            m
            for m in enabled_sites
            if m not in loaded_modules and m not in failed_modules
        ]
    )
    if untouched:
        message_lines.append("[B]Not attempted[/B]")
        for module_name in untouched:
            title = (
                favorites.get_custom_site_title_by_module(module_name) or module_name
            )
            message_lines.append("• {0}".format(title))

    if not message_lines:
        message_lines.append("No custom site import activity recorded.")

    utils.textBox("Custom site health", "[CR]".join(message_lines))


@url_dispatcher.register()
def INDEX():
    url_dispatcher.add_dir(
        "[COLOR white]{}[/COLOR]".format(utils.i18n("sites")),
        "",
        "site_list",
        basics.cum_image("cum-sites.png"),
        "",
        list_avail=False,
    )
    url_dispatcher.add_dir(
        "[COLOR white]Browse by Category[/COLOR]",
        "",
        "category_list",
        basics.cum_image("cum-sites.png"),
        "",
        list_avail=False,
    )
    url_dispatcher.add_dir(
        "[COLOR hotpink]Global Search[/COLOR]",
        "",
        "global_search_menu",
        basics.cum_image("cum-search.png"),
        "",
        list_avail=False,
    )
    url_dispatcher.add_dir(
        "[COLOR white]Site Health Status[/COLOR]",
        "",
        "site_health_status",
        basics.cum_image("cum-sites.png"),
        "",
        list_avail=False,
    )
    if any(x.is_new for x in AdultSite.get_sites()):
        url_dispatcher.add_dir(
            "[COLOR green]New Sites[/COLOR]",
            "",
            "new_site_list",
            basics.cum_image("cum-sites.png"),
            "",
            list_avail=False,
        )
    if any(AdultSite.get_testing_sites()):
        url_dispatcher.add_dir(
            "[COLOR white]Testing Sites[/COLOR]",
            "",
            "testing_site_list",
            basics.cum_image("cum-sites.png"),
            "",
            list_avail=False,
        )
    url_dispatcher.add_dir(
        "[COLOR white]{}[/COLOR]".format(utils.i18n("fav_videos")),
        "1",
        "favorites.List",
        basics.cum_image("cum-fav.png"),
        "",
        list_avail=False,
    )
    download_path = addon_get_setting("download_path")
    if download_path != "" and xbmcvfs.exists(download_path):
        url_dispatcher.add_dir(
            "[COLOR white]{}[/COLOR]".format(utils.i18n("dnld_folder")),
            "",
            "OpenDownloadFolder",
            basics.cum_image("cum-downloads.png"),
            "",
            list_avail=False,
        )

    url_dispatcher.add_dir(
        "[COLOR white]{}[/COLOR]".format(utils.i18n("custom_list")),
        "",
        "favorites.create_custom_list",
        Folder=False,
        list_avail=False,
    )
    if addon_get_setting("custom_sites") == "true":
        url_dispatcher.add_dir(
            "[COLOR white]Custom site health[/COLOR]",
            "",
            "custom_sites_health",
            basics.cum_image("cum-sites.png"),
            "",
            list_avail=False,
        )
    for rowid, name in favorites.get_custom_lists():
        url_dispatcher.add_dir(
            name,
            str(rowid),
            "favorites.load_custom_list",
            list_avail=False,
            custom_list=True,
        )
    favorites.load_custom_list("main")
    url_dispatcher.add_dir(
        "[COLOR white]{}[/COLOR]".format(utils.i18n("clear_cache")),
        "",
        "utils.clear_cache",
        basics.cuminationicon,
        "",
        Folder=False,
        list_avail=False,
    )

    utils.eod(basics.addon_handle, False)


_CATEGORY_ICONS = {
    "Video Tubes":      basics.site_image("pornhub.png"),
    "Cams & Live":      basics.site_image("chaturbate.png"),
    "JAV & Asian":      basics.site_image("javmoe.png"),
    "Hentai & Anime":   basics.site_image("hanime.png"),
    "Amateur & Social": basics.site_image("erome.png"),
    "Specialty":        basics.site_image("trannyteca.png"),
    "Aggregators":      basics.site_image("archivebate.png"),
}


def _site_health_map():
    show_badges = addon_get_setting("show_site_status_badges") == "true"
    hide_broken = addon_get_setting("hide_broken_sites") == "true"
    if not show_badges and not hide_broken:
        return {}
    try:
        from resources.lib import site_status

        return site_status.get_site_statuses()
    except Exception:
        return {}


def _visible_sites(sites, status_map=None):
    if addon_get_setting("hide_broken_sites") != "true" or not status_map:
        return list(sites)
    return [
        s for s in sites if (status_map.get(s.name) or {}).get("status") != "broken"
    ]


def _site_display_title(site_obj, custom_listitems_dict=None, status_map=None):
    title = site_obj.title
    if site_obj.is_new:
        title = "[COLOR lime][NEW][/COLOR] {}".format(title)
    if hasattr(site_obj, "requires_flaresolverr") and site_obj.requires_flaresolverr:
        title = "{} [COLOR orange][FS][/COLOR]".format(title)
    if (
        addon_get_setting("show_site_status_badges") == "true"
        and status_map
        and site_obj.name in status_map
    ):
        st = status_map[site_obj.name].get("status")
        if st == "healthy":
            title = "{} [COLOR lime][OK][/COLOR]".format(title)
        elif st == "blocked":
            title = "{} [COLOR orange][BLOCKED][/COLOR]".format(title)
        elif st == "broken":
            title = "{} [COLOR red][BROKEN][/COLOR]".format(title)
    if custom_listitems_dict and site_obj.title in custom_listitems_dict:
        title = "{} [COLOR red]{}[/COLOR]".format(
            title, "".ljust(custom_listitems_dict[site_obj.title], "*")
        )
    return title


@url_dispatcher.register()
def category_list():
    categories = set()
    for x in AdultSite.get_sites():
        if x.category:
            categories.add(x.category)

    for cat in sorted(categories):
        icon = _CATEGORY_ICONS.get(cat, basics.cum_image("cum-sites.png"))
        url_dispatcher.add_dir(
            "[COLOR white]{}[/COLOR]".format(cat),
            cat,
            "browse_category",
            icon,
            "",
            list_avail=False,
        )

    utils.eod(basics.addon_handle, False)


@url_dispatcher.register()
def browse_category(url):
    category = url
    custom_listitems = favorites.get_custom_listitems()
    custom_listitems_dict = {x[0]: x[1] for x in custom_listitems}
    
    sites = list(AdultSite.get_sites())
    filtered_sites = []
    
    for x in sites:
        if category == "None":
            if not x.category:
                filtered_sites.append(x)
        elif x.category == category:
            filtered_sites.append(x)
            
    status_map = _site_health_map()
    for x in sorted(_visible_sites(filtered_sites, status_map), key=lambda y: y.get_clean_title().lower()):
        title = _site_display_title(x, custom_listitems_dict, status_map)
        url_dispatcher.add_dir(
            title, x.url, x.default_mode, x.image, about=x.about, custom=x.custom
        )
    utils.eod(basics.addon_handle, False)


@url_dispatcher.register()
def site_list():
    custom_listitems = favorites.get_custom_listitems()
    custom_listitems_dict = {}
    for x in custom_listitems:
        custom_listitems_dict[x[0]] = x[1]
    status_map = _site_health_map()
    for x in sorted(
        _visible_sites(AdultSite.get_sites(), status_map),
        key=lambda y: y.get_clean_title().lower(),
        reverse=False,
    ):
        if x.custom:
            utils.kodilog(
                "{0}: {1}".format(utils.i18n("list_custom"), x.title), xbmc.LOGDEBUG
            )
        title = _site_display_title(x, custom_listitems_dict, status_map)
        url_dispatcher.add_dir(
            title, x.url, x.default_mode, x.image, about=x.about, custom=x.custom
        )
    utils.eod(basics.addon_handle, False)


@url_dispatcher.register()
def new_site_list():
    custom_listitems = favorites.get_custom_listitems()
    custom_listitems_dict = {x[0]: x[1] for x in custom_listitems}
    
    status_map = _site_health_map()
    new_sites = _visible_sites(
        [x for x in AdultSite.get_sites() if x.is_new], status_map
    )

    for x in sorted(new_sites, key=lambda y: y.get_clean_title().lower()):
        title = _site_display_title(x, custom_listitems_dict, status_map)
        url_dispatcher.add_dir(
            title, x.url, x.default_mode, x.image, about=x.about, custom=x.custom
        )
    utils.eod(basics.addon_handle, False)


@url_dispatcher.register()
def testing_site_list():
    for x in sorted(
        AdultSite.get_testing_sites(),
        key=lambda y: y.get_clean_title().lower(),
        reverse=False,
    ):
        url_dispatcher.add_dir(
            "[COLOR gold][TEST][/COLOR] {}".format(x.title),
            x.url,
            x.default_mode,
            x.image,
            about=x.about,
            custom=x.custom,
        )
    utils.eod(basics.addon_handle, False)


@url_dispatcher.register()
def OpenDownloadFolder():
    xbmc.executebuiltin("Dialog.Close(busydialog, true)")
    xbmc.sleep(100)
    download_path = addon_get_setting("download_path")
    if download_path:
        safe_url = download_path.replace('"', "").replace(",", "").replace(")", "")
        xbmc.executebuiltin('ActivateWindow(Videos, "{}")'.format(safe_url))
    else:
        utils.notify(utils.i18n("oh_oh"), utils.i18n("dnld_path"))


@url_dispatcher.register()
def smrSettings():
    import resolveurl

    resolveurl.display_settings()


@url_dispatcher.register()
def openLogUploader():
    from resources.lib.jsonrpc import check_addon

    if check_addon("script.kodi.loguploader"):
        xbmc.executebuiltin("RunScript(script.kodi.loguploader)")
    else:
        dialog.ok(
            "Kodi Logfile Uploader",
            "Installing Kodi Logfile Uploader unsuccesful\nPlease install it manually from the Kodi repository",
        )


@url_dispatcher.register()
def about_site(name, about, custom):
    heading = "{0} {1}".format(utils.i18n("about"), name)
    dir = basics.customSitesDir if custom else basics.aboutDir
    about_name = os.path.basename(str(about))
    if about_name != about or about_name in ("", ".", ".."):
        utils.notify(utils.i18n("oh_oh"), "Invalid about file")
        return
    try:
        about_path = _safe_child_path(dir, "{}.txt".format(about_name))
    except ValueError:
        utils.notify(utils.i18n("oh_oh"), "Invalid about file")
        return
    with open(about_path) as f:
        announce = f.read()
    utils.textBox(heading, announce)


def change():
    version = addon.getAddonInfo("version")
    if addon_get_setting("changelog_seen_version") == version or not os.path.isfile(
        basics.changelog
    ):
        return
    addon.setSetting("changelog_seen_version", version)
    heading = "[B][COLOR hotpink]Cumination[/COLOR] [COLOR white]Changelog[/COLOR][/B]"
    with open(basics.changelog) as f:
        cl_lines = f.readlines()
    announce = ""
    for line in cl_lines:
        if not line.strip():
            break
        announce += line
    utils.textBox(heading, announce)


@url_dispatcher.register()
def global_search_menu():
    url_dispatcher.add_dir(
        "[COLOR hotpink]Search All Sites[/COLOR]",
        "",
        "global_search",
        basics.cum_image("cum-search.png"),
        "",
        list_avail=False,
    )
    categories = sorted(
        {x.category for x in AdultSite.get_sites() if x.category}
    )
    for cat in categories:
        icon = _CATEGORY_ICONS.get(cat, basics.cum_image("cum-search.png"))
        url_dispatcher.add_dir(
            "[COLOR white]Search {}[/COLOR]".format(cat),
            cat,
            "global_search",
            icon,
            "",
            list_avail=False,
        )
    utils.eod(basics.addon_handle, False)


@url_dispatcher.register()
def global_search(url=""):
    from resources.lib import global_search as gs

    keyword = utils._get_keyboard(heading="Global Search")
    if not keyword:
        utils.eod(basics.addon_handle, False)
        return

    category = url or None
    results = gs.search_sites(keyword, category=category)
    if not results:
        utils.notify("Global Search", "No results found for '{}'".format(keyword))
        utils.eod(basics.addon_handle, False)
        return

    for item in results:
        label = "[COLOR hotpink][{}][/COLOR] {}".format(
            item["site_title"], item["name"]
        )
        url_dispatcher.add_download_link(
            label,
            item["url"],
            item["mode"],
            item["iconimage"],
            item.get("desc", ""),
            stream=item.get("stream"),
            fav=item.get("fav", "add"),
            noDownload=item.get("noDownload", False),
            contextm=item.get("contextm"),
            fanart=item.get("fanart"),
            duration=item.get("duration", ""),
            quality=item.get("quality", ""),
        )
    utils.eod(basics.addon_handle)


@url_dispatcher.register()
def site_health_status(url=""):
    from resources.lib import site_status

    force = url == "refresh"
    status_map = site_status.get_site_statuses(force_refresh=force)
    if not status_map:
        utils.notify("Site Health", "Could not load nightly site health status")
        utils.eod(basics.addon_handle, False)
        return

    url_dispatcher.add_dir(
        "[COLOR cyan]Refresh Status[/COLOR]",
        "refresh",
        "site_health_status",
        basics.cum_image("cum-sites.png"),
        "",
        list_avail=False,
    )
    sites_by_name = {s.name: s for s in AdultSite.get_sites()}
    order = {"broken": 0, "blocked": 1, "healthy": 2, "unknown": 3}
    for name in sorted(
        status_map.keys(),
        key=lambda n: (order.get(status_map[n].get("status", "unknown"), 3), n),
    ):
        site_obj = sites_by_name.get(name)
        if not site_obj:
            continue
        info = status_map[name]
        st = info.get("status", "unknown")
        if st == "healthy":
            badge = "[COLOR lime][OK][/COLOR]"
        elif st == "blocked":
            badge = "[COLOR orange][BLOCKED][/COLOR]"
        elif st == "broken":
            badge = "[COLOR red][BROKEN][/COLOR]"
        else:
            badge = "[COLOR gray][?][/COLOR]"
        label = "{} {}".format(badge, site_obj.get_clean_title() or site_obj.title)
        url_dispatcher.add_dir(
            label,
            site_obj.url,
            site_obj.default_mode,
            site_obj.image,
            about=site_obj.about,
            custom=site_obj.custom,
        )
    utils.eod(basics.addon_handle, False)


@url_dispatcher.register()
def test_flaresolverr():
    import time
    from urllib.parse import urlparse
    import requests
    from resources.lib import flaresolverr

    fs_host = (addon_get_setting("fs_host") or "http://127.0.0.1:8191/v1").strip()
    try:
        flaresolverr._validate_flaresolverr_url(fs_host)
    except ValueError as exc:
        dialog.ok(
            "FlareSolverr Connection Test",
            "Invalid FlareSolverr URL:\n{}".format(exc),
        )
        return

    parsed = urlparse(fs_host)
    health_url = "{}://{}/health".format(parsed.scheme, parsed.netloc)
    start = time.time()
    try:
        resp = requests.get(health_url, timeout=8)
        if resp.status_code == 404:
            resp = requests.post(fs_host, json={"cmd": "sessions.list"}, timeout=8)
        elapsed_ms = int((time.time() - start) * 1000)
        if resp.status_code == 200:
            dialog.ok(
                "FlareSolverr Connection Test",
                "Connected successfully!\nEndpoint: {}\nLatency: {} ms".format(
                    fs_host, elapsed_ms
                ),
            )
        else:
            dialog.ok(
                "FlareSolverr Connection Test",
                "Unexpected HTTP {} from {}".format(resp.status_code, fs_host),
            )
    except Exception as exc:
        dialog.ok(
            "FlareSolverr Connection Test",
            "Connection failed:\n{}\n{}".format(fs_host, exc),
        )


@url_dispatcher.register()
def test_doh():
    import time
    from resources.lib import doh

    providers = ["cloudflare", "google", "quad9"]
    try:
        idx = int(addon_get_setting("doh_provider") or "0")
    except ValueError:
        idx = 0
    provider = providers[idx] if 0 <= idx < len(providers) else "cloudflare"
    doh._DOH_CACHE.pop("example.com", None)
    start = time.time()
    ip = doh.resolve_doh("example.com", provider=provider, timeout=6.0)
    elapsed_ms = int((time.time() - start) * 1000)
    if ip:
        dialog.ok(
            "DoH Connection Test",
            "Resolved example.com -> {}\nProvider: {}\nLatency: {} ms".format(
                ip, provider, elapsed_ms
            ),
        )
    else:
        dialog.ok(
            "DoH Connection Test",
            "Failed to resolve example.com using provider '{}'".format(provider),
        )


@url_dispatcher.register()
def send_test_report():
    from resources.lib import telemetry
    reporter = telemetry.get_reporter()
    if not reporter.enabled():
        dialog.ok("Diagnostic Telemetry", "Diagnostic reporting is disabled in settings.")
        return

    result = reporter.send_test_report()
    if result.ok:
        dialog.ok("Diagnostic Telemetry", "Test report accepted by GlitchTip!\nEvent ID: {}".format(result.event_id))
    else:
        dialog.ok("Diagnostic Telemetry", "Failed to send test report:\n{}".format(result.message))


def main(argv=None):
    if argv is None:
        argv = sys.argv
    query = argv[2] if len(argv) > 2 else ""
    queries = utils.parse_query(query)
    mode = queries.get("mode", None)
    from resources.lib import telemetry
    reporter = telemetry.get_reporter()
    with reporter.operation_scope(mode, queries):
        url_dispatcher.dispatch(mode, queries)


if __name__ == "__main__":
    if not addon_get_setting("cuminationage") == "true":
        age = dialog.yesno(
            utils.i18n("warn"),
            utils.i18n("warn_msg"),
            nolabel=utils.i18n("exit"),
            yeslabel=utils.i18n("enter"),
        )
        if age:
            addon.setSetting("cuminationage", "true")
    else:
        age = True

    if age and pin.CheckPin():
        load_custom_sites()
        change()
        sys.exit(main())
