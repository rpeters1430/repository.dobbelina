#!/usr/bin/env python3
"""
Logo Validation Script
Validates all logos meet Cumination standards and site references are correct
"""

import re
import subprocess
from pathlib import Path
from collections import defaultdict

# Configuration
REPO_ROOT = Path(__file__).resolve().parent
IMAGES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "images"
SITES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"

# Standards
TARGET_SIZE = "256x256"
MAX_FILE_SIZE_KB = 50
OPTIMAL_FILE_SIZE_RANGE = (5, 30)


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def check_imagemagick():
    """Check if ImageMagick is available"""
    try:
        subprocess.run(["magick", "--version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_site_configs():
    """Extract all site configurations from site modules"""
    sites = {}
    # AdultSite(site_id, display_name, base_url, logo_file, about_file, ...)
    # We need to extract site_id (1st param) and logo_file (4th param)
    site_pattern = re.compile(
        r"site\s*=\s*AdultSite\s*\(\s*"
        r"['\"]([^'\"]+)['\"]"  # site_id (group 1)
        r"\s*,\s*['\"][^'\"]*['\"]"  # display_name
        r"\s*,\s*['\"][^'\"]*['\"]"  # base_url
        r"\s*,\s*['\"]([^'\"]+)['\"]",  # logo_file (group 2)
        re.DOTALL,
    )

    for site_file in SITES_DIR.glob("*.py"):
        if site_file.name in ("__init__.py", "soup_spec.py"):
            continue

        try:
            content = site_file.read_text(encoding="utf-8")
            content_single = content.replace("\n", " ")
            match = site_pattern.search(content_single)

            if match:
                site_id = match.group(1)
                logo_ref = match.group(2)
                sites[site_id] = {
                    "module": site_file.name,
                    "logo_ref": logo_ref,
                    "expected_local": f"{site_id}.png",
                }
        except Exception as e:
            print(
                f"{Colors.YELLOW}[WARNING]{Colors.ENDC} Error reading {site_file.name}: {e}"
            )

    return sites


def get_logo_files():
    """Get all logo files from images directory"""
    logos = {}

    for logo_file in IMAGES_DIR.glob("*"):
        if logo_file.is_file() and logo_file.suffix.lower() in (
            ".png",
            ".jpg",
            ".gif",
            ".jpeg",
        ):
            logos[logo_file.name] = {
                "path": logo_file,
                "size_bytes": logo_file.stat().st_size,
                "extension": logo_file.suffix.lower(),
            }

    return logos


def validate_logo_specs(logo_path, use_imagemagick=True):
    """Validate a single logo meets specifications"""
    issues = []

    # Check extension
    if logo_path.suffix.lower() != ".png":
        issues.append(f"Wrong format: {logo_path.suffix} (should be .png)")

    # Check file size
    size_kb = logo_path.stat().st_size / 1024
    if size_kb > MAX_FILE_SIZE_KB:
        issues.append(f"Too large: {size_kb:.1f} KB (max {MAX_FILE_SIZE_KB} KB)")
    elif size_kb < OPTIMAL_FILE_SIZE_RANGE[0]:
        issues.append(
            f"Too small: {size_kb:.1f} KB (min {OPTIMAL_FILE_SIZE_RANGE[0]} KB)"
        )
    elif size_kb > OPTIMAL_FILE_SIZE_RANGE[1]:
        issues.append(
            f"Suboptimal size: {size_kb:.1f} KB (optimal {OPTIMAL_FILE_SIZE_RANGE[0]}-{OPTIMAL_FILE_SIZE_RANGE[1]} KB)"
        )

    # Check dimensions with ImageMagick if available
    if use_imagemagick:
        try:
            result = subprocess.run(
                ["magick", "identify", "-format", "%wx%h", str(logo_path)],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                dims = result.stdout.strip()
                if dims != TARGET_SIZE:
                    issues.append(f"Wrong dimensions: {dims} (should be {TARGET_SIZE})")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            issues.append("Could not verify dimensions (ImageMagick not available)")

    return issues


def main():
    """Main validation routine"""
    print(f"{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}CUMINATION LOGO VALIDATION REPORT{Colors.ENDC}")
    print(f"{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

    has_imagemagick = check_imagemagick()
    if not has_imagemagick:
        print(
            f"{Colors.YELLOW}[WARNING]{Colors.ENDC} ImageMagick not found - dimension checks will be skipped"
        )
        print(
            f"            Install from: https://imagemagick.org/script/download.php\n"
        )

    # Load data
    sites = get_site_configs()
    logos = get_logo_files()

    print(f"Total site modules: {len(sites)}")
    print(f"Total logo files: {len([l for l in logos if not l.startswith('cum-')])}")
    print(
        f"Total cum-* utility icons: {len([l for l in logos if l.startswith('cum-')])}\n"
    )

    # Validation checks
    errors = []
    warnings = []
    info = []

    # Check 1: Sites with remote URLs instead of local files
    print(f"{Colors.BLUE}[CHECK 1]{Colors.ENDC} Sites using remote URLs...")
    remote_sites = []
    for site_id, config in sites.items():
        if config["logo_ref"].startswith("http://") or config["logo_ref"].startswith(
            "https://"
        ):
            remote_sites.append((site_id, config["logo_ref"], config["module"]))
            errors.append(f"Site '{site_id}' uses remote URL: {config['logo_ref']}")

    if remote_sites:
        print(
            f"  {Colors.RED}FAILED:{Colors.ENDC} {len(remote_sites)} sites use remote URLs"
        )
        for site_id, url, module in remote_sites[:5]:  # Show first 5
            print(f"    - {site_id} ({module}): {url[:60]}...")
        if len(remote_sites) > 5:
            print(f"    ... and {len(remote_sites) - 5} more")
    else:
        print(f"  {Colors.GREEN}PASSED{Colors.ENDC}")
    print()

    # Check 2: Sites missing logo files
    print(f"{Colors.BLUE}[CHECK 2]{Colors.ENDC} Sites with missing logo files...")
    missing_logos = []
    for site_id, config in sites.items():
        # Skip sites using remote URLs
        if config["logo_ref"].startswith("http"):
            continue

        if config["logo_ref"] not in logos:
            missing_logos.append((site_id, config["logo_ref"], config["module"]))
            errors.append(
                f"Site '{site_id}' references missing file: {config['logo_ref']}"
            )

    if missing_logos:
        print(
            f"  {Colors.RED}FAILED:{Colors.ENDC} {len(missing_logos)} sites missing logos"
        )
        for site_id, logo_file, module in missing_logos[:10]:
            print(f"    - {site_id} ({module}): expects {logo_file}")
        if len(missing_logos) > 10:
            print(f"    ... and {len(missing_logos) - 10} more")
    else:
        print(f"  {Colors.GREEN}PASSED{Colors.ENDC}")
    print()

    # Check 3: Orphaned logos (not referenced by any site)
    print(f"{Colors.BLUE}[CHECK 3]{Colors.ENDC} Orphaned logo files...")
    referenced_logos = {config["logo_ref"] for config in sites.values()}
    orphaned = []
    for logo_name in logos:
        if logo_name.startswith("cum-"):
            continue  # Skip utility icons
        if logo_name not in referenced_logos:
            orphaned.append(logo_name)
            warnings.append(f"Orphaned logo file: {logo_name}")

    if orphaned:
        print(
            f"  {Colors.YELLOW}WARNING:{Colors.ENDC} {len(orphaned)} orphaned logos found"
        )
        for logo_name in orphaned[:10]:
            print(f"    - {logo_name}")
        if len(orphaned) > 10:
            print(f"    ... and {len(orphaned) - 10} more")
    else:
        print(f"  {Colors.GREEN}PASSED{Colors.ENDC}")
    print()

    # Check 4: Logo file specifications
    print(f"{Colors.BLUE}[CHECK 4]{Colors.ENDC} Logo file specifications...")
    spec_issues = defaultdict(list)
    non_png_count = 0
    wrong_size_count = 0
    dimension_issues = 0

    for logo_name, logo_info in logos.items():
        if logo_name.startswith("cum-"):
            continue

        issues = validate_logo_specs(logo_info["path"], has_imagemagick)

        for issue in issues:
            spec_issues[logo_name].append(issue)

            if "Wrong format" in issue:
                non_png_count += 1
                warnings.append(f"{logo_name}: {issue}")
            elif "dimensions" in issue:
                dimension_issues += 1
                warnings.append(f"{logo_name}: {issue}")
            elif "Too large" in issue or "Too small" in issue:
                wrong_size_count += 1
                warnings.append(f"{logo_name}: {issue}")
            elif "Suboptimal" in issue:
                info.append(f"{logo_name}: {issue}")

    if spec_issues:
        print(f"  {Colors.YELLOW}ISSUES FOUND:{Colors.ENDC}")
        print(f"    - Non-PNG formats: {non_png_count}")
        print(f"    - Wrong dimensions: {dimension_issues}")
        print(f"    - File size issues: {wrong_size_count}")

        print(f"\n  Top 15 logos with issues:")
        for logo_name, issues in list(spec_issues.items())[:15]:
            print(f"    {logo_name}:")
            for issue in issues:
                print(f"      - {issue}")
        if len(spec_issues) > 15:
            print(f"    ... and {len(spec_issues) - 15} more")
    else:
        print(f"  {Colors.GREEN}PASSED{Colors.ENDC}")
    print()

    # Check 5: Filename conventions
    print(f"{Colors.BLUE}[CHECK 5]{Colors.ENDC} Logo filename conventions...")
    naming_issues = []
    for logo_name in logos:
        if logo_name.startswith("cum-"):
            continue

        # Check for uppercase in extension
        if any(c.isupper() for c in Path(logo_name).suffix):
            naming_issues.append(f"{logo_name}: Uppercase extension")
            warnings.append(f"Uppercase extension: {logo_name}")

        # Check for special characters (except hyphen and underscore)
        base_name = Path(logo_name).stem
        if not re.match(r"^[a-z0-9_-]+$", base_name):
            naming_issues.append(f"{logo_name}: Invalid characters in filename")
            warnings.append(f"Invalid filename characters: {logo_name}")

    if naming_issues:
        print(
            f"  {Colors.YELLOW}ISSUES:{Colors.ENDC} {len(naming_issues)} naming issues"
        )
        for issue in naming_issues[:10]:
            print(f"    - {issue}")
        if len(naming_issues) > 10:
            print(f"    ... and {len(naming_issues) - 10} more")
    else:
        print(f"  {Colors.GREEN}PASSED{Colors.ENDC}")
    print()

    # Summary
    print(f"{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}SUMMARY{Colors.ENDC}")
    print(f"{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

    print(f"{Colors.RED}Errors:{Colors.ENDC} {len(errors)}")
    print(f"{Colors.YELLOW}Warnings:{Colors.ENDC} {len(warnings)}")
    print(f"{Colors.BLUE}Info:{Colors.ENDC} {len(info)}\n")

    if errors:
        print(f"{Colors.RED}VALIDATION FAILED{Colors.ENDC}")
        print(f"\nCritical issues must be fixed:")
        print(f"  - {len(remote_sites)} sites use remote URLs (should be local files)")
        print(f"  - {len(missing_logos)} sites have missing logo files")
        return 1
    elif warnings:
        print(f"{Colors.YELLOW}VALIDATION PASSED WITH WARNINGS{Colors.ENDC}")
        print(f"\nRecommended improvements:")
        print(f"  - {len(orphaned)} orphaned logos should be removed")
        print(f"  - {non_png_count} non-PNG logos should be converted")
        print(f"  - {dimension_issues} logos have wrong dimensions")
        print(f"  - {wrong_size_count} logos have file size issues")
        return 0
    else:
        print(
            f"{Colors.GREEN}VALIDATION PASSED - ALL LOGOS MEET STANDARDS!{Colors.ENDC}"
        )
        return 0


if __name__ == "__main__":
    exit(main())
