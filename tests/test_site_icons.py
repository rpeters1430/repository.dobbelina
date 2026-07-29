import ast
import struct
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SITES_DIR = ROOT / "plugin.video.cumination" / "resources" / "lib" / "sites"
IMAGES_DIR = ROOT / "plugin.video.cumination" / "resources" / "images"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _site_icon_references():
    references = []
    for site_file in sorted(SITES_DIR.glob("*.py")):
        tree = ast.parse(site_file.read_text(encoding="utf-8"), filename=str(site_file))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Name) or node.func.id != "AdultSite":
                continue
            if len(node.args) < 4:
                continue
            site_id = node.args[0]
            icon = node.args[3]
            if not isinstance(site_id, ast.Constant) or not isinstance(icon, ast.Constant):
                continue
            if isinstance(site_id.value, str) and isinstance(icon.value, str):
                references.append((site_id.value, icon.value, site_file.name))
    return references


def test_every_site_references_a_valid_256px_local_png():
    problems = []

    for site_id, icon_name, module_name in _site_icon_references():
        if icon_name.startswith(("http://", "https://")):
            problems.append(f"{site_id} ({module_name}) uses remote icon {icon_name}")
            continue
        if Path(icon_name).name != icon_name or Path(icon_name).suffix != ".png":
            problems.append(f"{site_id} ({module_name}) has invalid icon name {icon_name}")
            continue

        icon_path = IMAGES_DIR / icon_name
        if not icon_path.is_file():
            problems.append(f"{site_id} ({module_name}) is missing {icon_name}")
            continue

        data = icon_path.read_bytes()
        if len(data) < 24 or data[:8] != PNG_SIGNATURE or data[12:16] != b"IHDR":
            problems.append(f"{site_id} ({module_name}) has invalid PNG {icon_name}")
            continue

        dimensions = struct.unpack(">II", data[16:24])
        if dimensions != (256, 256):
            problems.append(
                f"{site_id} ({module_name}) icon {icon_name} is "
                f"{dimensions[0]}x{dimensions[1]}, expected 256x256"
            )

    assert not problems, "\n" + "\n".join(problems)


def test_site_icons_are_not_solid_color_placeholders():
    icon_names = {icon_name for _, icon_name, _ in _site_icon_references()}
    placeholders = []

    for icon_name in sorted(icon_names):
        icon_path = IMAGES_DIR / icon_name
        if not icon_path.is_file():
            continue
        with Image.open(icon_path) as image:
            colors = image.convert("RGBA").getcolors(maxcolors=2)
        if colors is not None and len(colors) == 1:
            placeholders.append(icon_name)

    assert not placeholders, "Solid-color placeholder icons: " + ", ".join(placeholders)
