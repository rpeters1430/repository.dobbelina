"""Privacy sanitizer for opt-in diagnostic telemetry.

Ensures no full URLs, credentials, cookies, tokens, search terms, media titles,
local absolute paths, or frame local variables leak in telemetry payloads.
"""

import re
import traceback
import urllib.parse as urllib_parse

MAX_TEXT = 500
MAX_ITEMS = 30
MAX_MAP_ENTRIES = 50

TOP_KEYS = {
    "event_id",
    "timestamp",
    "level",
    "logger",
    "release",
    "environment",
    "message",
    "fingerprint",
    "tags",
    "contexts",
    "exception",
    "breadcrumbs",
    "extra",
}

TAGS_ALLOWLIST = {
    "site",
    "operation",
    "stage",
    "classification",
    "event_type",
    "version",
    "kodi_version",
    "python_version",
    "os",
    "arch",
    "device_class",
    "installation_id",
    "resolver",
    "outcome",
    "container",
    "manifest_type",
    "inputstream_used",
}

CONTEXTS_ALLOWLIST = {"http", "runtime", "device", "resolver", "playback", "os", "app"}

SECRET_KEY_PATTERN = re.compile(
    r"^(authorization|proxy_authorization|cookie|set_cookie|password|token|secret|session|api.?key|pin|username|query|search|media_title|room_name|model_name|unknown)$",
    re.I,
)

URL_PATTERN = re.compile(r"https?://[^\s'\"]+", re.I)
USER_PATH_PATTERN = re.compile(r"(?:[c-zC-Z]:\\Users\\|/home/|/Users/)[^/\\'\"]+", re.I)
SECRET_ASSIGN_PATTERN = re.compile(
    r"(?i)\b(password|token|secret|session|cookie|auth|api_?key|pin|sid)\b\s*[:=]\s*['\"]?[^\s'\",;&]+['\"]?"
)


def sanitize_url(value):
    """Sanitize URL to retain only scheme and domain."""
    if not value:
        return {"scheme": "", "domain": ""}
    url_str = str(value).split("|", 1)[0]
    parsed = urllib_parse.urlsplit(url_str)
    return {
        "scheme": (parsed.scheme or "").lower(),
        "domain": (parsed.hostname or "").lower(),
    }


def _scrub_text(text, addon_root=""):
    """Internal helper to scrub URLs, secrets, and local paths from text."""
    if not text:
        return ""
    text_str = str(text)

    # Scrub URLs into scheme+domain
    def _replace_url(match):
        u = match.group(0)
        parsed = urllib_parse.urlsplit(u)
        scheme = (parsed.scheme or "http").lower()
        host = (parsed.hostname or "").lower()
        return f"{scheme}://{host}"

    text_str = URL_PATTERN.sub(_replace_url, text_str)

    # Scrub secret assignments
    text_str = SECRET_ASSIGN_PATTERN.sub(r"\1=[REDACTED]", text_str)

    # Scrub addon root and user paths
    if addon_root:
        text_str = text_str.replace(addon_root, "<addon>")
    text_str = USER_PATH_PATTERN.sub("<user>", text_str)

    return text_str


def sanitize_text(value, addon_root=""):
    """Sanitize string values and truncate to MAX_TEXT."""
    scrubbed = _scrub_text(value, addon_root=addon_root)
    if len(scrubbed) > MAX_TEXT:
        return scrubbed[: MAX_TEXT - 3] + "..."
    return scrubbed


def safe_exception(exc, addon_root=""):
    """Extract type, sanitized message, and trace frames without locals."""
    if not exc:
        return {}
    exc_type = exc.__class__.__name__
    message = sanitize_text(exc, addon_root=addon_root)
    frames = []
    if exc.__traceback__:
        for f in traceback.extract_tb(exc.__traceback__):
            filename = sanitize_text(f.filename, addon_root=addon_root)
            frames.append({"filename": filename, "function": f.name, "lineno": f.lineno})
    return {"type": exc_type, "value": message, "frames": frames[-20:]}


def sanitize_event(event, addon_root=""):
    """Recursively sanitize an event payload using strict allowlists."""
    if not isinstance(event, dict):
        return {}

    sanitized = {}

    for key, val in event.items():
        if key not in TOP_KEYS:
            continue

        if key == "message":
            sanitized[key] = sanitize_text(val, addon_root=addon_root)
        elif key == "tags" and isinstance(val, dict):
            tags = {}
            for t_k, t_v in val.items():
                if t_k in TAGS_ALLOWLIST and not SECRET_KEY_PATTERN.match(t_k):
                    tags[t_k] = sanitize_text(t_v, addon_root=addon_root)
            sanitized[key] = tags
        elif key == "contexts" and isinstance(val, dict):
            contexts = {}
            for c_k, c_v in val.items():
                if c_k in CONTEXTS_ALLOWLIST and isinstance(c_v, dict):
                    sub_ctx = {}
                    for s_k, s_v in c_v.items():
                        if not SECRET_KEY_PATTERN.match(s_k):
                            sub_ctx[s_k] = sanitize_text(s_v, addon_root=addon_root)
                    contexts[c_k] = sub_ctx
            sanitized[key] = contexts
        elif key == "exception" and isinstance(val, dict):
            if "type" in val:
                sanitized[key] = {
                    "type": val.get("type", ""),
                    "value": sanitize_text(val.get("value", ""), addon_root=addon_root),
                    "frames": [
                        {
                            "filename": sanitize_text(fr.get("filename", ""), addon_root=addon_root),
                            "function": str(fr.get("function", "")),
                            "lineno": fr.get("lineno", 0),
                        }
                        for fr in val.get("frames", [])
                        if isinstance(fr, dict)
                    ][-20:],
                }
        elif key == "breadcrumbs" and isinstance(val, list):
            crumbs = []
            for item in val[:MAX_ITEMS]:
                if isinstance(item, dict):
                    crumb = {}
                    for b_k, b_v in item.items():
                        if not SECRET_KEY_PATTERN.match(b_k):
                            crumb[b_k] = sanitize_text(b_v, addon_root=addon_root)
                    crumbs.append(crumb)
            sanitized[key] = crumbs
        elif isinstance(val, (str, int, float, bool)):
            sanitized[key] = val if isinstance(val, (int, float, bool)) else sanitize_text(val, addon_root=addon_root)
        elif isinstance(val, list):
            sanitized[key] = [sanitize_text(i, addon_root=addon_root) for i in val[:MAX_ITEMS]]

    return sanitized
