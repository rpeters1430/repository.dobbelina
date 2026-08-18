"""
Dynamic Mirror Manager for Kodi Cumination.
Maintains known fallback mirrors and supports dynamic domain failover.
"""

from __future__ import annotations

import json
import os
from six.moves import urllib_parse, urllib_request
import ssl

from resources.lib import basics

DEFAULT_MIRRORS: dict[str, list[str]] = {
    "thothub": [
        "https://thothub.to/",
        "https://thothub.lol/",
        "https://thothub.is/",
        "https://thothub.vip/",
    ],
    "camwhorestv": [
        "https://www.camwhoresbay.com/",
        "https://www.camwhores.tv/",
    ],
    "pornditt": [
        "https://v.pornditt.com/",
    ],
    "notfans": [
        "https://notfans.com/",
    ],
    "cloudbate": [
        "https://www.cloudbate.com/",
    ],
    "hornyfap": [
        "https://hornyfap.tv/",
    ],
    "webpussi": [
        "https://www.webpussi.com/",
    ],
    "xhamster": [
        "https://xhamster.com/",
        "https://xhamster.desi/",
    ],
}

_ACTIVE_MIRRORS_CACHE: dict[str, str] = {}
_CACHE_FILE_NAME = "mirrors_cache.json"


def _get_cache_path() -> str:
    profile = basics.profile if hasattr(basics, "profile") and basics.profile else ""
    if not profile:
        try:
            profile = basics.addon.getAddonInfo("profile")
        except Exception:
            profile = ""
    if profile:
        return os.path.join(profile, _CACHE_FILE_NAME)
    return ""


def _load_cache() -> dict[str, str]:
    global _ACTIVE_MIRRORS_CACHE
    if _ACTIVE_MIRRORS_CACHE:
        return _ACTIVE_MIRRORS_CACHE

    cache_path = _get_cache_path()
    if cache_path and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    _ACTIVE_MIRRORS_CACHE = data
                    return _ACTIVE_MIRRORS_CACHE
        except Exception:
            pass

    return _ACTIVE_MIRRORS_CACHE


def _save_cache() -> None:
    cache_path = _get_cache_path()
    if cache_path:
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(_ACTIVE_MIRRORS_CACHE, f, indent=2)
        except Exception:
            pass


def get_mirrors(site_name: str) -> list[str]:
    """Return all known mirrors for a given site."""
    return DEFAULT_MIRRORS.get(site_name.lower(), [])


def get_site_url(site_name: str, default_url: str) -> str:
    """Return the active mirror URL for a given site."""
    cache = _load_cache()
    cached_url = cache.get(site_name.lower())
    if cached_url:
        return cached_url

    mirrors = get_mirrors(site_name)
    if mirrors:
        return mirrors[0]

    return default_url


def set_active_mirror(site_name: str, active_url: str) -> None:
    """Set and persist the active mirror URL for a given site."""
    if not site_name or not active_url:
        return
    _load_cache()
    _ACTIVE_MIRRORS_CACHE[site_name.lower()] = active_url
    _save_cache()


def report_failure(site_name: str, failed_url: str) -> str | None:
    """Report that a mirror failed and automatically switch to the next available mirror."""
    mirrors = get_mirrors(site_name)
    if not mirrors or len(mirrors) <= 1:
        return None

    failed_netloc = urllib_parse.urlsplit(failed_url).netloc.lower()
    available = [m for m in mirrors if urllib_parse.urlsplit(m).netloc.lower() != failed_netloc]

    if available:
        next_mirror = available[0]
        set_active_mirror(site_name, next_mirror)
        return next_mirror

    return None


def probe_mirror(url: str, timeout: float = 4.0) -> bool:
    """Quickly probe if a mirror URL is reachable and returning success/redirect."""
    if not url:
        return False
    try:
        ctx = ssl.create_default_context()
        req = urllib_request.Request(
            url,
            headers={
                "User-Agent": basics.USER_AGENT if hasattr(basics, "USER_AGENT") else "Mozilla/5.0",
                "Accept": "*/*",
            },
        )
        resp = urllib_request.urlopen(req, timeout=timeout, context=ctx)
        try:
            status = getattr(resp, "status", getattr(resp, "code", 200))
            return status in (200, 301, 302, 307, 308)
        finally:
            if hasattr(resp, "close"):
                resp.close()
    except Exception:
        return False


def clear_mirrors_cache() -> None:
    """Clear all cached mirror selections."""
    global _ACTIVE_MIRRORS_CACHE
    _ACTIVE_MIRRORS_CACHE.clear()
    cache_path = _get_cache_path()
    if cache_path and os.path.exists(cache_path):
        try:
            os.remove(cache_path)
        except Exception:
            pass
