#!/usr/bin/env python3
"""Token-efficient site inspection CLI using vercel-labs/agent-browser.

This tool is strictly for developer/agent investigation and debugging.
NEVER use agent-browser inside plugin.video.cumination site modules.

agent-browser connects via CDP and produces compact accessibility snapshots
with short-lived references (@e1, @e2) rather than dumping large DOM trees,
saving context window tokens while investigating broken sites or exploring new ones.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Ensure UTF-8 output on all platforms (especially Windows)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"


def find_agent_browser_cmd() -> list[str]:
    """Find the agent-browser executable or fallback to npx."""
    bin_dir = SCRIPTS_DIR / "node_modules" / ".bin"
    if os.name == "nt":
        cmd_path = bin_dir / "agent-browser.cmd"
        if cmd_path.is_file():
            return [str(cmd_path)]
    else:
        unix_path = bin_dir / "agent-browser"
        if unix_path.is_file():
            return [str(unix_path)]

    which_agent = shutil.which("agent-browser")
    if which_agent:
        return [which_agent]

    which_npx = shutil.which("npx")
    if which_npx:
        return [which_npx, "agent-browser"]

    raise FileNotFoundError(
        "agent-browser not found. Run 'npm install' inside the scripts directory or 'npm install -g agent-browser'."
    )


def run_agent_cmd(base_cmd: list[str], subargs: list[str], check: bool = False) -> tuple[int, str]:
    """Run an agent-browser command avoiding pipe-deadlocks on daemon processes."""
    cmd = base_cmd + subargs
    use_shell = os.name == "nt"

    with tempfile.TemporaryFile() as tmp_out:
        proc = subprocess.run(
            cmd,
            cwd=str(SCRIPTS_DIR),
            stdin=subprocess.DEVNULL,
            stdout=tmp_out,
            stderr=subprocess.STDOUT,
            shell=use_shell,
            check=False,
        )
        tmp_out.seek(0)
        output = tmp_out.read().decode("utf-8", errors="replace").strip()

    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed (exit {proc.returncode}): {' '.join(cmd)}\n{output}")

    return proc.returncode, output


def probe_site(
    url: str,
    *,
    interactive: bool = True,
    include_urls: bool = True,
    compact: bool = False,
    depth: int | None = None,
    selector: str | None = None,
    headed: bool = False,
    click_ref: str | None = None,
    wait_ms: int = 2000,
    screenshot_path: str | None = None,
    dump_html_path: str | None = None,
    keep_open: bool = False,
) -> str:
    """Run agent-browser session against a URL and return snapshot."""
    base_cmd = find_agent_browser_cmd()

    open_args = ["open", url]
    if headed:
        open_args = ["--headed"] + open_args

    print(f"[*] Navigating to {url} via agent-browser...")
    rc, out = run_agent_cmd(base_cmd, open_args)
    if out:
        print(f"    {out}")

    if wait_ms > 0:
        run_agent_cmd(base_cmd, ["wait", str(wait_ms)])

    if click_ref:
        print(f"[*] Clicking {click_ref}...")
        c_rc, c_out = run_agent_cmd(base_cmd, ["click", click_ref])
        if c_out:
            print(f"    {c_out}")
        time.sleep(1.0)

    if screenshot_path:
        print(f"[*] Capturing screenshot to {screenshot_path}...")
        s_rc, s_out = run_agent_cmd(base_cmd, ["screenshot", screenshot_path])
        if s_out:
            print(f"    {s_out}")

    if dump_html_path:
        print(f"[*] Dumping HTML to {dump_html_path}...")
        html_sel = selector or "html"
        html_args = ["get", "html", html_sel]
        h_rc, h_out = run_agent_cmd(base_cmd, html_args)
        Path(dump_html_path).write_text(h_out, encoding="utf-8", errors="replace")

    snapshot_args = ["snapshot"]
    if interactive:
        snapshot_args.append("-i")
    if include_urls:
        snapshot_args.append("-u")
    if compact:
        snapshot_args.append("-c")
    if depth is not None:
        snapshot_args.extend(["-d", str(depth)])
    if selector:
        snapshot_args.extend(["-s", selector])

    print("[*] Generating accessibility snapshot with element refs...")
    s_rc, snap_output = run_agent_cmd(base_cmd, snapshot_args)

    if not keep_open:
        run_agent_cmd(base_cmd, ["close"])

    return snap_output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Probe a website using agent-browser (token-efficient accessibility snapshot + refs)."
    )
    parser.add_argument("url", help="Target website URL to probe")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Capture full accessibility tree instead of interactive-only (-i)",
    )
    parser.add_argument(
        "--no-urls",
        action="store_true",
        help="Exclude element URLs/hrefs from snapshot output",
    )
    parser.add_argument(
        "-c",
        "--compact",
        action="store_true",
        help="Compact tree layout",
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=None,
        help="Limit accessibility tree depth",
    )
    parser.add_argument(
        "-s",
        "--selector",
        default=None,
        help="Scope snapshot to a CSS selector (e.g. '.video-card', '#main')",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in visible headed mode",
    )
    parser.add_argument(
        "--click",
        default=None,
        help="Click an element ref or selector before taking snapshot (e.g. '@e1' or 'button.play')",
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=2000,
        help="Milliseconds to wait after navigation (default: 2000)",
    )
    parser.add_argument(
        "--screenshot",
        default=None,
        help="Path to save page screenshot",
    )
    parser.add_argument(
        "--dump-html",
        default=None,
        help="Path to dump rendered page or selector HTML",
    )
    parser.add_argument(
        "--keep-open",
        action="store_true",
        help="Do not close the browser session on exit (allows follow-up CLI calls)",
    )

    args = parser.parse_args(argv)

    try:
        snapshot = probe_site(
            args.url,
            interactive=not args.full,
            include_urls=not args.no_urls,
            compact=args.compact,
            depth=args.depth,
            selector=args.selector,
            headed=args.headed,
            click_ref=args.click,
            wait_ms=args.wait,
            screenshot_path=args.screenshot,
            dump_html_path=args.dump_html,
            keep_open=args.keep_open,
        )
        print("\n--- Snapshot ---")
        print(snapshot)
        return 0
    except Exception as exc:
        print(f"[!] Error running agent-browser probe: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
