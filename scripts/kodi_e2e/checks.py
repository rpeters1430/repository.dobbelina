"""Heuristics that turn what Kodi showed into user-visible problems.

Pure functions only (no Kodi, no network) so they can be unit tested.
Severity:
    error - the feature is broken for users (nothing listed, won't play, ...)
    warn  - it works but looks wrong (missing thumbs, junk in titles, ...)
    info  - worth knowing (notifications shown, slow responses, ...)
"""

from __future__ import annotations

import re
from collections import Counter
from urllib.parse import parse_qs, urlsplit

from scripts.kodi_e2e.driver import strip_markup

NEXT_RE = re.compile(r"(^|\b)(next( page)?|more videos|load more|volgende|suivante|siguiente)\b|^\s*(>>|»|›)", re.I)
SEARCH_RE = re.compile(r"search|zoek|suche|buscar", re.I)
CATEGORY_RE = re.compile(
    r"categor|tags?\b|genres?|channels?|models?|pornstars?|stars\b|niches?|studios?|"
    r"collections?|playlists?|actress|actors?|performers?|sites?\b|networks?|countries|groups?",
    re.I,
)
LISTING_FOLDER_RE = re.compile(
    r"latest|newest|recent|new videos|most (viewed|popular|recent)|top( rated)?|popular|"
    r"trending|updates|all videos|videos\b|hot\b|featured|best", re.I,
)
CHALLENGE_RE = re.compile(r"cloudflare|just a moment|attention required|ddos-guard|verify you are human|access denied", re.I)
DEFAULT_ART = re.compile(r"Default(Video|Folder|File|Movie)", re.I)

ENTITY_RE = re.compile(r"&(amp|quot|lt|gt|nbsp|apos|#\d+|#x[0-9a-f]+);", re.I)
TAG_RE = re.compile(r"</?[a-z][a-z0-9]*(\s[^>]*)?/?>", re.I)
DURATION_EDGE_RE = re.compile(r"^\s*\d{1,2}:\d{2}(:\d{2})?\b|\b\d{1,2}:\d{2}(:\d{2})?\s*$")
LONG_NUMBER_RE = re.compile(r"(?<![\w.])\d{5,}(?![\w.])")
STATS_RE = re.compile(r"\b\d+(\.\d+)?\s?[kKmM]?\s?(views|likes|%)|\b\d{2,3}%", re.I)
HANDLE_RE = re.compile(r"^@\w+")
SLUG_RE = re.compile(r"^[\w]+([-_][\w]+){2,}$")


def issue(code: str, severity: str, area: str, message: str, step: str = "", examples=None) -> dict:
    d = {"code": code, "severity": severity, "area": area, "message": message}
    if step:
        d["step"] = step
    if examples:
        d["examples"] = list(examples)[:5]
    return d


# --------------------------------------------------------------------------
# item helpers
# --------------------------------------------------------------------------
def mode_of(item: dict) -> str:
    try:
        q = parse_qs(urlsplit(item.get("file", "")).query)
        return (q.get("mode") or [""])[0]
    except ValueError:
        return ""


def label(item: dict) -> str:
    return strip_markup(item.get("label", ""))


# Non-folder entries that are actions, not videos (search prompts, favourites,
# "Refresh images", "Clear all filters", ...). Video entries use Play*-style
# modes (Playvid, Play, NLPLAYVID, online, ...).
ACTION_MODE_PREFIXES = ("utils.", "favorites.", "main.", "pin.")
ACTION_FUNC_RE = re.compile(
    r"clean|reset|clear|refresh|setting|config|login|logout|sort|filter|toggle|^set|changeper|"
    r"delete|remove|update|about|help|account|lang|country|quality|order|period|orientation|contextm",
    re.I,
)
# Folders that change a filter instead of listing content: "Country: USA",
# "Sort by: Newest", "Orientation: Straight"
SETTING_LABEL_RE = re.compile(r"^[A-Za-z][A-Za-z ]{1,24}:\s+\S|^(sort|order|filter)\b", re.I)


def mode_func(item: dict) -> str:
    return mode_of(item).rsplit(".", 1)[-1]


def is_action(item: dict) -> bool:
    mode = mode_of(item)
    return mode.startswith(ACTION_MODE_PREFIXES) or bool(ACTION_FUNC_RE.search(mode_func(item)))


def is_video(item: dict) -> bool:
    return item.get("filetype") == "file" and not is_action(item)


def is_folder(item: dict) -> bool:
    return item.get("filetype") == "directory"


