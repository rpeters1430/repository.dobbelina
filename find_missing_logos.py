import re
from pathlib import Path


def find_missing_logos():
    project_root = Path.cwd()
    sites_dir = project_root / "plugin.video.cumination" / "resources" / "lib" / "sites"
    images_dir = project_root / "plugin.video.cumination" / "resources" / "images"

    # Get all existing image filenames
    existing_images = {f.name for f in images_dir.iterdir() if f.is_file()}

    missing_logos = []
    found_sites = 0

    # site = AdultSite("name", "title", "url", "logo.png", ...)
    # Improved regex to handle various quote types and potentially escaped quotes
    logo_pattern = r'AdultSite\s*\(\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*["\']([^"\']+)["\']'

    for site_file in sites_dir.glob("*.py"):
        if site_file.name == "__init__.py" or site_file.name == "soup_spec.py":
            continue

        found_sites += 1
        content = site_file.read_text(encoding="utf-8")

        matches = re.findall(logo_pattern, content)
        if matches:
            for logo_file in matches:
                # Filter out variables like site.img_cat
                if "." in logo_file and not logo_file.startswith("site."):
                    if logo_file not in existing_images:
                        missing_logos.append((site_file.name, logo_file))
        else:
            # Check if it uses AdultSite at all
            if "AdultSite" in content:
                # print(f"DEBUG: Could not find logo in {site_file.name}")
                pass

    print(f"Checked {found_sites} site modules.")
    if missing_logos:
        print(f"Found {len(missing_logos)} missing logos:")
        # Dedup if multiple AdultSite instances use same missing logo
        for site, logo in sorted(list(set(missing_logos))):
            print(f"  - {site}: {logo}")
    else:
        print("No missing logos found!")


if __name__ == "__main__":
    find_missing_logos()
