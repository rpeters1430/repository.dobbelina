"""Global multi-site search for Cumination."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import inspect
import threading

from resources.lib import url_dispatcher as ud
from resources.lib import utils
from resources.lib.adultsite import AdultSite
from resources.lib.url_dispatcher import URL_Dispatcher

_LOCAL = threading.local()


def _site_search_url(site_obj):
    base = site_obj.url.rstrip("/") + "/"
    name = (getattr(site_obj, "name", "") or "").lower()
    if name in ("pornxpert", "hentaihaven"):
        return base + "search/"
    return base + "?s="


def find_searchable_sites(category=None):
    """Return sorted AdultSite instances that expose a Search mode."""
    sites = []
    for site_obj in AdultSite.get_sites():
        if category and site_obj.category != category:
            continue
        mode_key = "{}.Search".format(site_obj.module_name)
        if mode_key in URL_Dispatcher.func_registry:
            sites.append(site_obj)
    return sorted(sites, key=lambda s: s.get_clean_title().lower())


def _call_site_search(site_obj, keyword, per_site_limit=10):
    mode_key = "{}.Search".format(site_obj.module_name)
    func = URL_Dispatcher.func_registry.get(mode_key)
    if func is None:
        return []

    sig = inspect.signature(func)
    if "keyword" not in sig.parameters:
        return []

    _LOCAL.capture = []
    _LOCAL.limit = per_site_limit
    try:
        func(_site_search_url(site_obj), keyword=keyword)
        return list(_LOCAL.capture)
    except Exception:
        return []
    finally:
        _LOCAL.capture = None


def search_sites(
    keyword,
    category=None,
    max_workers=8,
    per_site_limit=10,
    max_results=120,
    sites=None,
):
    """Search multiple sites in parallel and return normalized video items."""
    query = (keyword or "").strip()
    if not query:
        return []

    targets = list(sites) if sites is not None else find_searchable_sites(category=category)
    if not targets:
        return []

    orig_add_down = ud.addDownLink
    orig_add_dir = ud.addDir
    orig_eod = utils.eod

    def _capturing_add_down(
        name,
        url,
        mode,
        iconimage,
        desc="",
        stream=None,
        fav="add",
        noDownload=False,
        contextm=None,
        fanart=None,
        duration="",
        quality="",
    ):
        buf = getattr(_LOCAL, "capture", None)
        if buf is None:
            return orig_add_down(
                name,
                url,
                mode,
                iconimage,
                desc,
                stream,
                fav,
                noDownload,
                contextm,
                fanart,
                duration,
                quality,
            )
        if len(buf) < getattr(_LOCAL, "limit", per_site_limit):
            buf.append(
                {
                    "name": name,
                    "url": url,
                    "mode": mode,
                    "iconimage": iconimage,
                    "desc": desc,
                    "stream": stream,
                    "fav": fav,
                    "noDownload": noDownload,
                    "contextm": contextm,
                    "fanart": fanart,
                    "duration": duration,
                    "quality": quality,
                }
            )
        return None

    def _capturing_add_dir(*args, **kwargs):
        if getattr(_LOCAL, "capture", None) is not None:
            return None
        return orig_add_dir(*args, **kwargs)

    def _capturing_eod(*args, **kwargs):
        if getattr(_LOCAL, "capture", None) is not None:
            return None
        return orig_eod(*args, **kwargs)

    ud.addDownLink = _capturing_add_down
    ud.addDir = _capturing_add_dir
    utils.eod = _capturing_eod

    results = []
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            future_map = {
                pool.submit(_call_site_search, site_obj, query, per_site_limit): site_obj
                for site_obj in targets
            }
            for fut in as_completed(future_map):
                site_obj = future_map[fut]
                site_label = site_obj.get_clean_title() or site_obj.name
                try:
                    items = fut.result()
                except Exception:
                    items = []
                for item in items:
                    item["site_name"] = site_obj.name
                    item["site_title"] = site_label
                    results.append(item)
                    if len(results) >= max_results:
                        return results
    finally:
        ud.addDownLink = orig_add_down
        ud.addDir = orig_add_dir
        utils.eod = orig_eod

    return results
