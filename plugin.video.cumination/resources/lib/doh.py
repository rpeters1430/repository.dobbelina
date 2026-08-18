"""
DNS-over-HTTPS (DoH) resolver for Kodi Cumination.
Bypasses ISP DNS blocking and censorship by resolving domain names
over encrypted HTTPS channels (Cloudflare, Google, Quad9).
"""

from __future__ import annotations

import json
import time
from six.moves import urllib_parse, urllib_request
import ssl

DOH_PROVIDERS = {
    "cloudflare": "https://cloudflare-dns.com/dns-query",
    "google": "https://dns.google/resolve",
    "quad9": "https://dns.quad9.net/dns-query",
}

_DOH_CACHE: dict[str, tuple[str, float]] = {}  # {hostname: (ip, expiry_timestamp)}
_CACHE_TTL = 3600.0  # 1 hour default TTL


def resolve_doh(hostname: str, provider: str = "cloudflare", timeout: float = 5.0) -> str | None:
    """Resolve a hostname to IPv4 address via DNS-over-HTTPS.

    Returns the IPv4 string if successful, or None if resolution fails.
    """
    if not hostname:
        return None

    # Check cache first
    now = time.time()
    cached = _DOH_CACHE.get(hostname)
    if cached:
        ip, expiry = cached
        if now < expiry:
            return ip
        else:
            _DOH_CACHE.pop(hostname, None)

    endpoint = DOH_PROVIDERS.get(provider.lower()) or DOH_PROVIDERS["cloudflare"]
    params = urllib_parse.urlencode({"name": hostname, "type": "A"})
    req_url = f"{endpoint}?{params}"

    headers = {
        "Accept": "application/dns-json",
        "User-Agent": "Cumination-DoH/1.0",
    }

    try:
        ctx = ssl.create_default_context()
        req = urllib_request.Request(req_url, headers=headers)
        resp = urllib_request.urlopen(req, timeout=timeout, context=ctx)
        try:
            content = resp.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            data = json.loads(content)
            answers = data.get("Answer") or []
            for ans in answers:
                if ans.get("type") == 1:  # Type 1 is A record (IPv4)
                    ip = ans.get("data")
                    ttl = float(ans.get("TTL", 300))
                    if ip:
                        _DOH_CACHE[hostname] = (ip, now + min(ttl, _CACHE_TTL))
                        return ip
        finally:
            if hasattr(resp, "close"):
                resp.close()
    except Exception:
        pass

    return None


def clear_doh_cache() -> None:
    """Clear in-memory DoH resolution cache."""
    _DOH_CACHE.clear()
