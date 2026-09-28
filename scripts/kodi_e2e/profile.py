#!/usr/bin/env python3
"""Build a clean, throwaway Kodi profile for end-to-end tests.

The profile is a directory used as ``$HOME`` for Kodi, so everything lands in
``<profile>/.kodi``. It contains:

* the addons from this repository (copied from the working tree, or unpacked
  from the ZIPs that ``build_repo_addons.py`` produces, which is what users
  actually install);
* every dependency resolved recursively from the official Kodi addon
  repository, fetched from GitHub (``xbmc/repo-scripts``) so it works where
  ``mirrors.kodi.tv`` is not reachable;
* ``guisettings.xml`` with the web server / JSON-RPC enabled on localhost and
  nothing that pops up on first start;
* Cumination settings pre-seeded so the age gate and changelog do not block,
  and FlareSolverr wired in when a URL is given.

Binary addons (``inputstream.adaptive``) cannot come from GitHub; they come
from the distribution package (``kodi-inputstream-adaptive``).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]

# Addons that live in this repository.
LOCAL_ADDONS = (
    "plugin.video.cumination",
    "script.module.resolveurl",
    "script.module.resolveurl.xxx",
    "script.module.yt-dlp",
    "script.video.F4mProxy",
)
MAIN_ADDON = "plugin.video.cumination"

# The official repo is layered: an Omega install sees Omega + Nexus + Matrix
# addons. Newest branch wins.
REPO_SCRIPTS = "https://github.com/xbmc/repo-scripts.git"
BRANCHES_BY_MAJOR = {
    19: ["matrix"],
    20: ["nexus", "matrix"],
    21: ["omega", "nexus", "matrix"],
    22: ["piers", "omega", "nexus", "matrix"],
}

# Provided by Kodi itself or by distro packages, never fetched.
SYSTEM_ADDON_PREFIXES = ("xbmc.", "kodi.")
BINARY_ADDONS = ("inputstream.adaptive", "inputstream.ffmpegdirect", "inputstream.rtmp")
SYSTEM_ADDON_DIRS = (
    Path("/usr/share/kodi/addons"),
    Path("/usr/lib/x86_64-linux-gnu/kodi/addons"),
    Path("/usr/lib/aarch64-linux-gnu/kodi/addons"),
    Path("/usr/lib/kodi/addons"),
)

WEB_PORT_DEFAULT = 8080


def log(msg: str) -> None:
    print(f"[profile] {msg}", flush=True)


def detect_kodi_major(kodi_bin: str = "kodi") -> int:
    """Best effort: parse `kodi --version`, default to 21 (Omega)."""
    try:
        out = subprocess.run(
            [kodi_bin, "--version"], capture_output=True, text=True, timeout=20
        ).stdout
        for tok in out.replace("(", " ").split():
            head = tok.split(".")[0]
            if head.isdigit() and 17 <= int(head) <= 30:
                return int(head)
    except Exception:
        pass
    return 21


def read_requires(addon_dir: Path) -> list[tuple[str, bool]]:
    """Return [(addon_id, optional)] from addon.xml."""
    tree = ET.parse(addon_dir / "addon.xml")
    reqs = []
    for imp in tree.getroot().iter("import"):
        aid = imp.get("addon")
        if aid:
            reqs.append((aid, imp.get("optional", "false").lower() == "true"))
    return reqs


def addon_version(addon_dir: Path) -> str:
    return ET.parse(addon_dir / "addon.xml").getroot().get("version", "?")


def system_addon_present(aid: str) -> bool:
    return any((d / aid / "addon.xml").exists() for d in SYSTEM_ADDON_DIRS)


class RepoScripts:
    """Lazy sparse checkouts of xbmc/repo-scripts branches."""

    def __init__(self, cache: Path, branches: list[str]):
        self.cache = cache
        self.branches = branches
        self._index: dict[str, set[str]] = {}

    def _clone(self, branch: str) -> Path:
        dest = self.cache / f"repo-scripts-{branch}"
        if not (dest / ".git").exists():
            log(f"fetching index of xbmc/repo-scripts@{branch}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["git", "clone", "-q", "--filter=blob:none", "--no-checkout",
                 "--depth", "1", "-b", branch, REPO_SCRIPTS, str(dest)],
                check=True,
            )
            subprocess.run(["git", "-C", str(dest), "sparse-checkout", "init", "--no-cone"], check=True)
            subprocess.run(["git", "-C", str(dest), "sparse-checkout", "set", "--no-cone", "/README.md"], check=True)
            subprocess.run(["git", "-C", str(dest), "checkout", "-q"], check=True)
        return dest

    def _names(self, branch: str) -> set[str]:
        if branch not in self._index:
            dest = self._clone(branch)
            out = subprocess.run(
                ["git", "-C", str(dest), "ls-tree", "--name-only", "HEAD"],
                capture_output=True, text=True, check=True,
            ).stdout
            self._index[branch] = set(out.split())
        return self._index[branch]

    def fetch(self, aid: str) -> Path | None:
        for branch in self.branches:
            try:
                names = self._names(branch)
            except subprocess.CalledProcessError as exc:
                log(f"WARNING: cannot read branch {branch}: {exc}")
                continue
            if aid in names:
                dest = self._clone(branch)
                listed = subprocess.run(
                    ["git", "-C", str(dest), "sparse-checkout", "list"],
                    capture_output=True, text=True,
                ).stdout.split()
                if f"/{aid}/" not in listed:
                    subprocess.run(
                        ["git", "-C", str(dest), "sparse-checkout", "add", f"/{aid}/"],
                        check=True,
                    )
                return dest / aid
        return None


def unpack_built_zips(zip_dir: Path, into: Path) -> dict[str, Path]:
    found = {}
    for z in sorted(zip_dir.rglob("*.zip")):
        with zipfile.ZipFile(z) as zf:
            top = {n.split("/")[0] for n in zf.namelist() if "/" in n}
            if len(top) != 1:
                continue
            aid = top.pop()
            if aid not in LOCAL_ADDONS:
                continue
            zf.extractall(into)
            found[aid] = into / aid
    return found


def write_settings_xml(path: Path, values: dict[str, str], raw: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ['<settings version="2">']
    for key, val in values.items():
        lines.append(f'    <setting id="{escape(key)}">{escape(str(val))}</setting>')
    if raw:
        lines.append(raw)
    lines.append("</settings>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def gui_settings(port: int) -> dict[str, str]:
    return {
        # JSON-RPC over HTTP (localhost only, no auth: throwaway profile)
        "services.webserver": "true",
        "services.webserverport": str(port),
        "services.webserverauthentication": "false",
        "services.webserverusername": "kodi",
        "services.webserverpassword": "",
        # event server / TCP JSON-RPC use fixed ports: off, so several Kodi
        # instances (--workers) can run side by side
        "services.esenabled": "false",
        "services.zeroconf": "false",
        "services.upnp": "false",
        "services.airplay": "false",
        # nothing that interrupts an unattended run
        "general.addonupdates": "2",
        "general.addonnotifications": "false",
        "addons.unknownsources": "true",
        "screensaver.mode": "",
        "powermanagement.displaysoff": "0",
        "powermanagement.shutdowntime": "0",
        "videoplayer.adjustrefreshrate": "0",
        "lookandfeel.enablerssfeeds": "false",
        "audiooutput.guisoundmode": "0",
    }


ADVANCED_SETTINGS = """<advancedsettings version="1.0">
    <loglevel hide="false">{loglevel}</loglevel>
    <network>
        <curlclienttimeout>20</curlclienttimeout>
        <curllowspeedtime>20</curllowspeedtime>
        <curlretries>1</curlretries>
    </network>
    <imageres>540</imageres>
    <fanartres>720</fanartres>
