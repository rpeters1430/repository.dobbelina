"""
yt-dlp Resolver Bridge for Kodi Cumination.
Provides fallback video stream extraction via yt-dlp when ResolveURL / internal parsers fail.
Works with script.module.yt-dlp or system yt_dlp package.
"""

from __future__ import annotations

from six.moves import urllib_parse


def _get_ydl_class():
    """Dynamically get the YoutubeDL class if available."""
    try:
        import yt_dlp
        return getattr(yt_dlp, "YoutubeDL", None)
    except Exception:
        try:
            from yt_dlp import YoutubeDL
            return YoutubeDL
        except Exception:
            return None


def is_available() -> bool:
    """Return True if yt-dlp is available in the current environment."""
    return _get_ydl_class() is not None


def resolve_url(url: str, custom_headers: dict | None = None) -> str | None:
    """Extract direct playable stream URL from a page URL using yt-dlp."""
    ydl_class = _get_ydl_class()
    if not ydl_class or not url:
        return None

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "nocheckcertificate": True,
    }

    if custom_headers:
        ydl_opts["http_headers"] = custom_headers

    try:
        with ydl_class(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None

            stream_url = None
            # Extract URL from direct info or best format
            if "url" in info and info["url"]:
                stream_url = info["url"]
            elif "formats" in info and info["formats"]:
                # Prefer highest quality format with video+audio or highest resolution
                formats = [f for f in info["formats"] if f.get("url")]
                if formats:
                    # Pick the last (usually highest quality) format
                    stream_url = formats[-1].get("url")

            if not stream_url:
                return None

            # Append http_headers if present for Kodi player
            headers = info.get("http_headers") or {}
            header_parts = []
            if "User-Agent" in headers:
                header_parts.append("User-Agent=" + urllib_parse.quote(headers["User-Agent"], safe=""))
            if "Referer" in headers:
                header_parts.append("Referer=" + urllib_parse.quote(headers["Referer"], safe=""))

            if header_parts and "|" not in stream_url:
                stream_url += "|" + "&".join(header_parts)

            return stream_url

    except Exception:
        return None
