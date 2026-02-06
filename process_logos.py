#!/usr/bin/env python3
"""
Logo Processing Automation Script
Downloads, converts, resizes, and optimizes logos for Cumination addon
"""

import os
import sys
import subprocess
import urllib.request
import urllib.error
import re
from pathlib import Path

# Configuration
# Default to the repo root based on this script's location; allow override via REPO_ROOT env var.
REPO_ROOT = Path(os.environ.get("REPO_ROOT", Path(__file__).resolve().parent))
IMAGES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "images"
SITES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"
TEMP_DIR = REPO_ROOT / "temp_logos"

# Standards
TARGET_SIZE = (256, 256)
MAX_FILE_SIZE_KB = 50
OPTIMAL_FILE_SIZE_KB = (5, 30)

# Ensure temp directory exists
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def check_imagemagick():
    """Check if ImageMagick is installed"""
    try:
        result = subprocess.run(["magick", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] ImageMagick is installed")
            return True
    except FileNotFoundError:
        pass

    print("[ERROR] ImageMagick not found!")
    print(
        "Please install ImageMagick from: https://imagemagick.org/script/download.php"
    )
    print("On Windows, make sure to check 'Add to PATH' during installation")
    return False


def download_logo(url, output_path):
    """Download a logo from URL"""
    try:
        print(f"  Downloading from: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
            with open(output_path, "wb") as f:
                f.write(data)
        print(f"  Downloaded: {len(data)} bytes")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to download: {e}")
        return False


def process_logo(input_path, output_path, site_id):
    """
    Process a logo file:
    1. Convert to PNG if needed
    2. Resize to 256x256 with transparent padding
    3. Optimize file size
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        print(f"  [ERROR] Input file not found: {input_path}")
        return False

    try:
        # Step 1: Convert to PNG and resize with padding
        print(f"  Processing: {input_path.name} -> {output_path.name}")

        cmd = [
            "magick",
            str(input_path),
            "-background",
            "none",
            "-gravity",
            "center",
            "-resize",
            "256x256",
            "-extent",
            "256x256",
            "-strip",  # Remove metadata
            str(output_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [ERROR] ImageMagick failed: {result.stderr}")
            return False

        # Step 2: Optimize with pngquant if available
        if os.path.exists(output_path):
            file_size_kb = output_path.stat().st_size / 1024
            print(f"  Initial size: {file_size_kb:.1f} KB")

            # Try pngquant optimization if file is too large
            if file_size_kb > OPTIMAL_FILE_SIZE_KB[1]:
                try:
                    pngquant_cmd = [
                        "pngquant",
                        "--quality=80-95",
                        "--ext",
                        ".png",
                        "--force",
                        str(output_path),
                    ]
                    subprocess.run(pngquant_cmd, capture_output=True, timeout=10)
                    new_size_kb = output_path.stat().st_size / 1024
                    print(f"  Optimized size: {new_size_kb:.1f} KB")
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    print(f"  [INFO] pngquant not available, skipping optimization")

            # Final size check
            final_size_kb = output_path.stat().st_size / 1024
            if final_size_kb > MAX_FILE_SIZE_KB:
                print(
                    f"  [WARNING] File size {final_size_kb:.1f} KB exceeds maximum {MAX_FILE_SIZE_KB} KB"
                )

            print(
                f"  [SUCCESS] Processed logo: {output_path.name} ({final_size_kb:.1f} KB)"
            )
            return True
        else:
            print(f"  [ERROR] Output file not created")
            return False

    except Exception as e:
        print(f"  [ERROR] Processing failed: {e}")
        return False


def create_placeholder_logo(display_name, output_path, bg_color="hotpink"):
    """Create a placeholder logo with the site name"""
    try:
        # Clean up display name (remove Kodi color tags)
        clean_name = re.sub(r"\[COLOR.*?\]|\[/COLOR\]", "", display_name)

        print(f"  Creating placeholder logo for: {clean_name}")

        cmd = [
            "magick",
            "-size",
            "256x256",
            f"canvas:{bg_color}",
            "-fill",
            "white",
            "-gravity",
            "center",
            "-font",
            "Arial",
            "-pointsize",
            "40",
            f"caption:{clean_name}",
            str(output_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  [SUCCESS] Created placeholder: {output_path.name}")
            return True
        else:
            # Try without specific font if Arial fails
            cmd.pop(cmd.index("-font") + 1)
            cmd.pop(cmd.index("-font"))
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(
                    f"  [SUCCESS] Created placeholder (default font): {output_path.name}"
                )
                return True
            print(f"  [ERROR] Placeholder creation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  [ERROR] Placeholder creation failed: {e}")
        return False


def get_sites_needing_logos():
    """Extract all sites that need local logos"""
    sites_needing_logos = []
    # AdultSite(site_id, display_name, base_url, logo_file, ...)
    # We want sites where logo_file (4th param) is a remote URL
    remote_url_pattern = re.compile(
        r"site\s*=\s*AdultSite\s*\(\s*"
        r"['\"]([^'\"]+)['\"]"  # site_id (group 1)
        r"\s*,\s*['\"]([^'\"]+)['\"]"  # display_name (group 2)
        r"\s*,\s*['\"][^'\"]*['\"]"  # base_url
        r"\s*,\s*['\"]((https?://|http://)[^'\"]+)['\"]",  # logo_url (group 3, starts with http)
        re.DOTALL,
    )

    for site_file in SITES_DIR.glob("*.py"):
        if site_file.name in ("__init__.py", "soup_spec.py"):
            continue

        try:
            content = site_file.read_text(encoding="utf-8")
            content_single = content.replace("\n", " ")
            match = remote_url_pattern.search(content_single)

            if match:
                site_id = match.group(1)
                display_name = match.group(2)
                logo_url = match.group(3)
                sites_needing_logos.append(
                    {
                        "site_id": site_id,
                        "display_name": display_name,
                        "logo_url": logo_url,
                        "module": site_file.name,
                        "expected_filename": f"{site_id}.png",
                    }
                )
        except Exception as e:
            print(f"[WARNING] Error reading {site_file.name}: {e}")

    return sites_needing_logos


def download_and_process_missing_logos():
    """Download and process all missing logos"""
    sites = get_sites_needing_logos()

    print(f"\n{'=' * 80}")
    print(f"DOWNLOADING AND PROCESSING MISSING LOGOS")
    print(f"{'=' * 80}\n")
    print(f"Found {len(sites)} sites with remote logo URLs\n")

    success_count = 0
    placeholder_count = 0
    failed = []

    for i, site in enumerate(sites, 1):
        print(f"[{i}/{len(sites)}] Processing {site['site_id']}...")

        temp_file = TEMP_DIR / f"{site['site_id']}_temp{Path(site['logo_url']).suffix}"
        final_file = IMAGES_DIR / site["expected_filename"]

        # Download
        if download_logo(site["logo_url"], temp_file):
            # Process
            if process_logo(temp_file, final_file, site["site_id"]):
                success_count += 1
                # Clean up temp file
                temp_file.unlink(missing_ok=True)
            else:
                # Fallback to placeholder if processing failed
                if create_placeholder_logo(site["display_name"], final_file):
                    placeholder_count += 1
                else:
                    failed.append(site)
        else:
            # Fallback to placeholder if download failed
            if create_placeholder_logo(site["display_name"], final_file):
                placeholder_count += 1
            else:
                failed.append(site)

        print()

    print(f"\n{'=' * 80}")
    print(f"SUMMARY")
    print(f"{'=' * 80}")
    print(f"Successfully processed: {success_count}/{len(sites)}")
    print(f"Placeholders created:  {placeholder_count}")
    print(f"Total successful:      {success_count + placeholder_count}/{len(sites)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print(f"\nFailed sites:")
        for site in failed:
            print(f"  - {site['site_id']}: {site['logo_url']}")


def convert_existing_logos():
    """Convert all existing JPG/GIF logos to PNG and resize to 256x256"""
    print(f"\n{'=' * 80}")
    print(f"CONVERTING AND RESIZING EXISTING LOGOS")
    print(f"{'=' * 80}\n")

    converted_count = 0
    resized_count = 0

    for logo_file in sorted(IMAGES_DIR.glob("*")):
        if logo_file.name.startswith("cum-"):
            continue

        if logo_file.suffix.lower() in (".jpg", ".gif", ".jpeg"):
            print(f"Converting {logo_file.name} to PNG...")
            new_name = logo_file.with_suffix(".png")
            if process_logo(logo_file, new_name, logo_file.stem):
                logo_file.unlink()  # Remove old file
                converted_count += 1
        elif logo_file.suffix.lower() == ".png":
            # Check if already 256x256
            try:
                result = subprocess.run(
                    ["magick", "identify", "-format", "%wx%h", str(logo_file)],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    dims = result.stdout.strip()
                    if dims != "256x256":
                        print(f"Resizing {logo_file.name} from {dims} to 256x256...")
                        temp_file = TEMP_DIR / f"temp_{logo_file.name}"
                        if process_logo(logo_file, temp_file, logo_file.stem):
                            temp_file.replace(logo_file)
                            resized_count += 1
            except Exception as e:
                print(
                    f"  [WARNING] Could not check dimensions for {logo_file.name}: {e}"
                )

    print(f"\nConverted {converted_count} logos to PNG")
    print(f"Resized {resized_count} logos to 256x256")


def validate_all_logos():
    """Validate all logos meet standards"""
    print(f"\n{'=' * 80}")
    print(f"VALIDATING LOGOS")
    print(f"{'=' * 80}\n")

    issues = []

    for logo_file in sorted(IMAGES_DIR.glob("*.png")):
        if logo_file.name.startswith("cum-"):
            continue

        # Check dimensions
        try:
            result = subprocess.run(
                ["magick", "identify", "-format", "%wx%h %b", str(logo_file)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                dims, size_str = output.split()

                if dims != "256x256":
                    issues.append(f"{logo_file.name}: Wrong dimensions ({dims})")

                # Parse size (format like "12.5KB" or "1.2MB")
                size_kb = 0
                if "KB" in size_str:
                    size_kb = float(size_str.replace("KB", ""))
                elif "MB" in size_str:
                    size_kb = float(size_str.replace("MB", "")) * 1024
                elif "B" in size_str:
                    size_kb = float(size_str.replace("B", "")) / 1024

                if size_kb > MAX_FILE_SIZE_KB:
                    issues.append(f"{logo_file.name}: Too large ({size_kb:.1f} KB)")

        except Exception as e:
            issues.append(f"{logo_file.name}: Validation error ({e})")

    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("[SUCCESS] All logos meet standards!")

    return len(issues) == 0


def test_logo_source():
    """Test a logo from a URL or local file"""
    print(f"\n{'=' * 80}")
    print(f"TEST LOGO SOURCE")
    print(f"{'=' * 80}\n")

    source = input("Enter logo URL or path to local file: ").strip()
    if not source:
        return

    site_id = input("Enter site ID (for filename): ").strip()
    if not site_id:
        site_id = "test_logo"

    temp_file = (
        TEMP_DIR
        / f"test_temp{Path(source).suffix if 'http' in source else Path(source).suffix}"
    )
    final_file = IMAGES_DIR / f"{site_id}.png"

    if source.startswith("http"):
        if not download_logo(source, temp_file):
            print("[ERROR] Download failed")
            return
        input_path = temp_file
    else:
        input_path = Path(source)
        if not input_path.exists():
            print(f"[ERROR] Local file not found: {input_path}")
            return

    if process_logo(input_path, final_file, site_id):
        print(f"\n[SUCCESS] Logo processed and saved to: {final_file}")
        # On Windows, try to open the file
        if sys.platform == "win32":
            try:
                os.startfile(final_file)
            except Exception:
                pass
    else:
        print("\n[ERROR] Logo processing failed")

    # Clean up temp
    if temp_file.exists():
        temp_file.unlink()


def manual_placeholder():
    """Manually create a placeholder logo"""
    print(f"\n{'=' * 80}")
    print(f"CREATE PLACEHOLDER LOGO")
    print(f"{'=' * 80}\n")

    display_name = input("Enter site display name: ").strip()
    if not display_name:
        return

    site_id = input("Enter site ID (for filename): ").strip()
    if not site_id:
        site_id = display_name.lower().replace(" ", "_")

    final_file = IMAGES_DIR / f"{site_id}.png"

    if create_placeholder_logo(display_name, final_file):
        print(f"\n[SUCCESS] Placeholder created and saved to: {final_file}")
        if sys.platform == "win32":
            try:
                os.startfile(final_file)
            except Exception:
                pass
    else:
        print("\n[ERROR] Placeholder creation failed")


def main():
    """Main execution"""
    print("Cumination Logo Processing Script")
    print("=" * 80)

    # Check dependencies
    if not check_imagemagick():
        sys.exit(1)

    print(f"\nDirectories:")
    print(f"  Images: {IMAGES_DIR}")
    print(f"  Sites:  {SITES_DIR}")
    print(f"  Temp:   {TEMP_DIR}")

    # Menu
    print(f"\nOptions:")
    print("  1. Download and process all missing logos")
    print("  2. Convert existing JPG/GIF logos to PNG")
    print("  3. Resize all existing logos to 256x256")
    print("  4. Validate all logos")
    print("  5. Run all tasks (full standardization)")
    print("  6. Test a logo source (URL or file)")
    print("  7. Create placeholder logo manually")
    print("  8. Exit")

    choice = input("\nSelect option (1-8): ").strip()

    if choice == "1":
        download_and_process_missing_logos()
    elif choice == "2":
        convert_existing_logos()
    elif choice == "3":
        convert_existing_logos()  # Same function handles both
    elif choice == "4":
        validate_all_logos()
    elif choice == "5":
        download_and_process_missing_logos()
        convert_existing_logos()
        validate_all_logos()
    elif choice == "6":
        test_logo_source()
    elif choice == "7":
        manual_placeholder()
    elif choice == "8":
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice")
        sys.exit(1)

    print("\n[DONE] Logo processing complete!")


if __name__ == "__main__":
    main()
