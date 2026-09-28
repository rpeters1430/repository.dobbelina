"""Summaries of a crawl: summary.json, report.md and a filterable report.html."""

from __future__ import annotations

import html
import json
from collections import Counter
from pathlib import Path

RANK = {"fail": 0, "warn": 1, "pass": 2, "skipped": 3}


def load_results(results_dir: Path) -> tuple[dict, list[dict]]:
    run = {}
    if (results_dir / "run.json").exists():
        run = json.loads((results_dir / "run.json").read_text(encoding="utf-8"))
    sites = []
    for p in sorted((results_dir / "sites").glob("*.json")):
        try:
            sites.append(json.loads(p.read_text(encoding="utf-8")))
        except ValueError:
            continue
    sites.sort(key=lambda s: (RANK.get(s.get("status"), 9), s.get("site", "")))
    return run, sites


def diff_baseline(sites: list[dict], baseline: dict | None) -> dict:
    if not baseline:
        return {}
    before = {s["site"]: s for s in baseline.get("sites", [])}
    out = {"regressed": [], "fixed": [], "new_issues": {}}
    for s in sites:
        b = before.get(s["site"])
        if not b:
            continue
        if RANK[s["status"]] < RANK.get(b["status"], 9):
            out["regressed"].append({"site": s["site"], "was": b["status"], "now": s["status"], "message": s["message"]})
        elif RANK[s["status"]] > RANK.get(b["status"], 9) and b["status"] == "fail":
            out["fixed"].append({"site": s["site"], "was": b["status"], "now": s["status"]})
        new = sorted({i["code"] for i in s["issues"] if i["severity"] != "info"} - set(b.get("codes", [])))
        if new:
            out["new_issues"][s["site"]] = new
    return out


def summarise(run: dict, sites: list[dict], baseline: dict | None = None) -> dict:
    status = Counter(s["status"] for s in sites)
    codes = Counter(i["code"] for s in sites for i in s["issues"] if i["severity"] != "info")
    areas = Counter(i["area"] for s in sites for i in s["issues"] if i["severity"] == "error")
    return {
        "run": {k: run.get(k) for k in ("started", "finished", "kodi", "addon_version", "options", "flaresolverr",
                                        "addon_findings")},
        "totals": {"sites": len(sites), **{k: status.get(k, 0) for k in ("pass", "warn", "fail")}},
        "broken_areas": dict(areas.most_common()),
        "issue_codes": dict(codes.most_common()),
        "sites": [
            {"site": s["site"], "title": s.get("title"), "status": s["status"], "message": s["message"],
             "hint": s.get("hint"), "playback_started": s.get("playback_started"),
             "codes": sorted({i["code"] for i in s["issues"] if i["severity"] != "info"})}
            for s in sites
        ],
        "changes": diff_baseline(sites, baseline),
    }


def to_markdown(summary: dict, sites: list[dict]) -> str:
    t = summary["totals"]
    run = summary["run"]
    k = run.get("kodi") or {}
    lines = [
        "# Cumination in Kodi — e2e crawl",
        "",
        f"Kodi {k.get('major', '?')}.{k.get('minor', '?')} · Cumination {run.get('addon_version', '?')} · "
        f"{(run.get('started') or '')[:16]}",
        "",
        f"**{t['sites']} sites:** {t['fail']} broken · {t['warn']} with problems · {t['pass']} clean",
        "",
    ]
    ch = summary.get("changes") or {}
    if ch.get("regressed"):
        lines += ["## Newly broken since last run", ""]
        lines += [f"- **{r['site']}** ({r['was']} → {r['now']}): {r['message']}" for r in ch["regressed"]]
        lines.append("")
    if ch.get("fixed"):
        lines += ["## Fixed since last run", "", ", ".join(f"**{r['site']}**" for r in ch["fixed"]), ""]
    af = run.get("addon_findings") or {}
    if af:
        lines += ["## Addon-wide", ""]
        for k, vals in af.items():
            for v in vals[:5]:
                lines.append(f"- `{k}`: {v if isinstance(v, str) else json.dumps(v)}")
        lines.append("")
    fails = [s for s in sites if s["status"] == "fail"]
    if fails:
        lines += ["## Broken", "", "| Site | Problem |", "|---|---|"]
        for s in fails:
            msg = s["message"].replace("|", "/")
            lines.append(f"| {s['site']} | {msg[:180]} |")
        lines.append("")
    warns = [s for s in sites if s["status"] == "warn"]
    if warns:
        lines += ["## Works, with problems", "", "| Site | Problems |", "|---|---|"]
        for s in warns:
            codes = ", ".join(sorted({i["code"] for i in s["issues"] if i["severity"] == "warn"}))
            lines.append(f"| {s['site']} | {codes} |")
        lines.append("")
    if summary["issue_codes"]:
        lines += ["## Most common problems", ""]
        lines += [f"- `{c}` × {n}" for c, n in list(summary["issue_codes"].items())[:15]]
    return "\n".join(lines) + "\n"


