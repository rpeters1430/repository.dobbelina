"""Walk every site the way a user would, inside real Kodi, and record issues."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, urlsplit

from scripts.kodi_e2e import checks as C
from scripts.kodi_e2e.driver import KodiDriver, StepResult, strip_markup

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = "plugin://plugin.video.cumination/"


@dataclass
class CrawlOptions:
    search_term: str = "blonde"
    thumbs: int = 8                 # video thumbnails loaded through Kodi per listing
    category_thumbs: int = 6
    categories: int = 1             # category-type folders to open
    subcategories: int = 2          # entries opened inside each
    play_attempts: int = 2          # videos tried before calling playback broken
    play_timeout: float = 75.0
    list_timeout: float = 90.0
    min_play_seconds: float = 4.0
    deep: bool = False              # also play from category + search results
    site_budget: float = 420.0      # seconds; remaining optional steps are skipped


def load_profiles() -> dict:
    path = ROOT / "config" / "site_profiles.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"default": {}, "sites": {}}


def site_profile(profiles: dict, name: str) -> dict:
    prof = json.loads(json.dumps(profiles.get("default", {})))
    for key, val in profiles.get("sites", {}).get(name, {}).items():
        if isinstance(val, dict) and isinstance(prof.get(key), dict):
            prof[key].update(val)
        else:
            prof[key] = val
    return prof


def discover_sites(drv: KodiDriver) -> tuple[list[dict], StepResult]:
    """Open Cumination -> Sites exactly like a user and return the entries."""
    root = drv.get_directory(PLUGIN, label="Cumination root")
    sites_url = next((i["file"] for i in root.items if C.mode_of(i) == "main.site_list"),
                     PLUGIN + "?url=&mode=main.site_list")
    listing = drv.get_directory(sites_url, label="Sites")
    # module import errors are logged when the plugin starts
    for k in ("import_errors", "exceptions", "addon_settings"):
        listing.log.setdefault(k, [])
        listing.log[k] = root.log.get(k, []) + [x for x in listing.log[k] if x not in root.log.get(k, [])]
    sites = []
    for item in listing.items:
        mode = C.mode_of(item)
        if "." not in mode:
            continue
        sites.append({"name": mode.split(".")[0], "title": strip_markup(item.get("label", "")),
                      "file": item["file"], "mode": mode, "thumbnail": item.get("thumbnail", "")})
    return sites, listing


def with_cause(found: list[dict], step: StepResult) -> list[dict]:
    """Append what the user saw (notification, exception) to 'empty' findings."""
    why = C.cause(step)
    if why:
        for i in found:
            if i["code"] in ("LISTING_EMPTY", "NO_VIDEOS", "FEW_VIDEOS"):
                i["message"] += f" — {why}"
    return found


class SiteCrawler:
    def __init__(self, drv: KodiDriver, opts: CrawlOptions, profiles: dict | None = None):
        self.drv = drv
        self.opts = opts
        self.profiles = profiles if profiles is not None else load_profiles()

    # ------------------------------------------------------------------
    def crawl(self, site: dict) -> dict:
        name = site["name"]
        prof = site_profile(self.profiles, name)
        supports = prof.get("supports", {})
        harness = prof.get("harness", {})
        term = harness.get("search_term") or self.opts.search_term
        self.drv.search_term = term
        t0 = time.time()
        issues: list[dict] = []
        steps: list[StepResult] = []
        plays: list[StepResult] = []
        notes: list[str] = []

        def over_budget(what: str) -> bool:
            if time.time() - t0 > self.opts.site_budget:
                notes.append(f"skipped {what}: site time budget ({self.opts.site_budget:.0f}s) used up")
                return True
            return False

        def step_list(url, label_):
            st = self.drv.get_directory(url, timeout=self.opts.list_timeout, label=label_)
            steps.append(st)
            if st.elapsed > 30 and st.ok:
                issues.append(C.issue("SLOW_LISTING", "info", "listing", f"took {st.elapsed:.0f}s", label_))
            for d in st.dialogs:
                if d["kind"] in ("ok", "yesno", "textviewer", "unknown_dialog"):
                    issues.append(C.issue("UNEXPECTED_DIALOG", "warn", "dialogs",
                                          f"{d['kind']} popup: {d.get('heading', '')} {d.get('text', '')}".strip(),
                                          label_))
            return st

        # 1. site main menu ------------------------------------------------
        main = step_list(site["file"], "main menu")
        hint = None
        if not main.ok or not main.items:
            code, msg = ("LISTING_ERROR", main.error or "error") if not main.ok else ("LISTING_EMPTY", "empty list")
            why = C.cause(main)
            issues.append(C.issue(code, "error", "listing",
                                  f"Site does not open: {msg}" + (f" — {why}" if why and why != msg else ""),
                                  "main menu"))
            return self._finish(site, prof, t0, issues, steps, plays, notes, hint, listing=None)

        parts = C.split_items(main.items)
        listing = main
        if not parts["videos"]:
            # A user would open the obvious "videos" folder.
            cands = [f for f in parts["folders"] if not C.is_category(f) and not C.is_search(f)]
            pick = next((f for f in cands if C.LISTING_FOLDER_RE.search(C.label(f))), cands[0] if cands else None)
            if pick:
                notes.append(f"main menu has no videos; opened '{C.label(pick)}'")
                listing = step_list(pick["file"], f"'{C.label(pick)}'")
                if not listing.ok:
                    issues.append(C.issue("LISTING_ERROR", "error", "listing",
                                          f"'{C.label(pick)}' failed: {listing.error}", listing.target))

        # 2. the video list -------------------------------------------------
        if listing is main:
            issues.extend(with_cause(C.check_listing(main.items, "main menu"), main))
        else:
            issues.extend(C.check_listing(main.items, "main menu", expect_videos=False))
            if listing.ok:
                issues.extend(with_cause(C.check_listing(listing.items, listing.target), listing))
        lparts = C.split_items(listing.items) if listing.ok else C.split_items([])
        videos = lparts["videos"]

        # 3. thumbnails, loaded by Kodi ------------------------------------
        if videos:
            fetched = [self.drv.fetch_image(C.thumb_of(v)) for v in videos[: self.opts.thumbs] if C.thumb_of(v)]
            issues.extend(C.check_thumbnails(videos, fetched, listing.target))
            listing.extra["thumbs"] = fetched

        # 4. next page ------------------------------------------------------
        if lparts["next"] and not over_budget("next page"):
            p2 = step_list(lparts["next"]["file"], "next page")
            issues.extend(C.check_pagination(listing.items, p2, "next page"))
            if p2.ok:
                issues.extend([i for i in C.check_titles([v for v in p2.items if C.is_video(v)], "next page")
                               if i["code"] in ("BLANK_TITLES",)])

        # 5. playback -------------------------------------------------------
        if supports.get("play", True) is False or harness.get("playback_not_testable"):
            notes.append("playback not tested (site profile)")
        elif not videos:
            if listing.ok:
                why = C.cause(listing)
                issues.append(C.issue("NOTHING_TO_PLAY", "error", "playback",
                                      "No playable items found" + (f" — {why}" if why else ""), listing.target))
        else:
            issues.extend(self._play_some(videos, listing.target, plays))

        # 6. categories -----------------------------------------------------
        cats = sorted(parts["categories"], key=lambda f: 0 if "categor" in C.label(f).lower() else 1)
        if supports.get("categories", True) is not False:
            for cat in cats[: self.opts.categories]:
                if over_budget("categories"):
                    break
                issues.extend(self._check_category(cat, step_list, plays, harness))

        # 7. search ---------------------------------------------------------
        search = parts["search"] or lparts["search"]
        if supports.get("search", True) is False:
            notes.append("search not supported (site profile)")
        elif search is None:
            issues.append(C.issue("NO_SEARCH", "info", "search", "No search entry in the site menu", "main menu"))
        elif not over_budget("search"):
            issues.extend(self._check_search(search, term, step_list, plays, harness))

        return self._finish(site, prof, t0, issues, steps, plays, notes, hint, listing=listing)

    # ------------------------------------------------------------------
    def _play_some(self, videos, where, plays, attempts=None) -> list[dict]:
        attempts = attempts or self.opts.play_attempts
        tried = []
        for v in videos[:attempts]:
            st = self.drv.play(v["file"], label=C.label(v), timeout=self.opts.play_timeout,
                               min_seconds=self.opts.min_play_seconds)
            st.extra["from"] = where
            plays.append(st)
            tried.append(st)
            if st.ok:
                break
        ok = [t for t in tried if t.ok]
        out = []
        for t in tried:
            out.extend(C.log_issues(f"play '{t.target[:40]}'", t.log))
        if not ok:
            reason = C.playback_failure_reason(tried[0])
            hint = C.blocked_hint(tried[0])
            out.append(C.issue("PLAYBACK_FAILED", "error", "playback",
                               f"{len(tried)} of {len(tried)} videos failed to play: {reason}"
                               + (f" ({hint})" if hint else ""), where,
                               [t.target for t in tried]))
        else:
            if not tried[0].ok:
                out.append(C.issue("PLAYBACK_FLAKY", "warn", "playback",
                                   f"first video failed ({C.playback_failure_reason(tried[0])}), next one played",
                                   where, [tried[0].target]))
            out.extend(C.check_playback(ok[0], where))
        return out

    def _check_category(self, cat, step_list, plays, harness) -> list[dict]:
        name = C.label(cat)
        optional = harness.get("categories_optional")
        cs = step_list(cat["file"], f"'{name}'")
        if not cs.ok or not cs.items:
            sev = "info" if optional else "error"
            what = cs.error if not cs.ok else "empty list"
            why = C.cause(cs)
            return [C.issue("CATEGORY_BROKEN", sev, "categories",
                            f"'{name}' does not open: {what}" + (f" — {why}" if why and why != what else ""),
                            cs.target)]
        out = C.log_issues(cs.target, cs.log)
        parts = C.split_items(cs.items)
        out.extend(i for i in C.check_listing(cs.items, cs.target, expect_videos=False))
        if parts["videos"] and not parts["folders"]:
            # the "category" is already a video list
            out.extend(C.check_listing(cs.items, cs.target))
            return out
        entries = [f for f in parts["folders"] if C.label(f)]
        fetched = [self.drv.fetch_image(C.thumb_of(f)) for f in entries[: self.opts.category_thumbs] if C.thumb_of(f)]
        out.extend(C.check_thumbnails(entries, fetched, cs.target, kind="category"))
        empties = []
        for sub in entries[: self.opts.subcategories]:
            st = step_list(sub["file"], f"'{name}' > '{C.label(sub)}'")
            out.extend(C.log_issues(st.target, st.log))
            sv = [i for i in st.items if C.is_video(i)] if st.ok else []
            if not sv:
                empties.append(f"{C.label(sub)}: {C.cause(st) or 'no videos'}")
                continue
            out.extend(C.check_listing(st.items, st.target))
            if self.opts.deep:
                out.extend(self._play_some(sv, st.target, plays, attempts=1))
        if empties:
            sampled = min(len(entries), self.opts.subcategories)
            sev = "error" if len(empties) == sampled and not optional else "warn"
            out.append(C.issue("CATEGORY_EMPTY", sev, "categories",
                               f"{len(empties)}/{sampled} opened entries under '{name}' had no videos",
                               cs.target, empties))
        return out

    def _check_search(self, search, term, step_list, plays, harness) -> list[dict]:
        optional = harness.get("search_results_optional")
        ss = step_list(search["file"], "search menu")
        if not ss.ok:
            return [C.issue("SEARCH_BROKEN", "error", "search", f"Search menu failed: {ss.error}", ss.target)]
        out = C.log_issues(ss.target, ss.log)
        results = ss
        if not any(C.is_video(i) for i in ss.items):
            one = next((i for i in ss.items if C.mode_of(i) == "utils.oneSearch"), None)
            if one is None:
                return out + [C.issue("SEARCH_BROKEN", "error", "search",
                                      "Search menu has no 'One time search' entry and asked for no keyword", ss.target)]
            # What Kodi runs after the user types the keyword (utils.oneSearch)
            q = parse_qs(urlsplit(one["file"]).query)
            url = (q.get("url") or [""])[0]
            channel = (q.get("channel") or [""])[0]
            search_url = f"{PLUGIN}?url={quote_plus(url)}&mode={channel}&keyword={quote_plus(term)}"
            results = step_list(search_url, f"search '{term}'")
        if not results.ok:
            return out + [C.issue("SEARCH_BROKEN", "error", "search",
                                  f"Searching '{term}' failed: {C.cause(results) or results.error}", results.target)]
        out.extend(C.log_issues(results.target, results.log))
        rv = [i for i in results.items if C.is_video(i)]
        if not rv:
            sev = "info" if optional else "error"
            why = C.cause(results)
            out.append(C.issue("SEARCH_EMPTY", sev, "search",
                               f"Searching '{term}' returned no videos" + (f" — {why}" if why else ""),
                               results.target))
            return out
        out.extend(i for i in C.check_listing(results.items, results.target)
                   if i["area"] in ("titles", "listing") and i["code"] != "NO_NEXT_PAGE")
        if self.opts.deep:
            out.extend(self._play_some(rv, results.target, plays, attempts=1))
        return out

    # ------------------------------------------------------------------
    def _finish(self, site, prof, t0, issues, steps, plays, notes, hint, listing) -> dict:
        for st in steps:
            issues.extend(C.log_issues(st.target, st.log))
        # dedupe (same code + message)
        seen, uniq = set(), []
        for i in issues:
            key = (i["code"], i["message"])
            if key not in seen:
                seen.add(key)
                uniq.append(i)
        order = {"error": 0, "warn": 1, "info": 2}
        # headline = what hurts users most: can't open > can't play > search ...
        area_rank = {a: n for n, a in enumerate(
            ["listing", "playback", "search", "categories", "pagination", "errors", "images", "titles", "dialogs"])}
        uniq.sort(key=lambda i: (order.get(i["severity"], 3), area_rank.get(i["area"], 99)))
        status = C.site_status(uniq)
        if status == "fail" and not hint:
            # one explanation for the whole site when the network is the problem
            hint = next((h for h in (C.blocked_hint(s) for s in steps + plays) if h), None)
        videos = [i for i in (listing.items if listing and listing.ok else []) if C.is_video(i)]
        played = [p for p in plays if p.ok]
        notifications = sorted({n for st in steps + plays for n in st.log.get("notifications", [])})
        first_error = next((i for i in uniq if i["severity"] == "error"), None)
        return {
            "site": site["name"],
            "title": site.get("title", site["name"]),
            "status": status,
            "hint": hint,
            "tier": prof.get("tier"),
            "content_type": prof.get("content_type"),
            "duration": round(time.time() - t0, 1),
            "issues": uniq,
            "notes": notes,
            "notifications": notifications,
            "steps": [s.to_dict(keep_items=5) for s in steps],
            "playback": [p.to_dict() for p in plays],
            # compatible with scripts/merge_kodi_results.py
            "passed": status != "fail",
            "item_count": len(videos),
            "playback_started": bool(played),
            "message": first_error["message"] if first_error else ("OK" if status == "pass" else "works with warnings"),
        }
