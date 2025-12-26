#!/usr/bin/env python
"""
Analyze all site logos and site configurations for standardization
"""

import os
import re
import json
from collections import defaultdict

REPO_ROOT = r"C:\Users\James\Desktop\repository.dobbelina"
SITES_DIR = os.path.join(
    REPO_ROOT, "plugin.video.cumination", "resources", "lib", "sites"
)
IMAGES_DIR = os.path.join(REPO_ROOT, "plugin.video.cumination", "resources", "images")


def get_all_sites():
    """Extract all site configurations from site modules"""
    sites = {}
    site_pattern = re.compile(
        r"site\s*=\s*AdultSite\s*\(\s*['\"]([^'\"]+)['\"].*?['\"]([^'\"]+\.(png|jpg|gif|PNG))['\"]",
        re.DOTALL,
    )

    for filename in os.listdir(SITES_DIR):
        if filename.endswith(".py") and filename not in ("__init__.py", "soup_spec.py"):
            filepath = os.path.join(SITES_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Handle multi-line AdultSite declarations
                    content_single = content.replace("\n", " ")
                    match = site_pattern.search(content_single)
                    if match:
                        site_id = match.group(1)
                        logo_file = match.group(2)
                        sites[site_id] = {
                            "module": filename,
                            "logo": logo_file,
                            "logo_exists": os.path.exists(
                                os.path.join(IMAGES_DIR, logo_file)
                            ),
                        }
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    return sites


def get_all_logos():
    """Get all logo files from images directory"""
    logos = {}
    for filename in os.listdir(IMAGES_DIR):
        if filename.lower().endswith((".png", ".jpg", ".gif")):
            filepath = os.path.join(IMAGES_DIR, filename)
            file_size = os.path.getsize(filepath)
            logos[filename] = {
                "size_bytes": file_size,
                "size_kb": file_size / 1024,
                "extension": os.path.splitext(filename)[1].lower(),
            }
    return logos


def analyze():
    """Main analysis function"""
    sites = get_all_sites()
    logos = get_all_logos()

    print("=" * 80)
    print("CUMINATION LOGO STANDARDIZATION ANALYSIS")
    print("=" * 80)
    print()

    # Statistics
    print(f"Total site modules: {len(sites)}")
    print(f"Total logo files: {len(logos)}")
    print()

    # Sites missing logos
    missing_logos = []
    for site_id, info in sites.items():
        if not info["logo_exists"]:
            missing_logos.append((site_id, info["logo"], info["module"]))

    print(f"Sites with MISSING logos: {len(missing_logos)}")
    if missing_logos:
        print("-" * 80)
        for site_id, logo_file, module in sorted(missing_logos):
            print(f"  {site_id:20s} -> expects {logo_file:25s} (in {module})")
    print()

    # Logo file format distribution
    format_count = defaultdict(int)
    for logo_file, info in logos.items():
        format_count[info["extension"]] += 1

    print("Logo format distribution:")
    for fmt, count in sorted(format_count.items()):
        print(f"  {fmt:10s}: {count:3d} files")
    print()

    # File size distribution
    sizes_kb = sorted([info["size_kb"] for info in logos.values()])
    if sizes_kb:
        print("Logo file sizes (KB):")
        print(f"  Minimum:  {min(sizes_kb):8.1f} KB")
        print(f"  Maximum:  {max(sizes_kb):8.1f} KB")
        print(f"  Average:  {sum(sizes_kb) / len(sizes_kb):8.1f} KB")
        print(f"  Median:   {sizes_kb[len(sizes_kb) // 2]:8.1f} KB")
    print()

    # Orphaned logos (not referenced by any site)
    site_logos = {info["logo"] for info in sites.values()}
    orphaned = [
        logo
        for logo in logos.keys()
        if logo not in site_logos and not logo.startswith("cum-")
    ]

    print(f"Orphaned logos (not referenced by any site): {len(orphaned)}")
    if orphaned:
        print("-" * 80)
        for logo in sorted(orphaned):
            print(f"  {logo}")
    print()

    # Sites referencing logos that exist
    sites_with_logos = sum(1 for info in sites.values() if info["logo_exists"])
    print(f"Sites with existing logos: {sites_with_logos}/{len(sites)}")
    print()


if __name__ == "__main__":
    analyze()