def is_setting(item: dict) -> bool:
    return is_folder(item) and (bool(SETTING_LABEL_RE.search(label(item))) or is_action(item))


def is_next(item: dict) -> bool:
    return is_folder(item) and bool(NEXT_RE.search(label(item)))


def is_search(item: dict) -> bool:
    return bool(SEARCH_RE.search(mode_of(item)) or SEARCH_RE.search(label(item)))


def is_category(item: dict) -> bool:
    return (is_folder(item) and not is_next(item) and not is_search(item) and not is_setting(item)
            and bool(CATEGORY_RE.search(label(item))))


def thumb_of(item: dict) -> str:
    art = item.get("art") or {}
    t = item.get("thumbnail") or art.get("thumb") or art.get("poster") or art.get("icon") or ""
    return "" if DEFAULT_ART.search(t) else t


def split_items(items: list[dict]) -> dict:
    videos = [i for i in items if is_video(i)]
    folders = [i for i in items if is_folder(i)]
    return {
        "videos": videos,
        "folders": [f for f in folders if not is_next(f) and not is_setting(f)],
        "settings": [f for f in folders if is_setting(f)],
        "next": next((f for f in folders if is_next(f)), None),
        "search": next((f for f in folders if is_search(f)), None),
        "categories": [f for f in folders if is_category(f)],
    }


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------
def check_listing(items: list[dict], step: str, *, expect_videos: bool = True,
                  min_videos: int = 6, next_expected_at: int = 10) -> list[dict]:
    out: list[dict] = []
    if not items:
        return [issue("LISTING_EMPTY", "error", "listing", "Kodi showed an empty list", step)]
    parts = split_items(items)
    labels = [label(i) for i in items]

    blocked = [lb for lb in labels if CHALLENGE_RE.search(lb)]
    if blocked:
        out.append(issue("BLOCKED_PAGE", "error", "listing",
                         "Listing contains an anti-bot / challenge page", step, blocked))

    blank = [i for i in parts["folders"] if not label(i)]
    if blank:
        out.append(issue("BLANK_FOLDERS", "warn", "listing",
                         f"{len(blank)} folder(s) with no name", step,
                         [redact_file(i.get("file", "")) for i in blank]))

    videos = parts["videos"]
    if expect_videos:
        if not videos and not parts["folders"]:
            out.append(issue("NO_VIDEOS", "error", "listing", "No videos in the list", step))
        elif 0 < len(videos) < min_videos:
            out.append(issue("FEW_VIDEOS", "warn", "listing",
                             f"Only {len(videos)} video(s) listed", step))
        if len(videos) >= next_expected_at and parts["next"] is None:
            out.append(issue("NO_NEXT_PAGE", "warn", "pagination",
                             f"{len(videos)} videos but no 'Next Page' item", step))

    files = [v.get("file", "") for v in videos]
    if len(files) >= 5:
        dup = len(files) - len(set(files))
        if dup / len(files) > 0.2:
            out.append(issue("DUPLICATE_ITEMS", "warn", "listing",
                             f"{dup} duplicate video entries", step))
    out.extend(check_titles(videos, step))
    return out


