#!/usr/bin/env python3
"""
Site Module Updater
Automatically updates site modules to reference local logo files instead of remote URLs
"""

import re
from pathlib import Path
import shutil

REPO_ROOT = Path(r"C:\Users\James\Desktop\repository.dobbelina")
SITES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"
IMAGES_DIR = REPO_ROOT / "plugin.video.cumination" / "resources" / "images"
BACKUP_DIR = REPO_ROOT / "site_modules_backup"


def backup_sites():
    """Create backup of all site modules"""
    if BACKUP_DIR.exists():
        print(f"Backup directory already exists: {BACKUP_DIR}")
        response = input("Overwrite existing backup? (y/N): ")
        if response.lower() != "y":
            print("Aborting...")
            return False
        shutil.rmtree(BACKUP_DIR)

    BACKUP_DIR.mkdir()
    count = 0
    for site_file in SITES_DIR.glob("*.py"):
        if site_file.name not in ("__init__.py", "soup_spec.py"):
            shutil.copy2(site_file, BACKUP_DIR / site_file.name)
            count += 1

    print(f"[SUCCESS] Backed up {count} site modules to: {BACKUP_DIR}")
    return True


def get_sites_with_remote_urls():
    """Find all sites using remote URLs for logos"""
    sites_to_update = []

    # Pattern to match AdultSite with remote logo URL
    pattern = re.compile(
        r"(site\s*=\s*AdultSite\s*\(\s*"
        r"['\"]([^'\"]+)['\"]"  # site_id (group 2)
        r"\s*,\s*['\"][^'\"]*['\"]"  # display_name
        r"\s*,\s*['\"][^'\"]*['\"]"  # base_url
        r"\s*,\s*['\"])((https?://|http://)[^'\"]+)(['\"])",  # logo_url (group 4)
        re.DOTALL | re.MULTILINE,
    )

    for site_file in SITES_DIR.glob("*.py"):
        if site_file.name in ("__init__.py", "soup_spec.py"):
            continue

        try:
            content = site_file.read_text(encoding="utf-8")
            match = pattern.search(content)

            if match:
                site_id = match.group(2)
                logo_url = match.group(4)
                full_match = match.group(0)
                prefix = match.group(1)
                suffix = match.group(7)

                # Check if local logo exists
                local_logo = f"{site_id}.png"
                local_logo_path = IMAGES_DIR / local_logo

                sites_to_update.append(
                    {
                        "file": site_file,
                        "site_id": site_id,
                        "logo_url": logo_url,
                        "local_logo": local_logo,
                        "local_exists": local_logo_path.exists(),
                        "full_match": full_match,
                        "prefix": prefix,
                        "suffix": suffix,
                        "content": content,
                    }
                )
        except Exception as e:
            print(f"[WARNING] Error reading {site_file.name}: {e}")

    return sites_to_update


def preview_changes(sites):
    """Show what will be changed"""
    print("\n" + "=" * 80)
    print("PREVIEW OF CHANGES")
    print("=" * 80 + "\n")

    for i, site in enumerate(sites, 1):
        print(f"{i}. {site['file'].name} (site_id: {site['site_id']})")
        print(f"   BEFORE: {site['logo_url'][:60]}...")
        print(f"   AFTER:  {site['local_logo']}")

        if not site["local_exists"]:
            print(f"   [WARNING] Local logo does not exist yet!")

        print()

    print(f"Total sites to update: {len(sites)}")
    missing_logos = sum(1 for s in sites if not s["local_exists"])
    if missing_logos:
        print(f"[WARNING] {missing_logos} sites don't have local logos yet!")
        print(f"          Run process_logos.py first to download missing logos")


def apply_changes(sites, dry_run=False):
    """Apply the changes to site modules"""
    updated_count = 0
    skipped_count = 0

    for site in sites:
        if not site["local_exists"]:
            print(
                f"[SKIP] {site['file'].name} - local logo {site['local_logo']} not found"
            )
            skipped_count += 1
            continue

        # Create the replacement
        old_text = site["full_match"]
        new_text = f"{site['prefix']}{site['local_logo']}{site['suffix']}"

        # Replace in content
        new_content = site["content"].replace(old_text, new_text, 1)

        if new_content == site["content"]:
            print(f"[SKIP] {site['file'].name} - no changes needed (pattern not found)")
            skipped_count += 1
            continue

        if dry_run:
            print(f"[DRY RUN] Would update {site['file'].name}")
        else:
            try:
                site["file"].write_text(new_content, encoding="utf-8")
                print(f"[UPDATED] {site['file'].name}")
                updated_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to update {site['file'].name}: {e}")
                skipped_count += 1

    print(f"\n{'=' * 80}")
    print(f"SUMMARY")
    print(f"{'=' * 80}")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {skipped_count}")

    return updated_count, skipped_count


def main():
    """Main execution"""
    print("Cumination Site Module Updater")
    print("=" * 80)
    print("\nThis script updates site modules to use local logo files")
    print("instead of remote URLs.\n")

    # Find sites to update
    print("Scanning site modules...")
    sites = get_sites_with_remote_urls()

    if not sites:
        print("\n[SUCCESS] No sites found using remote URLs!")
        print("All sites are already using local logo files.")
        return

    # Preview changes
    preview_changes(sites)

    # Confirm
    print("\n" + "=" * 80)
    print("OPTIONS")
    print("=" * 80)
    print("1. Create backup and apply changes")
    print("2. Apply changes without backup (not recommended)")
    print("3. Dry run (show what would change without modifying files)")
    print("4. Exit without making changes")

    choice = input("\nSelect option (1-4): ").strip()

    if choice == "1":
        if not backup_sites():
            return
        print("\nApplying changes...")
        updated, skipped = apply_changes(sites, dry_run=False)
        if updated > 0:
            print(f"\n[SUCCESS] Updated {updated} site modules!")
            print(f"Backup saved to: {BACKUP_DIR}")
            print(f"\nTo restore from backup if needed:")
            print(f"  Copy files from {BACKUP_DIR} back to {SITES_DIR}")

    elif choice == "2":
        print("\n[WARNING] Proceeding without backup!")
        response = input("Are you sure? (yes/NO): ")
        if response.lower() == "yes":
            print("\nApplying changes...")
            updated, skipped = apply_changes(sites, dry_run=False)
            if updated > 0:
                print(f"\n[SUCCESS] Updated {updated} site modules!")
        else:
            print("Cancelled.")

    elif choice == "3":
        print("\nDry run - no files will be modified...")
        apply_changes(sites, dry_run=True)

    elif choice == "4":
        print("Exiting without changes.")
        return

    else:
        print("Invalid option.")
        return


if __name__ == "__main__":
    main()
