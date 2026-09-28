"""Cumination end-to-end tests inside real Kodi.

  python -m scripts.kodi_e2e selftest                       # harness check, offline
  python -m scripts.kodi_e2e crawl --out results/kodi_e2e   # every site
  python -m scripts.kodi_e2e crawl --site pornhub,xvideos --deep
  python -m scripts.kodi_e2e crawl --workers 4 --flaresolverr http://127.0.0.1:8191/v1
  python -m scripts.kodi_e2e report results/kodi_e2e --baseline old/summary.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.kodi_e2e import checks as C  # noqa: E402
from scripts.kodi_e2e.crawler import CrawlOptions, SiteCrawler, discover_sites  # noqa: E402
from scripts.kodi_e2e.driver import KodiDriver  # noqa: E402
from scripts.kodi_e2e.profile import build_profile  # noqa: E402
from scripts.kodi_e2e.report import write_reports  # noqa: E402
from scripts.kodi_e2e.runner import KodiInstance  # noqa: E402


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def say(msg: str) -> None:
    print(msg, flush=True)


# ---------------------------------------------------------------------------
def add_common(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--profile", type=Path, default=ROOT / ".cache" / "kodi_e2e" / "profile",
                    help="throwaway Kodi home (rebuilt each run)")
    ap.add_argument("--reuse-profile", action="store_true",
                    help="don't rebuild the Kodi profile (default: rebuilt every run so it tests your current code)")
    ap.add_argument("--source", choices=["tree", "zip"], default="tree",
                    help="install the addon from the working tree or from built release ZIPs")
    ap.add_argument("--port", type=int, default=8080, help="Kodi web server port")
    ap.add_argument("--kodi-bin", default="kodi")
    ap.add_argument("--no-xvfb", action="store_true", help="use the real $DISPLAY (watch Kodi work)")
    ap.add_argument("--flaresolverr", help="FlareSolverr URL to configure in the addon")
    ap.add_argument("--debug-log", action="store_true")


def add_crawl_opts(ap: argparse.ArgumentParser) -> None:
    ap.add_argument("--search-term", default="blonde")
    ap.add_argument("--deep", action="store_true", help="also play from a category and from search results")
    ap.add_argument("--thumbs", type=int, default=8, help="thumbnails loaded through Kodi per listing")
    ap.add_argument("--play-attempts", type=int, default=2)
    ap.add_argument("--play-timeout", type=float, default=75)
    ap.add_argument("--list-timeout", type=float, default=90)
    ap.add_argument("--site-budget", type=float, default=420, help="max seconds per site")


def crawl_options(args) -> CrawlOptions:
    return CrawlOptions(search_term=args.search_term, deep=args.deep, thumbs=args.thumbs,
                        play_attempts=args.play_attempts, play_timeout=args.play_timeout,
                        list_timeout=args.list_timeout, site_budget=args.site_budget)


def ensure_profile(args, extra_site_modules=None) -> None:
    if not args.reuse_profile or extra_site_modules or not (args.profile / "kodi_e2e_manifest.json").exists():
        build_profile(args.profile, source=args.source, web_port=args.port,
                      flaresolverr_url=args.flaresolverr, debug_log=args.debug_log,
                      extra_site_modules=extra_site_modules)


def select_sites(sites: list[dict], args) -> list[dict]:
    # unique keys when one module registers several sites
    names = [s["name"] for s in sites]
    for s in sites:
        if names.count(s["name"]) > 1:
            s["name"] = s["mode"]
    wanted = {w.strip().lower() for w in ",".join(args.site or []).split(",") if w.strip()}
    skip = {w.strip().lower() for w in ",".join(args.skip or []).split(",") if w.strip()}
    out = []
    for s in sites:
        key = s["name"].lower()
        if wanted and key not in wanted and key.split(".")[0] not in wanted:
            continue
        if key in skip or key.split(".")[0] in skip:
            continue
        out.append(s)
    out.sort(key=lambda s: s["name"])
    if args.shard:
        i, n = (int(x) for x in args.shard.split("/"))
        out = [s for k, s in enumerate(out) if k % n == i]
    if args.limit:
        out = out[: args.limit]
    return out


def write_site(out: Path, res: dict) -> None:
    safe = re.sub(r"[^\w.-]", "_", res["site"])
    (out / "sites" / f"{safe}.json").write_text(json.dumps(res, indent=2), encoding="utf-8")


def harness_error(site: dict, message: str) -> dict:
    return {"site": site["name"], "title": site.get("title", ""), "status": "fail", "hint": "harness",
            "duration": 0, "notes": [], "notifications": [], "steps": [], "playback": [],
            "issues": [C.issue("HARNESS_ERROR", "error", "harness", message)],
            "passed": False, "item_count": 0, "playback_started": False, "message": message}


def run_crawl(args, only: set[str] | None = None) -> int:
    out: Path = args.out
    (out / "sites").mkdir(parents=True, exist_ok=True)
    kodi = KodiInstance(args.profile, port=args.port, kodi_bin=args.kodi_bin, use_xvfb=not args.no_xvfb)
    meta = {"started": now(), "flaresolverr": bool(args.flaresolverr), "shard": args.shard,
            "options": crawl_options(args).__dict__}
    kodi.start()
    try:
        drv = KodiDriver(kodi, search_term=args.search_term)
        sites, listing = discover_sites(drv)
        meta.update(kodi=kodi.version, addon_version=kodi.manifest.get("main_version"),
                    sites_listed=len(sites),
                    addon_findings={k: listing.log.get(k, []) for k in ("addon_settings", "import_errors", "exceptions")
                                    if listing.log.get(k)})
        if only:
            sites = [s for s in sites if s["name"] in only]
        selected = select_sites(sites, args)
        # modules that crash on import never reach the Sites list: report them
        if not args.shard or args.shard.startswith("0/"):
            for err in listing.log.get("import_errors", []):
                mod = err["module"] if isinstance(err, dict) else str(err)
                if args.site and mod not in ",".join(args.site):
                    continue
                res = harness_error({"name": mod}, "")
                res.update(hint=None, message=f"Site module fails to import, so it is missing from the Sites list: "
                                              f"{err.get('error') if isinstance(err, dict) else err}")
                res["issues"] = [C.issue("SITE_IMPORT_ERROR", "error", "errors", res["message"])]
                write_site(out, res)
        say(f"crawling {len(selected)} of {len(sites)} listed sites")
        crawler = SiteCrawler(drv, crawl_options(args))
        for n, site in enumerate(selected, 1):
            if args.restart_every and n > 1 and (n - 1) % args.restart_every == 0:
                kodi.restart()
            if not kodi.alive():
                kodi.restart()
            t0 = time.time()
            try:
                res = crawler.crawl(site)
            except Exception as exc:  # noqa: BLE001
                traceback.print_exc()
                res = harness_error(site, f"crawler crashed: {type(exc).__name__}: {exc}")
            if not kodi.alive():
                res["issues"].insert(0, C.issue("KODI_CRASHED", "error", "errors",
                                                "Kodi stopped responding while testing this site"))
                res["status"], res["passed"] = "fail", False
                kodi.restart()
            write_site(out, res)
            codes = ", ".join(sorted({i["code"] for i in res["issues"] if i["severity"] != "info"}))
            say(f"[{n}/{len(selected)}] {res['status'].upper():4} {site['name']:<22} {time.time() - t0:5.0f}s  {codes}")
    finally:
        meta["finished"] = now()
        name = "run.json" if not args.shard else f"run-{args.shard.replace('/', 'of')}.json"
        (out / name).write_text(json.dumps(meta, indent=2), encoding="utf-8")
        kodi.stop()
    return 0


def run_workers(args) -> int:
    """Split the site list over N Kodi instances (own profile + port each)."""
    n = args.workers
    args.out.mkdir(parents=True, exist_ok=True)
    base = [a for a in sys.argv[1:]]
    # drop options we set per worker
    cleaned, skip_next = [], False
    for a in base:
        if skip_next:
            skip_next = False
            continue
        if a in ("--workers", "--profile", "--port", "--shard"):
            skip_next = True
            continue
        if a.startswith(("--workers=", "--profile=", "--port=", "--shard=")):
            continue
        cleaned.append(a)
    if "--no-report" not in cleaned:
        cleaned.append("--no-report")
    procs = []
    for i in range(n):
        cmd = [sys.executable, "-m", "scripts.kodi_e2e"] + cleaned + [
            "--shard", f"{i}/{n}", "--port", str(args.port + i),
            "--profile", str(args.profile.parent / f"{args.profile.name}-w{i}")]
        logf = open(args.out / f"worker-{i}.log", "w")
        say(f"worker {i}: {' '.join(cmd[3:])}")
        procs.append(subprocess.Popen(cmd, cwd=ROOT, stdout=logf, stderr=subprocess.STDOUT))
        time.sleep(5)  # stagger Kodi start-ups
    codes = [p.wait() for p in procs]
    runs = sorted(args.out.glob("run-*.json"))
    if runs:
        metas = [json.loads(r.read_text()) for r in runs]
        merged = dict(metas[0])
        merged["started"] = min(m["started"] for m in metas)
        merged["finished"] = max(m.get("finished", "") for m in metas)
        merged["workers"] = n
        (args.out / "run.json").write_text(json.dumps(merged, indent=2), encoding="utf-8")
    return max(codes) if codes else 0


def rotate_previous(args) -> None:
    """Keep the last run's summary as the baseline for this run, and clear
    stale per-site files before a full crawl."""
    args.out.mkdir(parents=True, exist_ok=True)
    prev = args.out / "summary.json"
    if prev.exists():
        keep = args.out / "previous_summary.json"
        keep.write_bytes(prev.read_bytes())
        if args.baseline is None:
            args.baseline = keep
    if not (args.site or args.limit):
        for f in (args.out / "sites").glob("*.json"):
            f.unlink()


def cmd_crawl(args) -> int:
    if not args.shard:
        rotate_previous(args)
    if args.workers > 1 and not args.shard:
        # build once up front: fills the dependency cache the workers share
        ensure_profile(args)
        rc = run_workers(args)
    else:
        ensure_profile(args)
        rc = run_crawl(args)
    if not args.no_report:
        summary = write_reports(args.out, args.baseline)
        t = summary["totals"]
        say(f"\n{t['sites']} sites: {t['fail']} broken, {t['warn']} with problems, {t['pass']} clean")
        say(f"report: {args.out / 'report.html'}")
        if args.fail_on_regression and (summary.get("changes") or {}).get("regressed"):
            return 1
    return rc


def cmd_report(args) -> int:
    summary = write_reports(args.results, args.baseline)
    say(json.dumps(summary["totals"]))
    return 0


def cmd_profile(args) -> int:
    ensure_profile(args)
    return 0


# ---------------------------------------------------------------------------
SELFTEST_EXPECT = {
    "e2egood": {"status": {"pass"}, "codes": set()},
    "e2ebroken": {"status": {"fail"}, "codes": {
        "TITLE_HTML_ENTITIES", "TITLE_HTML_TAGS", "TITLE_NUMBER_NOISE", "NO_NEXT_PAGE",
        "THUMBS_BROKEN", "THUMBS_PLACEHOLDER", "THUMBS_LOW_RES", "BLANK_FOLDERS",
        "CATEGORY_EMPTY", "PYTHON_EXCEPTION", "SEARCH_EMPTY", "PLAYBACK_FAILED"}},
}


def cmd_selftest(args) -> int:
    from scripts.kodi_e2e.selftest.server import serve

    tmp = Path(tempfile.mkdtemp(prefix="kodi_e2e_selftest_"))
    httpd = serve(tmp / "www", args.http_port)
    mods = []
    for src in sorted((Path(__file__).parent / "selftest" / "sites").glob("*.py")):
        dst = tmp / src.name
        dst.write_text(src.read_text().replace("__PORT__", str(args.http_port)))
        mods.append(dst)
    args.reuse_profile = False
    ensure_profile(args, extra_site_modules=mods)
    args.site, args.skip, args.shard, args.limit, args.restart_every = ["e2egood,e2ebroken"], None, None, None, 0
    try:
        run_crawl(args)
    finally:
        httpd.shutdown()
    write_reports(args.out)
    ok = True
    for site, exp in SELFTEST_EXPECT.items():
        p = args.out / "sites" / f"{site}.json"
        if not p.exists():
            say(f"SELFTEST FAIL {site}: no result (site missing from Kodi's Sites list?)")
            ok = False
            continue
        res = json.loads(p.read_text())
        codes = {i["code"] for i in res["issues"] if i["severity"] != "info"}
        missing = exp["codes"] - codes
        extra = codes - exp["codes"] if not exp["codes"] else set()
        good = res["status"] in exp["status"] and not missing and not extra
        if site == "e2egood" and not res.get("playback_started"):
            good = False
            missing = missing | {"(playback did not start)"}
        say(f"SELFTEST {'ok  ' if good else 'FAIL'} {site}: status={res['status']}"
            + (f" missing={sorted(missing)}" if missing else "") + (f" unexpected={sorted(extra)}" if extra else ""))
        ok &= good
    say(f"report: {args.out / 'report.html'}")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m scripts.kodi_e2e", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("crawl", help="test sites in headless Kodi")
    add_common(p)
    add_crawl_opts(p)
    p.add_argument("--out", type=Path, default=ROOT / "results" / "kodi_e2e")
    p.add_argument("--site", action="append", help="site name(s), comma separated; default all")
    p.add_argument("--skip", action="append", help="site name(s) to skip")
    p.add_argument("--shard", help="i/n: only every n-th site starting at i (for CI matrices)")
    p.add_argument("--limit", type=int)
    p.add_argument("--workers", type=int, default=1, help="parallel Kodi instances")
    p.add_argument("--restart-every", type=int, default=40, help="restart Kodi every N sites (0 = never)")
    p.add_argument("--baseline", type=Path, help="previous summary.json to diff against")
    p.add_argument("--fail-on-regression", action="store_true")
    p.add_argument("--no-report", action="store_true")
    p.set_defaults(fn=cmd_crawl)

    p = sub.add_parser("selftest", help="check the harness against local fake sites (no internet)")
    add_common(p)
    add_crawl_opts(p)
    p.add_argument("--out", type=Path, default=ROOT / "results" / "kodi_e2e_selftest")
    p.add_argument("--http-port", type=int, default=8765)
    p.set_defaults(fn=cmd_selftest, profile=ROOT / ".cache" / "kodi_e2e" / "selftest-profile", play_attempts=2)

    p = sub.add_parser("report", help="rebuild summary/report from a results dir")
    p.add_argument("results", type=Path)
    p.add_argument("--baseline", type=Path)
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser("profile", help="only build the Kodi profile")
    add_common(p)
    p.set_defaults(fn=cmd_profile)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