def check_titles(videos: list[dict], step: str) -> list[dict]:
    if not videos:
        return []
    out = []
    raw = [strip_markup(v.get("label", "")) for v in videos]
    n = len(raw)

    def fire(code, pred, message, min_ratio=0.25, min_count=2, severity="warn"):
        """Report a pattern only when it is systematic (a parser problem),
        not a single odd title."""
        hits = [t for t in raw if pred(t)]
        if len(hits) >= min_count and len(hits) / n >= min_ratio:
            out.append(issue(code, severity, "titles", message.format(n=len(hits), total=n), step, hits))

    # These are decoding bugs even when they hit a single title.
    fire("BLANK_TITLES", lambda t: not t, "{n}/{total} videos have no title", min_ratio=0, min_count=1)
    fire("TITLE_HTML_ENTITIES", lambda t: bool(ENTITY_RE.search(t)),
         "{n}/{total} titles contain undecoded HTML entities (&amp; etc.)", min_ratio=0, min_count=1)
    fire("TITLE_HTML_TAGS", lambda t: bool(TAG_RE.search(t)),
         "{n}/{total} titles contain HTML tags", min_ratio=0, min_count=1)
    fire("TITLE_NUMBER_NOISE",
         lambda t: bool(DURATION_EDGE_RE.search(t) or LONG_NUMBER_RE.search(t) or STATS_RE.search(t)),
         "{n}/{total} titles have durations/ids/view counts mixed into the name")
    fire("TITLE_HANDLE", lambda t: bool(HANDLE_RE.search(t)),
         "{n}/{total} titles are usernames (@handle) rather than video names")
    fire("TITLE_SLUG", lambda t: bool(SLUG_RE.match(t)) or t.lower().startswith(("http://", "https://")),
         "{n}/{total} titles look like URL slugs")
    fire("TITLE_WHITESPACE", lambda t: "\n" in t or "\t" in t or "  " in t,
         "{n}/{total} titles contain line breaks or runs of spaces")
    fire("TITLE_TOO_LONG", lambda t: len(t) > 140, "{n}/{total} titles are over 140 characters")
    fire("TITLE_MOSTLY_DIGITS",
         lambda t: bool(t) and sum(c.isalpha() for c in t) < 3 and sum(c.isdigit() for c in t) >= 2,
         "{n}/{total} titles are only numbers")

    nonblank = [t for t in raw if t]
    if len(nonblank) >= 5:
        dup = [t for t, c in Counter(nonblank).items() if c > 1]
        if len(set(nonblank)) / len(nonblank) < 0.7:
            out.append(issue("DUPLICATE_TITLES", "warn", "titles",
                             f"Only {len(set(nonblank))} distinct titles among {len(nonblank)} videos", step, dup))
    return out


def check_thumbnails(items: list[dict], fetched: list[dict], step: str, kind: str = "video") -> list[dict]:
    """items: listed entries; fetched: driver.fetch_image results for a sample."""
    out = []
    if not items:
        return out
    missing = [label(i) for i in items if not thumb_of(i)]
    ratio_missing = len(missing) / len(items)
    if ratio_missing >= 0.5:
        out.append(issue("THUMBS_MISSING", "warn" if kind != "video" else "error", "images",
                         f"{len(missing)}/{len(items)} {kind}s have no image", step, missing))
    elif missing:
        out.append(issue("THUMBS_SOME_MISSING", "warn", "images",
                         f"{len(missing)}/{len(items)} {kind}s have no image", step, missing))
    if not fetched:
        return out

    failed = [f for f in fetched if not f.get("ok")]
    if failed:
        sev = "error" if len(failed) / len(fetched) >= 0.5 and kind == "video" else "warn"
        code = "THUMBS_BROKEN" if sev == "error" else "THUMBS_SOME_BROKEN"
        by_status = Counter(str(f.get("status")) for f in failed)
        out.append(issue(code, sev, "images",
                         f"Kodi could not load {len(failed)}/{len(fetched)} sampled {kind} images "
                         f"({', '.join(f'{k}×{v}' for k, v in by_status.most_common())})",
                         step, [f.get("thumb") for f in failed]))

    good = [f for f in fetched if f.get("ok")]
    if len(good) >= 3:
        common, count = Counter(f.get("sha1") for f in good).most_common(1)[0]
        if count / len(good) >= 0.6:
            out.append(issue("THUMBS_PLACEHOLDER", "warn", "images",
                             f"{count}/{len(good)} {kind} images are the same picture (placeholder?)",
                             step, [f.get("thumb") for f in good if f.get("sha1") == common]))
        sized = [f for f in good if f.get("width")]
        small = [f for f in sized if f["width"] < 200 or f["height"] < 110]
        if sized and len(small) / len(sized) >= 0.5:
            out.append(issue("THUMBS_LOW_RES", "warn", "images",
                             f"{len(small)}/{len(sized)} {kind} images are tiny (<200x110)",
                             step, [f"{f['width']}x{f['height']} {f.get('thumb')}" for f in small]))
        slow = [f for f in good if f.get("elapsed", 0) > 8]
        if len(slow) / len(good) >= 0.5:
            out.append(issue("THUMBS_SLOW", "info", "images",
                             f"{len(slow)}/{len(good)} images took over 8s to load", step))
    return out


def check_pagination(page1: list[dict], page2_step, step: str) -> list[dict]:
    if page2_step is None:
        return []
    if not page2_step.ok:
        return [issue("NEXT_PAGE_ERROR", "error", "pagination",
                      f"'Next Page' failed: {page2_step.error}", step)]
    v1 = {i.get("file") for i in page1 if is_video(i)}
    v2 = [i for i in page2_step.items if is_video(i)]
    if not v2:
        return [issue("NEXT_PAGE_EMPTY", "error", "pagination", "'Next Page' opened an empty list", step)]
    same = sum(1 for i in v2 if i.get("file") in v1)
    if same / len(v2) > 0.8:
        return [issue("NEXT_PAGE_SAME", "warn", "pagination",
                      f"Page 2 repeats page 1 ({same}/{len(v2)} identical)", step)]
    return []