CSS = """
:root{--bg:#fafaf9;--fg:#1c1917;--muted:#78716c;--card:#fff;--line:#e7e5e4;--fail:#b91c1c;--failbg:#fef2f2;
--warn:#a16207;--warnbg:#fefce8;--pass:#15803d;--passbg:#f0fdf4;--info:#475569;--code:#f5f5f4}
@media (prefers-color-scheme:dark){:root{--bg:#0c0a09;--fg:#e7e5e4;--muted:#a8a29e;--card:#1c1917;--line:#292524;
--fail:#f87171;--failbg:#2a1414;--warn:#facc15;--warnbg:#2a2410;--pass:#4ade80;--passbg:#10231a;--info:#94a3b8;--code:#292524}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px}h1{font-size:22px;margin:0 0 4px}.muted{color:var(--muted)}
.tiles{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}.tile{background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:10px 16px;min-width:120px}.tile b{font-size:24px;display:block}
.bar{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0;align-items:center}button,input,select{font:inherit;
background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:6px 10px}
button.on{outline:2px solid var(--fg)}input{flex:1;min-width:180px}
details{background:var(--card);border:1px solid var(--line);border-radius:10px;margin:8px 0}
summary{cursor:pointer;padding:10px 14px;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.badge{font-size:12px;font-weight:600;border-radius:6px;padding:1px 8px;text-transform:uppercase}
.fail{color:var(--fail);background:var(--failbg)}.warn{color:var(--warn);background:var(--warnbg)}
.pass{color:var(--pass);background:var(--passbg)}.info{color:var(--info);background:var(--code)}
.body{padding:0 14px 12px}.iss{margin:6px 0;padding:6px 10px;border-left:3px solid var(--line)}
.iss.error{border-color:var(--fail)}.iss.warn{border-color:var(--warn)}.iss.info{border-color:var(--info)}
code{background:var(--code);padding:0 4px;border-radius:4px;font-size:12px}
ul.ex{margin:4px 0 0;padding-left:18px;color:var(--muted);font-size:12px;word-break:break-all}
table{border-collapse:collapse;width:100%;font-size:12px}td,th{border-bottom:1px solid var(--line);padding:4px 6px;
text-align:left;vertical-align:top}.msg{flex:1;min-width:200px}.chg{background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:10px 14px;margin:8px 0}
"""

JS = """
const state={status:'all',q:'',area:''};
function apply(){document.querySelectorAll('details.site').forEach(d=>{
 const okS=state.status==='all'||d.dataset.status===state.status;
 const okQ=!state.q||d.dataset.text.includes(state.q);
 const okA=!state.area||d.dataset.areas.split(' ').includes(state.area);
 d.style.display=okS&&okQ&&okA?'':'none';});}
document.querySelectorAll('[data-f]').forEach(b=>b.onclick=()=>{state.status=b.dataset.f;
 document.querySelectorAll('[data-f]').forEach(x=>x.classList.toggle('on',x===b));apply();});
document.getElementById('q').oninput=e=>{state.q=e.target.value.toLowerCase();apply();};
document.getElementById('area').onchange=e=>{state.area=e.target.value;apply();};
"""


def _e(x) -> str:
    return html.escape(str(x if x is not None else ""))


