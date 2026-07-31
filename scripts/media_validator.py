import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import parse_qs, unquote, urljoin, urlparse

from scripts.site_health_types import ValidationResult, redact_url

MAX_READ_BYTES = 65536
HTML_SIGNATURES = [
    b"<html",
    b"<!doctype html",
    b"video removed",
    b"file not found",
    b"cloudflare",
    b"just a moment",
]


def parse_kodi_url(raw_url: str) -> tuple[str, dict[str, str]]:
    """Parse a Kodi pipe-suffixed URL like URL|Header=Val&Referer=..."""
    if "|" not in raw_url:
        return raw_url.strip(), {}
    parts = raw_url.split("|", 1)
    real_url = parts[0].strip()
    header_str = parts[1].strip()
    headers = {}
    if header_str:
        parsed_qs = parse_qs(header_str, keep_blank_values=True)
        for k, vals in parsed_qs.items():
            if vals:
                headers[k] = unquote(vals[0])
    return real_url, headers


def validate_media(
    raw_url: str,
    allowed_hosts: list[str],
    timeout: float = 15.0,
    session: Any = None,
) -> ValidationResult:
    """Validate direct media, HLS, or DASH streams by fetching headers and sample segment bytes."""
    real_url, extra_headers = parse_kodi_url(raw_url)
    redacted_sample_url = redact_url(real_url)

    evidence: dict[str, Any] = {"sample_url": redacted_sample_url}

    parsed = urlparse(real_url)
    host = parsed.netloc.lower()

    if allowed_hosts:
        matched = False
        for ah in allowed_hosts:
            ah_clean = ah.lower().strip()
            if host == ah_clean or host.endswith("." + ah_clean) or ah_clean.endswith(":" + str(parsed.port or "")):
                matched = True
                break
        if not matched:
            return ValidationResult(
                passed=False,
                classification="HOST_DISALLOWED",
                message=f"Disallowed host for media stream: {host}",
                evidence=evidence,
            )

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    headers.update(extra_headers)
    opener = urllib.request.build_opener()

    try:
        req_headers = dict(headers)
        req_headers["Range"] = "bytes=0-65535"
        req = urllib.request.Request(real_url, headers=req_headers)

        try:
            resp = opener.open(req, timeout=timeout)
            status_code = resp.getcode()
            content_type = resp.headers.get("Content-Type", "")
            content = resp.read(MAX_READ_BYTES)
            resp.close()
        except urllib.error.HTTPError as exc:
            evidence["status_code"] = exc.code
            return ValidationResult(
                passed=False,
                classification="MEDIA_HTTP_ERROR",
                message=f"HTTP status {exc.code} requesting media",
                evidence=evidence,
            )

        evidence["status_code"] = status_code
        evidence["content_type"] = content_type

        # Check HTML signature
        content_lower = content[:2048].lower()
        if any(sig in content_lower for sig in HTML_SIGNATURES):
            return ValidationResult(
                passed=False,
                classification="HTML_PAYLOAD",
                message="Server returned HTML page instead of media content",
                evidence=evidence,
            )

        content_type_lower = content_type.lower()
        path = parsed.path.lower()

        # Check HLS (.m3u8)
        if ".m3u8" in path or "mpegurl" in content_type_lower or content.startswith(b"#EXTM3U"):
            return _validate_hls(real_url, content, headers, opener, timeout, evidence)

        # Check DASH (.mpd)
        if ".mpd" in path or "dash+xml" in content_type_lower or b"<MPD" in content:
            return _validate_dash(real_url, content, headers, opener, timeout, evidence)

        # Direct media
        if len(content) > 0:
            return ValidationResult(
                passed=True,
                classification="NONE",
                message="Direct media stream verified",
                metrics={"media_kind": "direct", "segment_bytes": len(content)},
                evidence=evidence,
            )

        return ValidationResult(
            passed=False,
            classification="EMPTY_MEDIA",
            message="Media response contained 0 bytes",
            evidence=evidence,
        )

    except Exception as exc:
        return ValidationResult(
            passed=False,
            classification="MEDIA_NETWORK_ERROR",
            message=f"Network error fetching media: {type(exc).__name__}",
            evidence=evidence,
        )


