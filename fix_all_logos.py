#!/usr/bin/env python3
"""
Comprehensive Logo Fix Script
- Verifies all site logos
- Downloads missing logos from actual sites
- Updates site code to use local PNG files
- Processes and optimizes all logos

Usage:
  python3 fix_all_logos.py              # Interactive mode
  python3 fix_all_logos.py --yes        # Automatic mode (no confirmation)
  python3 fix_all_logos.py --dry-run    # Show what would be done without making changes
"""

import os
import sys
import re
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from bs4 import BeautifulSoup
import time
import argparse

# Configuration
REPO_ROOT = Path(os.environ.get("REPO_ROOT", Path(__file__).resolve().parent))
IMAGES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "images"
SITES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"
TEMP_DIR = REPO_ROOT / "temp_logos"

# Standards
TARGET_SIZE = (256, 256)
MAX_FILE_SIZE_KB = 50

# Ensure directories exist
TEMP_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def check_dependencies():
    """Check if required tools are installed"""
    missing = []

    # Check ImageMagick
    try:
        result = subprocess.run(["magick", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] ImageMagick is installed")
        else:
            missing.append("ImageMagick")
    except FileNotFoundError:
        missing.append("ImageMagick")

    # Check BeautifulSoup4 (imported above)
    print("[OK] BeautifulSoup4 is available")

    if missing:
        print(f"\n[ERROR] Missing dependencies: {', '.join(missing)}")
        print("Install ImageMagick from: https://imagemagick.org/script/download.php")
        return False

    return True


def download_file(url, output_path, timeout=10):
    """Download a file from URL"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            with open(output_path, "wb") as f:
                f.write(data)
        return True
    except Exception as e:
        print(f"    [ERROR] Download failed: {e}")
        return False


def process_logo(input_path, output_path):
    """Process logo: convert to PNG, resize to 256x256, optimize"""
    try:
        cmd = [
            "magick",
            str(input_path),
            "-background", "none",
            "-gravity", "center",
            "-resize", "256x256",
            "-extent", "256x256",
            "-strip",
            str(output_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"    [ERROR] ImageMagick failed: {result.stderr}")
            return False

        # Try to optimize with pngquant if available
        try:
            pngquant_cmd = [
                "pngquant", "--quality=80-95", "--ext", ".png",
                "--force", str(output_path)
            ]
            subprocess.run(pngquant_cmd, capture_output=True, timeout=10)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass  # pngquant is optional

        file_size_kb = output_path.stat().st_size / 1024
        print(f"    [SUCCESS] Processed: {output_path.name} ({file_size_kb:.1f} KB)")
        return True

    except Exception as e:
        print(f"    [ERROR] Processing failed: {e}")
        return False


def get_favicon_from_site(base_url):
    """Try to extract favicon/logo URL from a website"""
    favicon_urls = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        req = urllib.request.Request(base_url, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')

            # Look for various favicon/logo link tags
            for rel in ['icon', 'shortcut icon', 'apple-touch-icon', 'logo']:
                links = soup.find_all('link', rel=lambda x: x and rel in x.lower())
                for link in links:
                    href = link.get('href')
                    if href:
                        # Make absolute URL
                        if href.startswith('//'):
                            href = 'https:' + href
                        elif href.startswith('/'):
                            from urllib.parse import urljoin
                            href = urljoin(base_url, href)
                        elif not href.startswith('http'):
                            from urllib.parse import urljoin
                            href = urljoin(base_url, href)

                        # Prefer PNG/JPG over ICO, and larger sizes
                        if any(ext in href.lower() for ext in ['.png', '.jpg', '.jpeg']):
                            favicon_urls.insert(0, href)
                        else:
                            favicon_urls.append(href)

            # Fallback: try standard /favicon.ico
            if not favicon_urls:
                from urllib.parse import urljoin
                favicon_urls.append(urljoin(base_url, '/favicon.ico'))

    except Exception as e:
        print(f"    [WARNING] Could not parse {base_url}: {e}")
        # Fallback to standard favicon.ico
        from urllib.parse import urljoin
        favicon_urls.append(urljoin(base_url, '/favicon.ico'))

    return favicon_urls


def extract_all_sites():
    """Extract all site configurations from site modules"""
    sites = []

    # Pattern to match AdultSite declarations
    # AdultSite('site_id', 'display', 'base_url', 'logo_file', ...)
    pattern = re.compile(
        r'(site\d*)\s*=\s*AdultSite\s*\(\s*'
        r'["\']([^"\']+)["\']\s*,\s*'  # site_id (group 2)
        r'["\'][^"\']*["\']\s*,\s*'     # display_name
        r'["\']([^"\']+)["\']\s*,\s*'   # base_url (group 3)
        r'["\']([^"\']+)["\']',          # logo_file (group 4)
        re.MULTILINE
    )

    for site_file in sorted(SITES_DIR.glob("*.py")):
        if site_file.name in ("__init__.py", "soup_spec.py"):
            continue

        try:
            content = site_file.read_text(encoding='utf-8')

            for match in pattern.finditer(content):
                var_name = match.group(1)
                site_id = match.group(2)
                base_url = match.group(3)
                logo_file = match.group(4)

                is_remote = logo_file.startswith('http://') or logo_file.startswith('https://')
                expected_filename = f"{site_id}.png"

                # Check if local file exists
                # First check the convention (site_id.png)
                local_exists = (IMAGES_DIR / expected_filename).exists()

                # If not remote and doesn't exist, check if the referenced file exists
                # (e.g., vvp.jpg when we expect viralvideosporno.png)
                current_file_exists = False
                needs_extension_fix = False
                if not is_remote:
                    current_file_exists = (IMAGES_DIR / logo_file).exists()
                    # Check if same file exists with .png extension
                    png_version = Path(logo_file).with_suffix('.png')
                    if (IMAGES_DIR / png_version).exists() and not current_file_exists:
                        needs_extension_fix = True

                sites.append({
                    'site_id': site_id,
                    'var_name': var_name,
                    'base_url': base_url,
                    'logo_file': logo_file,
                    'is_remote': is_remote,
                    'expected_filename': expected_filename,
                    'local_exists': local_exists,
                    'current_file_exists': current_file_exists,
                    'needs_extension_fix': needs_extension_fix,
                    'module': site_file.name,
                    'module_path': site_file,
                })

        except Exception as e:
            print(f"[WARNING] Error reading {site_file.name}: {e}")

    return sites


def download_and_process_logo(site_info):
    """Download logo from site and process it"""
    site_id = site_info['site_id']
    base_url = site_info['base_url']
    expected_filename = site_info['expected_filename']

    print(f"  Attempting to download logo for {site_id}...")

    # If there's already a remote URL, try that first
    urls_to_try = []
    if site_info['is_remote']:
        urls_to_try.append(site_info['logo_file'])

    # Then try to find favicon from the site
    favicon_urls = get_favicon_from_site(base_url)
    urls_to_try.extend(favicon_urls)

    # Try each URL until one works
    for url in urls_to_try:
        print(f"    Trying: {url}")

        # Determine temp file extension
        ext = Path(url).suffix
        if not ext or ext not in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg']:
            ext = '.png'

        temp_file = TEMP_DIR / f"{site_id}_temp{ext}"
        final_file = IMAGES_DIR / expected_filename

        if download_file(url, temp_file):
            if process_logo(temp_file, final_file):
                temp_file.unlink(missing_ok=True)
                return True
            else:
                print(f"    Processing failed, trying next URL...")
        else:
            print(f"    Download failed, trying next URL...")

        time.sleep(0.5)  # Be polite

    return False


def update_site_code(site_info):
    """Update site module to use local PNG file instead of remote URL"""
    if not site_info['is_remote']:
        return True  # Already using local file

    module_path = site_info['module_path']
    old_logo = site_info['logo_file']
    new_logo = site_info['expected_filename']

    try:
        content = module_path.read_text(encoding='utf-8')

        # Replace the remote URL with local filename
        # Be careful to only replace within the AdultSite declaration
        updated_content = content.replace(f'"{old_logo}"', f'"{new_logo}"')
        updated_content = updated_content.replace(f"'{old_logo}'", f"'{new_logo}'")

        if updated_content != content:
            module_path.write_text(updated_content, encoding='utf-8')
            print(f"    [SUCCESS] Updated {module_path.name} to use {new_logo}")
            return True
        else:
            print(f"    [WARNING] No changes made to {module_path.name}")
            return False

    except Exception as e:
        print(f"    [ERROR] Failed to update {module_path.name}: {e}")
        return False


def main():
    """Main execution"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fix and download missing site logos")
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    print("=" * 80)
    print("COMPREHENSIVE LOGO FIX SCRIPT")
    if args.dry_run:
        print("(DRY RUN MODE - No changes will be made)")
    print("=" * 80)
    print()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    print(f"\nDirectories:")
    print(f"  Sites:  {SITES_DIR}")
    print(f"  Images: {IMAGES_DIR}")
    print(f"  Temp:   {TEMP_DIR}")
    print()

    # Extract all sites
    print("Scanning site modules...")
    sites = extract_all_sites()
    print(f"Found {len(sites)} sites total\n")

    # Categorize sites
    needs_download = []      # Local file doesn't exist
    needs_update = []        # Using remote URL but local file exists
    needs_extension_fix = [] # File exists but wrong extension (e.g., vvp.jpg vs vvp.png)
    ok_sites = []            # Local file exists and code uses it

    for site in sites:
        # Check for extension mismatch (file exists with .png but code references .jpg)
        if site['needs_extension_fix']:
            needs_extension_fix.append(site)
        # Check if file doesn't exist at all (neither standard name nor referenced name)
        elif not site['local_exists'] and not site['current_file_exists']:
            needs_download.append(site)
        # Check if using remote URL but local file exists
        elif site['is_remote'] and (site['local_exists'] or site['current_file_exists']):
            needs_update.append(site)
        # File exists and code references it correctly
        elif site['current_file_exists'] or site['local_exists']:
            ok_sites.append(site)
        else:
            # Shouldn't reach here, but add to needs_download as fallback
            needs_download.append(site)

    # Display summary
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print(f"✅ Sites with working local logos: {len(ok_sites)}")
    print(f"🔧 Sites with logo file but code uses remote URL: {len(needs_update)}")
    print(f"🔨 Sites with wrong file extension: {len(needs_extension_fix)}")
    print(f"❌ Sites missing logo files: {len(needs_download)}")
    print()

    if needs_extension_fix:
        print(f"\nSites needing extension fix:")
        for site in needs_extension_fix:
            png_version = Path(site['logo_file']).with_suffix('.png')
            print(f"  - {site['site_id']:20s} expects {site['logo_file']:15s} but have {png_version} ({site['module']})")

    if needs_update:
        print(f"\nSites needing code update (have local file):")
        for site in needs_update:
            print(f"  - {site['site_id']:20s} ({site['module']})")

    if needs_download:
        print(f"\nSites needing logo download:")
        for site in needs_download:
            print(f"  - {site['site_id']:20s} ({site['module']})")

    # Ask for confirmation
    if not needs_download and not needs_update and not needs_extension_fix:
        print("\n✅ All logos are properly configured!")
        return

    total_fixes = len(needs_update) + len(needs_download) + len(needs_extension_fix)
    print("\n" + "=" * 80)

    if args.dry_run:
        print(f"DRY RUN: Would process {total_fixes} fixes ({len(needs_extension_fix)} extensions + {len(needs_update)} code updates + {len(needs_download)} downloads)")
        print("\nRe-run without --dry-run to apply changes")
        return

    if not args.yes:
        response = input(f"Process {total_fixes} fixes ({len(needs_extension_fix)} extensions + {len(needs_update)} code updates + {len(needs_download)} downloads)? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return

    print("\n" + "=" * 80)
    print("FIXING LOGOS")
    print("=" * 80)

    # Step 1: Fix extension mismatches
    extension_fixes = 0
    if needs_extension_fix:
        print(f"\n[1/3] Fixing file extensions ({len(needs_extension_fix)} sites)...")
        for i, site in enumerate(needs_extension_fix, 1):
            print(f"\n[{i}/{len(needs_extension_fix)}] {site['site_id']}")
            png_version = Path(site['logo_file']).with_suffix('.png')
            print(f"  Updating {site['logo_file']} -> {png_version} in {site['module']}")

            # Update the site code to use .png extension
            module_path = site['module_path']
            try:
                content = module_path.read_text(encoding='utf-8')
                updated_content = content.replace(f'"{site["logo_file"]}"', f'"{png_version}"')
                updated_content = updated_content.replace(f"'{site['logo_file']}'", f"'{png_version}'")

                if updated_content != content:
                    module_path.write_text(updated_content, encoding='utf-8')
                    print(f"  [SUCCESS] Updated {module_path.name}")
                    extension_fixes += 1
            except Exception as e:
                print(f"  [ERROR] Failed: {e}")

    # Step 2: Update code for sites that have local files
    updated_count = 0
    if needs_update:
        print(f"\n[2/3] Updating code to use local files ({len(needs_update)} sites)...")
        for i, site in enumerate(needs_update, 1):
            print(f"\n[{i}/{len(needs_update)}] {site['site_id']}")
            if update_site_code(site):
                updated_count += 1

    # Step 3: Download and process missing logos
    downloaded_count = 0
    failed_downloads = []

    if needs_download:
        print(f"\n[3/3] Downloading missing logos ({len(needs_download)} sites)...")
        for i, site in enumerate(needs_download, 1):
            print(f"\n[{i}/{len(needs_download)}] {site['site_id']}")
            if download_and_process_logo(site):
                downloaded_count += 1
                # If this was using a remote URL, update the code
                if site['is_remote']:
                    update_site_code(site)
            else:
                failed_downloads.append(site)

    # Final summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Extensions fixed: {extension_fixes}/{len(needs_extension_fix)}")
    print(f"✅ Code updated: {updated_count}/{len(needs_update)}")
    print(f"✅ Logos downloaded: {downloaded_count}/{len(needs_download)}")

    if failed_downloads:
        print(f"\n❌ Failed to download ({len(failed_downloads)} sites):")
        for site in failed_downloads:
            print(f"  - {site['site_id']:20s} @ {site['base_url']}")
        print("\nYou may need to manually download these logos.")

    print("\n[DONE] Logo fix complete!")


if __name__ == "__main__":
    main()
