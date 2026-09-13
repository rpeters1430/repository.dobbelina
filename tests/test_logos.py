from PIL import Image

from validate_logos import get_site_configs, get_logo_files


def test_all_sites_have_valid_existing_logos():
    sites = get_site_configs()
    logos = get_logo_files()
    assert len(sites) > 0

    for site_id, config in sites.items():
        logo_ref = config["logo_ref"]
        # Must be local filename, not remote URL
        assert not logo_ref.startswith("http://") and not logo_ref.startswith("https://"), (
            f"Site {site_id} uses remote logo: {logo_ref}"
        )
        # Logo must exist in images directory
        assert logo_ref in logos, f"Site {site_id} references missing logo file: {logo_ref}"

        logo_path = logos[logo_ref]["path"]
        assert logo_path.is_file(), f"Logo path is not a file: {logo_path}"
        assert logo_path.suffix.lower() == ".png", f"Logo is not PNG: {logo_ref}"

        # Must be readable and 256x256
        with Image.open(logo_path) as img:
            assert img.format == "PNG", f"{logo_ref} format is {img.format}, expected PNG"
            assert img.size == (256, 256), f"{logo_ref} dimensions {img.size} != (256, 256)"


def test_no_orphaned_site_logos():
    sites = get_site_configs()
    logos = get_logo_files()
    referenced = {config["logo_ref"] for config in sites.values()}

    orphans = []
    for name in logos:
        if name.startswith("cum-"):
            continue
        if name not in referenced:
            orphans.append(name)

    assert not orphans, f"Found orphaned logo files: {orphans}"


def test_cum_utility_icons_are_valid():
    logos = get_logo_files()
    cum_icons = [name for name in logos if name.startswith("cum-")]
    assert len(cum_icons) >= 10

    for name in cum_icons:
        p = logos[name]["path"]
        with Image.open(p) as img:
            assert img.format == "PNG", f"{name} is not PNG"
            assert img.width > 0 and img.height > 0
