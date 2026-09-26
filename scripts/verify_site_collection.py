#!/usr/bin/env python3
"""Treat missing site reports as a collection failure, not a healthy run."""

import json
import sys
from pathlib import Path

from scripts.generate_smoke_matrix import discover_site_names, load_profiles, build_strict_matrix


SITE_ALIASES = {
    "poldertube": "nltubes",
    "rlc": "reallifecam",
    "xoxo": "xoxostream",
}


def missing_sites(broad, strict):
    expected_broad = set(discover_site_names())
    expected_strict = {item["site"] for item in build_strict_matrix(load_profiles())["include"]}
    seen_broad = {
        SITE_ALIASES.get(site["site"], site["site"])
        for site in broad.get("sites", [])
    }
    seen_strict = {site for site, data in strict.get("sites", {}).items()
                   if data.get("state") != "NOT_TESTED"}
    return sorted(expected_broad - seen_broad), sorted(expected_strict - seen_strict)


def main():
    broad = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    strict = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    missing_broad, missing_strict = missing_sites(broad, strict)
    if missing_broad or missing_strict:
        print(f"Missing broad reports: {', '.join(missing_broad) or 'none'}")
        print(f"Missing strict reports: {', '.join(missing_strict) or 'none'}")
        return 1
    print("All expected sites returned a report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
