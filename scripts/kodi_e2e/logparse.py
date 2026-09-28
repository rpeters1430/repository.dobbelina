"""Turn a slice of kodi.log into structured findings."""

from __future__ import annotations

import re
from urllib.parse import urlsplit

LINE_RE = re.compile(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+ T:\d+\s+(\w+) <([^>]*)>: ?(.*)$")

NOISE = (
    "GUIFontManager", "VDPAU", "DBus", "ActiveAE", "OpenSink", "InitSink",
    "CDisplaySettings", "unable to load settings", "pw.conf", "libva",
    "CPowerManager", "Unable to find a", "CAddonMgr::FindAddons", "RetroPlayer",
    "Previous line repeats", "CSettingsManager", "Failed to load skin",
    "CPeripheral", "CWinSystemX11", "CGUIWindowManager", "CInputManager",
    "CLangInfo", "CSkinInfo", "GetMaxRes", "XRandR", "CAirPlay", "CZeroconf",
    "Texture manager unable to load file", "CGUIMediaWindow::GetDirectory",
    "CServiceAddon", "Unable to get Codec", "CAddonDatabase", "CPythonInvoker(",
)

PLAYBACK_PATTERNS = (
    "skipping unplayable item", "error opening", "Error creating demuxer",
    "OpenInputStream", "OpenDemuxStream", "error probing input format",
    "CVideoPlayer::OpenFile", "Playback failed", "inputstream.adaptive",
    "Unable to open", "CDVDInputStream", "Open - Failed to open",
    "manifest", "Failed to play", "CFFmpegImage",
)

MAX_PER_KIND = 12


def _host(url: str) -> str:
    try:
        return urlsplit(url.split("|", 1)[0]).netloc or url[:60]
    except ValueError:
        return url[:60]


def _entries(lines: list[str]):
    """Group raw lines into (level, text) entries; continuation lines are
    appended to the previous entry."""
    cur = None
    for raw in lines:
        m = LINE_RE.match(raw)
        if m:
            if cur:
                yield cur
            cur = [m.group(1).lower(), m.group(2), m.group(3)]
        elif cur is not None:
            cur[2] += "\n" + raw
    if cur:
        yield cur


def parse_log_lines(lines: list[str]) -> dict:
    out: dict[str, list] = {
        "exceptions": [], "notifications": [], "import_errors": [],
        "addon_errors": [], "curl_errors": [], "playback_errors": [],
        "directory_errors": [], "other_errors": [], "addon_settings": [],
    }
    in_exc: list[str] | None = None

    def add(kind, value):
        if value not in out[kind] and len(out[kind]) < MAX_PER_KIND:
            out[kind].append(value)

    for level, comp, text in _entries(lines):
        # Kodi complaining about the addon's settings.xml (shown to every user)
        if comp.startswith("CAddonSettings") and "plugin.video.cumination" in comp:
            add("addon_settings", text[:200])
            continue
        # --- python exceptions (single multi-line entry, or split over entries)
        if "EXCEPTION Thrown (PythonToCppException)" in text or "Python callback/script returned the following error" in text:
            in_exc = [text]
            # Kodi 19+ writes the whole report as one entry; older builds
            # split it over several timestamped lines until the end marker.
            if "End of Python script error report" not in text and "Error Type:" not in text:
                continue
        elif in_exc is not None:
            in_exc.append(text)
            if "End of Python script error report" not in text and len(in_exc) < 60:
                continue
        if in_exc is not None:
            add("exceptions", _summarise_exception("\n".join(in_exc)))
            in_exc = None
            continue

        if "@@@@Cumination:" in text:
            msg = text.split("@@@@Cumination:", 1)[1].strip()
            if msg.startswith("Notification:"):
                add("notifications", msg[len("Notification:"):].strip())
            elif level in ("error", "fatal", "warning"):
                add("addon_errors", msg[:300])
            continue
        if "incompatible site module" in text:
            m = re.search(r"incompatible site module \(([^)]+)\): (.*)", text)
            add("import_errors", {"module": m.group(1), "error": m.group(2)[:300]} if m else text[:300])
            continue

        if level not in ("error", "fatal", "warning"):
            if "skipping unplayable item" in text:
                add("playback_errors", text[:300])
            continue

        if "CCurlFile" in text or "CurlFile" in text:
            m = re.search(r"code (\d{3})", text) or re.search(r"\((\d+)\)", text)
            u = re.search(r"(?:for|url) (\S+)", text)
            add("curl_errors", {"code": m.group(1) if m else "?", "host": _host(u.group(1)) if u else "?",
                                "what": "stat" if "Stat" in text else "open"})
            continue
        if any(p in text for p in PLAYBACK_PATTERNS):
            add("playback_errors", _strip_urls(text)[:300])
            continue
        if "plugin://" in text and ("GetDirectory" in text or "CPluginDirectory" in text):
            add("directory_errors", _strip_urls(text)[:300])
            continue
        if level in ("error", "fatal") and not any(n in text for n in NOISE):
            add("other_errors", _strip_urls(text)[:300])

    return {k: v for k, v in out.items() if v}


def _strip_urls(text: str) -> str:
    return re.sub(r"(https?://[^/\s|]+)[^\s|]*(\|\S*)?", r"\1/…", text)


def _summarise_exception(block: str) -> dict:
    etype = re.search(r"Error Type: <class '([^']+)'>", block)
    contents = re.search(r"Error Contents: (.*)", block)
    frames = re.findall(r'File "([^"]+)", line (\d+), in (\S+)', block)
    where = ""
    for path, line, func in reversed(frames):
        if "plugin.video.cumination" in path or "resolveurl" in path:
            short = path.split("addons/", 1)[-1]
            where = f"{short}:{line} in {func}"
            break
    if not where and frames:
        path, line, func = frames[-1]
        where = f"{path.split('/')[-1]}:{line} in {func}"
    return {
        "type": etype.group(1) if etype else "Exception",
        "message": _strip_urls(contents.group(1).strip())[:300] if contents else "",
        "where": where,
    }
