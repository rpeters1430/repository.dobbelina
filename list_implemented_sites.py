#!/usr/bin/env python3
"""List implemented Cumination site modules grouped by category."""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
SITES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"
SKIP_MODULES = {"__init__.py", "soup_spec.py"}


def clean_display_name(value: str) -> str:
    return re.sub(r"\[[^\]]+\]", "", value).strip()


def literal_string(node: ast.AST, constants: dict[str, str]) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return constants.get(node.id)
    return None


def module_string_constants(tree: ast.Module) -> dict[str, str]:
    constants: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        value = literal_string(node.value, constants)
        if value is None:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                constants[target.id] = value
    return constants


def extract_site(path: Path) -> dict[str, str] | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return None

    constants = module_string_constants(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        is_adult_site = (
            isinstance(func, ast.Name)
            and func.id == "AdultSite"
            or isinstance(func, ast.Attribute)
            and func.attr == "AdultSite"
        )
        if not is_adult_site or len(node.args) < 3:
            continue

        internal_name = literal_string(node.args[0], constants)
        display_name = literal_string(node.args[1], constants)
        url = literal_string(node.args[2], constants)
        if not internal_name or not display_name or not url:
            continue

        category = "Unknown"
        for keyword in node.keywords:
            if keyword.arg == "category":
                category = literal_string(keyword.value, constants) or category
                break

        return {
            "file": path.name,
            "internal_name": internal_name,
            "name": clean_display_name(display_name),
            "url": url,
            "category": category,
        }

    return None


def implemented_sites(sites_dir: Path = SITES_DIR) -> list[dict[str, str]]:
    sites: list[dict[str, str]] = []
    for path in sorted(sites_dir.glob("*.py")):
        if path.name in SKIP_MODULES:
            continue
        site = extract_site(path)
        if site:
            sites.append(site)
    return sites


def render_grouped(sites: list[dict[str, str]]) -> str:
    categories: dict[str, list[str]] = {}
    for site in sites:
        categories.setdefault(site["category"], []).append(site["name"])

    lines = [f"Scan complete. Found {len(sites)} sites.", "-" * 40]
    for category in sorted(categories):
        lines.append(f"### {category}")
        lines.append(", ".join(sorted(categories[category])))
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sites-dir",
        type=Path,
        default=SITES_DIR,
        help="Site module directory to scan.",
    )
    args = parser.parse_args()
    print(render_grouped(implemented_sites(args.sites_dir)))


if __name__ == "__main__":
    main()
