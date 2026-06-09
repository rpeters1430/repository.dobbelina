#!/usr/bin/env python3
"""Human-friendly dispatcher for common Cumination site maintenance tasks.

This script is intentionally thin: it points to the existing specialized
scripts so older CI jobs and notes keep working while humans get one stable
place to start.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ToolCommand:
    name: str
    group: str
    script: Path
    summary: str
    example: str
    aliases: tuple[str, ...] = ()
    extra_args: tuple[str, ...] = ()


COMMANDS: tuple[ToolCommand, ...] = (
    ToolCommand(
        name="sites-list",
        aliases=("list-sites", "listed-sites"),
        group="Site inventory",
        script=ROOT / "list_implemented_sites.py",
        summary="List implemented site modules grouped by category.",
        example="python scripts/site_tool.py sites-list",
    ),
    ToolCommand(
        name="sites-status",
        aliases=("status",),
        group="Site inventory",
        script=ROOT / "scripts" / "generate_status_metrics.py",
        summary="Regenerate the canonical site status report.",
        example="python scripts/site_tool.py sites-status",
    ),
    ToolCommand(
        name="site-check",
        aliases=("check-site",),
        group="Site inventory",
        script=ROOT / "scripts" / "check_site_status.py",
        summary="Check one site URL/module status using the lightweight checker.",
        example="python scripts/site_tool.py site-check example",
    ),
    ToolCommand(
        name="candidates-rank",
        aliases=("rank-sites", "new-sites"),
        group="New sites",
        script=ROOT / "scripts" / "rank_new_sites.py",
        summary="Rank candidate sites that are not implemented yet.",
        example="python scripts/site_tool.py candidates-rank --limit 25",
    ),
    ToolCommand(
        name="candidates-validate",
        aliases=("validate-candidates",),
        group="New sites",
        script=ROOT / "scripts" / "validate_candidate_sites.py",
        summary="Live-check ranked candidates before implementation.",
        example="python scripts/site_tool.py candidates-validate --limit 10",
    ),
    ToolCommand(
        name="smoke-live",
        aliases=("live-smoke", "smoke"),
        group="Testing",
        script=ROOT / "scripts" / "live_smoke_test.py",
        summary="Run live Kodi-style site smoke flows and write JSON/Markdown reports.",
        example=(
            "python scripts/site_tool.py smoke-live --site hornyfap "
            "--steps main,list,categories,search,play"
        ),
    ),
    ToolCommand(
        name="smoke-unit",
        aliases=("unit-smoke",),
        group="Testing",
        script=ROOT / "scripts" / "run_smoke_tests.py",
        summary="Run generated pytest smoke tests for one or more sites.",
        example="python scripts/site_tool.py smoke-unit --site hornyfap",
    ),
    ToolCommand(
        name="smoke-generate",
        aliases=("generate-smoke",),
        group="Testing",
        script=ROOT / "scripts" / "generate_smoke_tests.py",
        summary="Generate pytest smoke files under tests/smoke_generated.",
        example="python scripts/site_tool.py smoke-generate --site hornyfap",
    ),
    ToolCommand(
        name="playwright-inspect",
        aliases=("inspect", "codegen"),
        group="Playwright",
        script=ROOT / "scripts" / "codegen.py",
        summary="Open a headed browser with ad blocking for selector/network research.",
        example="python scripts/site_tool.py playwright-inspect https://example.com --sniff",
    ),
    ToolCommand(
        name="playwright-listing",
        aliases=("listing-probe",),
        group="Playwright",
        script=ROOT / "scripts" / "playwright_listing_probe.py",
        summary="Probe live listing pages and count visible cards/video links.",
        example="python scripts/site_tool.py playwright-listing --url https://example.com/videos",
    ),
    ToolCommand(
        name="logos-validate",
        aliases=("check-logos", "validate-logos"),
        group="Logos",
        script=ROOT / "validate_logos.py",
        summary="Validate logo references, dimensions, formats, and missing files.",
        example="python scripts/site_tool.py logos-validate",
    ),
    ToolCommand(
        name="logos-fix",
        aliases=("fix-logos",),
        group="Logos",
        script=ROOT / "fix_all_logos.py",
        summary="Download/process missing logos and update references when requested.",
        example="python scripts/site_tool.py logos-fix --dry-run",
    ),
    ToolCommand(
        name="logos-process",
        aliases=("process-logos",),
        group="Logos",
        script=ROOT / "process_logos.py",
        summary="Use the older interactive logo processing menu.",
        example="python scripts/site_tool.py logos-process",
    ),
)


COMMAND_BY_NAME = {
    command_name: command
    for command in COMMANDS
    for command_name in (command.name, *command.aliases)
}


def grouped_commands() -> dict[str, list[ToolCommand]]:
    groups: dict[str, list[ToolCommand]] = {}
    for command in COMMANDS:
        groups.setdefault(command.group, []).append(command)
    return groups


def print_command_list() -> None:
    print("Recommended Cumination maintenance commands:\n")
    for group, commands in grouped_commands().items():
        print(group)
        for command in commands:
            print(f"  {command.name:<22} {command.summary}")
        print()
    print("Run a command with --help-after to see the wrapped script help:")
    print("  python scripts/site_tool.py smoke-live --help-after")


def print_workflows() -> None:
    print("Common workflows:\n")
    print("Add or evaluate a new site")
    print("  1. python scripts/site_tool.py candidates-rank")
    print("  2. python scripts/site_tool.py candidates-validate --limit 10")
    print("  3. python scripts/site_tool.py playwright-inspect <url> --sniff")
    print("  4. Add plugin.video.cumination/resources/lib/sites/<site>.py")
    print("  5. Add tests/sites/test_<site>.py")
    print("  6. python scripts/site_tool.py smoke-live --site <site>")
    print()
    print("Test an existing site")
    print("  1. python scripts/site_tool.py smoke-unit --site <site>")
    print("  2. python scripts/site_tool.py smoke-live --site <site> --steps main,list,categories,search,play")
    print()
    print("Investigate JavaScript/listing behavior")
    print("  1. python scripts/site_tool.py playwright-inspect <url> --sniff")
    print("  2. python scripts/site_tool.py playwright-listing --url <listing-url> --selector <css>")
    print()
    print("Logo maintenance")
    print("  1. python scripts/site_tool.py logos-validate")
    print("  2. python scripts/site_tool.py logos-fix --dry-run")
    print("  3. python scripts/site_tool.py logos-fix --yes")
    print()
    print("Check listed sites")
    print("  1. python scripts/site_tool.py sites-list")
    print("  2. python scripts/site_tool.py sites-status")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List recommended commands and exit.",
    )
    parser.add_argument(
        "--workflows",
        action="store_true",
        help="Print common maintenance workflows and exit.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        help="Command to run. Use --list to see choices.",
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments forwarded to the wrapped script.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        print_command_list()
        return 0

    if args.workflows:
        print_workflows()
        return 0

    if not args.command:
        print_workflows()
        print()
        print_command_list()
        return 0

    command = COMMAND_BY_NAME.get(args.command)
    if command is None:
        parser.error(f"unknown command: {args.command!r}. Run with --list for choices.")

    forwarded = list(args.args)
    if "--help-after" in forwarded:
        forwarded = ["--help" if arg == "--help-after" else arg for arg in forwarded]

    if not command.script.exists():
        print(f"Missing wrapped script: {command.script}", file=sys.stderr)
        return 2

    cmd = [sys.executable, str(command.script), *command.extra_args, *forwarded]
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