</advancedsettings>
"""


def build_profile(
    profile: Path,
    *,
    source: str = "tree",
    zip_dir: Path | None = None,
    kodi_major: int | None = None,
    web_port: int = WEB_PORT_DEFAULT,
    flaresolverr_url: str | None = None,
    debug_log: bool = False,
    cache_dir: Path | None = None,
    extra_addon_settings: dict[str, str] | None = None,
    extra_site_modules: list[Path] | None = None,
) -> dict:
    """Create the profile. Returns a manifest describing what was installed."""
    kodi_major = kodi_major or detect_kodi_major()
    branches = BRANCHES_BY_MAJOR.get(kodi_major, BRANCHES_BY_MAJOR[21])
    kodi_home = profile / ".kodi"
    addons_dir = kodi_home / "addons"
    userdata = kodi_home / "userdata"
    if kodi_home.exists():
        shutil.rmtree(kodi_home)
    addons_dir.mkdir(parents=True)
    (userdata / "addon_data").mkdir(parents=True)

    manifest: dict = {"kodi_major": kodi_major, "branches": branches, "addons": {}, "missing": []}

    # 1. addons from this repo
    local: dict[str, Path] = {}
    if source == "zip":
        if zip_dir is None:
            zip_dir = profile / "_built"
            log("building addon ZIPs with build_repo_addons.py")
            subprocess.run(
                [sys.executable, str(ROOT / "build_repo_addons.py"), "--out", str(zip_dir)],
                check=True, cwd=ROOT,
            )
        local = unpack_built_zips(zip_dir, addons_dir)
    else:
        for aid in LOCAL_ADDONS:
            src = ROOT / aid
            if (src / "addon.xml").exists():
                shutil.copytree(src, addons_dir / aid, ignore=shutil.ignore_patterns(
                    "__pycache__", "*.pyc", ".git", "tests", "cookies.lwp"))
                local[aid] = addons_dir / aid
    if MAIN_ADDON not in local:
        raise SystemExit(f"{MAIN_ADDON} not found (source={source})")
    # test-only site modules (self-test) go into the profile copy, never the repo
    for mod in extra_site_modules or []:
        shutil.copy2(mod, local[MAIN_ADDON] / "resources" / "lib" / "sites" / mod.name)

    # 2. resolve dependencies starting from the main addon
    repo = RepoScripts(cache_dir or (ROOT / ".cache" / "kodi_e2e"), branches)
    installed: dict[str, Path] = {}
    queue = [(MAIN_ADDON, False)]
    seen = set()
    while queue:
        aid, optional = queue.pop(0)
        if aid in seen:
            continue
        seen.add(aid)
        if aid.startswith(SYSTEM_ADDON_PREFIXES):
            continue
        if aid in BINARY_ADDONS:
            present = system_addon_present(aid)
            manifest["addons"][aid] = {"source": "system", "present": present}
            if not present:
                (manifest["missing"]).append(aid)
                log(f"WARNING: binary addon {aid} not installed on this system "
                    f"(install kodi-{aid.replace('.', '-')}); HLS/DASH playback may differ")
            continue
        if aid in local:
            path = local[aid]
            origin = "repo-" + source
        elif system_addon_present(aid):
            manifest["addons"][aid] = {"source": "system"}
            continue
        else:
            fetched = repo.fetch(aid)
            if fetched is None or not (fetched / "addon.xml").exists():
                manifest["missing"].append(aid)
                log(f"{'note' if optional else 'WARNING'}: dependency {aid} not found")
                continue
            path = addons_dir / aid
            shutil.copytree(fetched, path)
            origin = "repo-scripts"
        installed[aid] = path
        manifest["addons"][aid] = {"source": origin, "version": addon_version(path)}
        for dep, dep_optional in read_requires(path):
            queue.append((dep, dep_optional))

    # local addons nobody required (e.g. F4mProxy) are still useful to have
    for aid, path in local.items():
        if aid not in manifest["addons"]:
            manifest["addons"][aid] = {"source": "repo-" + source, "version": addon_version(path)}
            installed[aid] = path

    # 3. Kodi settings
    # Kodi rejects a guisettings.xml without <resolutions> (and logs an error)
    write_settings_xml(userdata / "guisettings.xml", gui_settings(web_port), raw="    <resolutions />")
    (userdata / "advancedsettings.xml").write_text(
        ADVANCED_SETTINGS.format(loglevel=1 if debug_log else 0), encoding="utf-8"
    )

    # 4. Cumination settings: skip blocking first-run dialogs
    version = addon_version(installed[MAIN_ADDON])
    cum = {
        "cuminationage": "true",
        "changelog_seen_version": version,
        "telemetry_enabled": "false",
    }
    if flaresolverr_url:
        cum.update({"fs_enable": "true", "fs_host": flaresolverr_url, "fs_allow_remote": "true"})
    cum.update(extra_addon_settings or {})
    write_settings_xml(userdata / "addon_data" / MAIN_ADDON / "settings.xml", cum)

    manifest["main_version"] = version
    manifest["enable"] = sorted(installed)  # to enable over JSON-RPC after start
    (profile / "kodi_e2e_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    log(f"profile ready at {kodi_home} ({len(installed)} addons, Kodi {kodi_major})")
    if manifest["missing"]:
        log(f"missing: {', '.join(manifest['missing'])}")
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("profile", type=Path, help="directory to use as Kodi's $HOME")
    ap.add_argument("--source", choices=["tree", "zip"], default="tree",
                    help="copy addons from the working tree, or build+unpack release ZIPs")
    ap.add_argument("--zip-dir", type=Path, help="use already-built ZIPs from this dir")
    ap.add_argument("--kodi-major", type=int, help="Kodi major version (default: detect)")
    ap.add_argument("--port", type=int, default=WEB_PORT_DEFAULT)
    ap.add_argument("--flaresolverr", help="FlareSolverr URL, e.g. http://127.0.0.1:8191/v1")
    ap.add_argument("--debug-log", action="store_true", help="Kodi debug logging")
    args = ap.parse_args(argv)
    build_profile(args.profile, source=args.source, zip_dir=args.zip_dir,
                  kodi_major=args.kodi_major, web_port=args.port,
                  flaresolverr_url=args.flaresolverr, debug_log=args.debug_log)


if __name__ == "__main__":
    main()