def _validate_hls(
    base_url: str,
    content: bytes,
    headers: dict[str, str],
    opener: Any,
    timeout: float,
    evidence: dict[str, Any],
) -> ValidationResult:
    text = content.decode("utf-8", errors="ignore")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Check if master playlist
    media_playlist_url = None
    for line in lines:
        if not line.startswith("#"):
            media_playlist_url = urljoin(base_url, line)
            break

    if not media_playlist_url:
        return ValidationResult(
            passed=False,
            classification="HLS_MANIFEST_INVALID",
            message="HLS playlist contained no variant streams or segments",
            evidence=evidence,
        )

    # If line was media segment TS/AAC/etc vs media playlist .m3u8
    if "#EXT-X-STREAM-INF" in text:
        # Fetch media playlist
        try:
            req = urllib.request.Request(media_playlist_url, headers=headers)
            with opener.open(req, timeout=timeout) as m_resp:
                m_text = m_resp.read().decode("utf-8", errors="ignore")
                m_lines = [l.strip() for l in m_text.splitlines() if l.strip()]
                segment_url = None
                for l in m_lines:
                    if not l.startswith("#"):
                        segment_url = urljoin(media_playlist_url, l)
                        break
                if not segment_url:
                    return ValidationResult(
                        passed=False,
                        classification="HLS_MANIFEST_INVALID",
                        message="HLS media playlist contained no segment URLs",
                        evidence=evidence,
                    )
        except Exception as exc:
            return ValidationResult(
                passed=False,
                classification="HLS_NETWORK_ERROR",
                message=f"Failed to fetch HLS media playlist: {type(exc).__name__}",
                evidence=evidence,
            )
    else:
        segment_url = media_playlist_url

    # Fetch segment bytes
    try:
        req_headers = dict(headers, Range="bytes=0-65535")
        req = urllib.request.Request(segment_url, headers=req_headers)
        with opener.open(req, timeout=timeout) as seg_resp:
            seg_bytes = seg_resp.read(MAX_READ_BYTES)

        if len(seg_bytes) > 0:
            return ValidationResult(
                passed=True,
                classification="NONE",
                message="HLS media stream verified",
                metrics={"media_kind": "hls", "segment_bytes": len(seg_bytes)},
                evidence=evidence,
            )
    except Exception:
        pass

    return ValidationResult(
        passed=False,
        classification="HLS_SEGMENT_EMPTY",
        message="HLS segment fetch failed or returned 0 bytes",
        evidence=evidence,
    )


def _validate_dash(
    base_url: str,
    content: bytes,
    headers: dict[str, str],
    opener: Any,
    timeout: float,
    evidence: dict[str, Any],
) -> ValidationResult:
    try:
        root = ET.fromstring(content)
        base_urls = root.findall(".//{*}BaseURL")
        segment_rel = base_urls[0].text.strip() if base_urls and base_urls[0].text else None

        if not segment_rel:
            segment_rel = "segment.m4s"

        segment_url = urljoin(base_url, segment_rel)
        req_headers = dict(headers, Range="bytes=0-65535")
        req = urllib.request.Request(segment_url, headers=req_headers)
        with opener.open(req, timeout=timeout) as seg_resp:
            seg_bytes = seg_resp.read(MAX_READ_BYTES)

        if len(seg_bytes) > 0:
            return ValidationResult(
                passed=True,
                classification="NONE",
                message="DASH media stream verified",
                metrics={"media_kind": "dash", "segment_bytes": len(seg_bytes)},
                evidence=evidence,
            )
    except Exception as exc:
        return ValidationResult(
            passed=False,
            classification="DASH_PARSE_ERROR",
            message=f"Failed to parse or fetch DASH manifest: {type(exc).__name__}",
            evidence=evidence,
        )

    return ValidationResult(
        passed=False,
        classification="DASH_SEGMENT_EMPTY",
        message="DASH segment fetch failed or returned 0 bytes",
        evidence=evidence,
    )