def check_playback(step, label_: str) -> list[dict]:
    out = []
    ex = step.extra
    if step.ok:
        h = ex.get("height") or 0
        if h and h < 300:
            out.append(issue("LOW_QUALITY_STREAM", "warn", "playback",
                             f"Plays at only {ex.get('width')}x{h}", label_))
        if step.elapsed > 30:
            out.append(issue("SLOW_START", "info", "playback",
                             f"Took {step.elapsed:.0f}s to start playing", label_))
    return out


def playback_failure_reason(step) -> str:
    log = step.log or {}
    bits = []
    if log.get("notifications"):
        bits.append("addon said: " + "; ".join(log["notifications"][:2]))
    for d in step.dialogs:
        if d.get("kind") == "ok":
            bits.append(f"Kodi dialog: {d.get('heading')} - {d.get('text')}".strip(" -"))
    if log.get("exceptions"):
        e = log["exceptions"][0]
        bits.append(f"{e['type']}: {e['message']} @ {e['where']}")
    if log.get("curl_errors"):
        bits.append("HTTP errors: " + ", ".join(f"{c['code']} {c['host']}" for c in log["curl_errors"][:3]))
    if log.get("playback_errors"):
        bits.append("player: " + log["playback_errors"][0])
    if step.extra.get("started") and not step.ok:
        bits.append(f"started but stalled at {step.extra.get('position') or 0:.1f}s")
    if not bits and step.extra.get("gave_up"):
        bits.append(step.extra["gave_up"])
    if not bits:
        bits.append(step.error or "nothing started within the timeout")
    return " | ".join(bits)


def log_issues(step_name: str, log: dict) -> list[dict]:
    out = []
    for e in log.get("exceptions", []):
        out.append(issue("PYTHON_EXCEPTION", "error", "errors",
                         f"{e['type']}: {e['message']}", step_name, [e.get("where", "")]))
    for e in log.get("import_errors", []):
        out.append(issue("SITE_IMPORT_ERROR", "error", "errors", str(e), step_name))
    return out


def blocked_hint(step) -> str | None:
    """Explain failures caused by the network / anti-bot protection rather
    than by the scraper. Keyed to the addon's own notification texts
    (strings.po 30416-30418 and the Cloudflare messages in utils.getHtml)."""
    text = " ".join(step.log.get("notifications", []) + step.log.get("addon_errors", []))
    codes = {c.get("code") for c in step.log.get("curl_errors", [])}
    if CHALLENGE_RE.search(text) or "flaresolverr" in text.lower():
        return "anti-bot challenge (Cloudflare/DDoS-Guard) - needs FlareSolverr"
    if codes & {"403", "503", "429"}:
        return f"site refused requests (HTTP {', '.join(sorted(codes & {'403', '503', '429'}))})"
    if re.search(r"too slow|timed out|timeout|name resolution|resolve host|connection refused", text, re.I):
        return "site unreachable (DNS, connection or timeout error)"
    if re.search(r"website is down", text, re.I):
        return "site returned a server error (5xx)"
    if re.search(r"page does not exist", text, re.I):
        return "page not found (4xx) - URL or site layout changed?"
    return None


def cause(step) -> str:
    """Short 'why' for a failed/empty step, from what the user would see."""
    log = step.log or {}
    if log.get("exceptions"):
        e = log["exceptions"][0]
        return f"{e['type']}: {e['message']}"
    if log.get("notifications"):
        return "addon said: " + log["notifications"][0]
    for d in step.dialogs:
        if d.get("kind") in ("ok", "yesno"):
            return f"popup: {d.get('heading')} {d.get('text')}".strip()
    return step.error or ""


def site_status(issues: list[dict]) -> str:
    sev = {i["severity"] for i in issues}
    if "error" in sev:
        return "fail"
    if "warn" in sev:
        return "warn"
    return "pass"


def redact_file(plugin_url: str) -> str:
    try:
        q = parse_qs(urlsplit(plugin_url).query)
        mode = (q.get("mode") or [""])[0]
        url = (q.get("url") or [""])[0]
        return f"{mode} {url[:80]}".strip()
    except ValueError:
        return plugin_url[:100]