def to_html(summary: dict, sites: list[dict]) -> str:
    t = summary["totals"]
    run = summary["run"]
    k = run.get("kodi") or {}
    areas = sorted({i["area"] for s in sites for i in s["issues"]})
    out = [f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
           f"<title>Kodi e2e report</title><style>{CSS}</style></head><body><main>",
           "<h1>Cumination in Kodi — e2e crawl</h1>",
           f"<div class=muted>Kodi {_e(k.get('major', '?'))}.{_e(k.get('minor', '?'))} · Cumination "
           f"{_e(run.get('addon_version', '?'))} · {_e((run.get('started') or '')[:16])}"
           f"{' · FlareSolverr on' if run.get('flaresolverr') else ''}</div>",
           "<div class=tiles>",
           f"<div class=tile><b>{t['sites']}</b>sites</div>",
           f"<div class=tile><b style='color:var(--fail)'>{t['fail']}</b>broken</div>",
           f"<div class=tile><b style='color:var(--warn)'>{t['warn']}</b>with problems</div>",
           f"<div class=tile><b style='color:var(--pass)'>{t['pass']}</b>clean</div></div>"]
    ch = summary.get("changes") or {}
    if ch.get("regressed") or ch.get("fixed"):
        out.append("<div class=chg>")
        if ch.get("regressed"):
            out.append("<b>Newly broken:</b> " + ", ".join(_e(r["site"]) for r in ch["regressed"]) + "<br>")
        if ch.get("fixed"):
            out.append("<b>Fixed:</b> " + ", ".join(_e(r["site"]) for r in ch["fixed"]))
        out.append("</div>")
    af = run.get("addon_findings") or {}
    if af:
        out.append("<div class=chg><b>Addon-wide:</b><ul class=ex>")
        for key, vals in af.items():
            for v in vals[:5]:
                out.append(f"<li><code>{_e(key)}</code> {_e(v if isinstance(v, str) else json.dumps(v))}</li>")
        out.append("</ul></div>")
    out.append("<div class=bar>")
    for f, lab in (("all", "All"), ("fail", "Broken"), ("warn", "Problems"), ("pass", "Clean")):
        out.append(f"<button data-f={f} class='{'on' if f == 'all' else ''}'>{lab}</button>")
    out.append("<select id=area><option value=''>any area</option>"
               + "".join(f"<option>{_e(a)}</option>" for a in areas) + "</select>")
    out.append("<input id=q placeholder='filter sites or problems…'></div>")

    for s in sites:
        text = " ".join([s["site"], s.get("title", ""), s["message"]] + [i["code"] + " " + i["message"] for i in s["issues"]]).lower()
        site_areas = " ".join(sorted({i["area"] for i in s["issues"] if i["severity"] != "info"}))
        out.append(f"<details class=site data-status={s['status']} data-areas='{_e(site_areas)}' data-text='{_e(text)}'>")
        out.append(f"<summary><span class='badge {s['status']}'>{s['status']}</span><b>{_e(s['site'])}</b>"
                   f"<span class='msg muted'>{_e(s['message'])}</span><span class=muted>{s.get('duration', 0):.0f}s</span></summary>")
        out.append("<div class=body>")
        if s.get("hint"):
            out.append(f"<p><b>Likely cause:</b> {_e(s['hint'])}</p>")
        for i in s["issues"]:
            sev = i["severity"]
            out.append(f"<div class='iss {sev}'><span class='badge {'fail' if sev == 'error' else sev}'>{_e(i['area'])}</span> "
                       f"<code>{_e(i['code'])}</code> {_e(i['message'])}"
                       f"{' <span class=muted>@ ' + _e(i['step']) + '</span>' if i.get('step') else ''}")
            if i.get("examples"):
                out.append("<ul class=ex>" + "".join(f"<li>{_e(x)}</li>" for x in i["examples"]) + "</ul>")
            out.append("</div>")
        if s.get("notes"):
            out.append("<p class=muted>" + "<br>".join(_e(n) for n in s["notes"]) + "</p>")
        if s.get("notifications"):
            out.append("<p><b>Popups the user saw:</b> " + "; ".join(_e(n) for n in s["notifications"]) + "</p>")
        if s.get("playback"):
            out.append("<p><b>Playback</b></p><table><tr><th>video</th><th>result</th><th>stream</th><th>time</th></tr>")
            for p in s["playback"]:
                res = "played" if p["ok"] else ("started, stalled" if p.get("started") else "failed")
                dims = f"{p.get('width')}x{p.get('height')} {p.get('codec') or ''}" if p.get("height") else ""
                out.append(f"<tr><td>{_e(p['target'][:60])}</td><td>{res}</td><td>{_e(p.get('resolved'))}<br>"
                           f"<span class=muted>{_e(dims)}</span></td><td>{p['elapsed']:.0f}s</td></tr>")
            out.append("</table>")
        out.append("<p><b>Steps</b></p><table><tr><th>step</th><th>result</th><th>items</th><th>time</th></tr>")
        for st in s.get("steps", []):
            res = "ok" if st["ok"] else _e(st.get("error"))
            out.append(f"<tr><td>{_e(st['target'][:70])}</td><td>{res}</td><td>{st['item_count']}</td>"
                       f"<td>{st['elapsed']:.1f}s</td></tr>")
        out.append("</table></div></details>")
    out.append(f"</main><script>{JS}</script></body></html>")
    return "\n".join(out)


def write_reports(results_dir: Path, baseline_path: Path | None = None) -> dict:
    run, sites = load_results(results_dir)
    baseline = None
    if baseline_path and baseline_path.exists():
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    summary = summarise(run, sites, baseline)
    (results_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (results_dir / "report.md").write_text(to_markdown(summary, sites), encoding="utf-8")
    (results_dir / "report.html").write_text(to_html(summary, sites), encoding="utf-8")
    return summary
