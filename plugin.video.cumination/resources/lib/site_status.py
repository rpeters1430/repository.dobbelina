"""Live site health status loader and cache for Cumination."""

from __future__ import annotations

import json
import os
import time

import requests

from resources.lib import basics

STRICT_HEALTH_URL = (
    "https://raw.githubusercontent.com/rpeters1430/repository.dobbelina/"
    "site-health/strict_health_latest.json"
)
BROAD_HEALTH_URL = (
    "https://raw.githubusercontent.com/rpeters1430/repository.dobbelina/"
    "site-health/live_smoke_latest.json"
)
CACHE_TTL_SECONDS = 6 * 3600


def _cache_path():
    base = getattr(basics, "tempDir", "") or ""
    if not base:
        return ""
    return os.path.join(base, "site_health_cache.json")


def normalize_status(strict_state=None, broad_overall=None):
    """Map strict/broad health states to 'healthy', 'blocked', 'broken', or 'unknown'."""
    if strict_state:
        s = str(strict_state).upper()
        if s == "HEALTHY":
            return "healthy"
        if s == "BLOCKED":
            return "blocked"
        if s in ("BROKEN", "HARNESS_ERROR"):
            return "broken"

    if broad_overall:
        b = str(broad_overall).upper()
        if b in ("PASS", "WARN"):
            return "healthy"
        if b == "FAIL":
            return "broken"
    return "unknown"


def _parse_reports(strict_data, broad_data):
    statuses = {}
    if isinstance(broad_data, dict):
        for entry in broad_data.get("sites", []):
            site_name = entry.get("site")
            if site_name:
                statuses[site_name] = {
                    "status": normalize_status(broad_overall=entry.get("overall")),
                    "source": "broad",
                    "detail": entry.get("overall", ""),
                }
    if isinstance(strict_data, dict):
        for site_name, entry in strict_data.get("sites", {}).items():
            raw_state = str(entry.get("state", "")).replace("HealthState.", "")
            statuses[site_name] = {
                "status": normalize_status(strict_state=raw_state),
                "source": "strict",
                "detail": entry.get("message") or raw_state,
            }
    return statuses


def get_site_statuses(force_refresh=False, timeout=8):
    """Return {site_name: {'status': ..., 'source': ..., 'detail': ...}} with local cache."""
    cache_file = _cache_path()
    if not force_refresh and cache_file and os.path.isfile(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as fh:
                cached = json.load(fh)
            if time.time() - cached.get("fetched_at", 0) < CACHE_TTL_SECONDS:
                return cached.get("sites", {})
        except Exception:
            pass

    strict_data = None
    broad_data = None
    try:
        resp = requests.get(STRICT_HEALTH_URL, timeout=timeout)
        if resp.status_code == 200:
            strict_data = resp.json()
    except Exception:
        pass

    try:
        resp = requests.get(BROAD_HEALTH_URL, timeout=timeout)
        if resp.status_code == 200:
            broad_data = resp.json()
    except Exception:
        pass

    statuses = _parse_reports(strict_data, broad_data)
    if statuses and cache_file:
        try:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as fh:
                json.dump({"fetched_at": time.time(), "sites": statuses}, fh)
        except Exception:
            pass
    return statuses
