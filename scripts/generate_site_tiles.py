#!/usr/bin/env python3
"""Generate uniform site icon tiles for the Kodi site list.

Site logos in ``resources/images`` are transparent PNGs of every shape and
colour; dark lettering disappears on dark skins.  This script renders each
logo onto a 256x256 tile that matches the addon's neon/brick theme:

* background: a darkened crop of the addon fanart
* logos with dark or low-contrast lettering get a light rounded plate
* logos shipped inside a solid box are trimmed to their content first
* other logos get a soft pink glow

Tiles are written to ``resources/images/tiles/<name>.jpg``; originals are left
untouched so upstream logo updates keep working.  ``basics.site_image()``
prefers a tile when one exists.  Re-run after adding or changing a site logo:

    python scripts/generate_site_tiles.py            # all logos
    python scripts/generate_site_tiles.py pornhub    # selected logos
    python scripts/generate_site_tiles.py --sheet out.png  # also write a contact sheet
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "plugin.video.cumination"
IMAGES = ADDON / "resources" / "images"
TILES = IMAGES / "tiles"
FANART = ADDON / "fanart.jpg"

SIZE = 256
BG_CROP = (60, 560, 480, 980)  # plain brick area of fanart.jpg
DARK_LUMA = 70
DARK_SHARE_FOR_PLATE = 0.12
PLATE_BELOW_MEDIAN_LUMA = 120
LIGHT_LUMA = 200
MAX_LIGHT_SHARE_FOR_PLATE = 0.15
MAX_UPSCALE = 3.0
OWN_BACKGROUND_COVERAGE = 0.97
PLATE_COLOR = (242, 238, 240, 240)
GLOW_COLOR = (255, 40, 150)
JPEG_QUALITY = 88


def logo_sources(names=None):
    for path in sorted(IMAGES.glob("*.png")):
        if path.name.startswith("cum-"):
            continue
        if names and path.stem not in names:
            continue
        yield path


def _background():
    bg = Image.open(FANART).convert("RGB").crop(BG_CROP).resize((SIZE, SIZE), Image.LANCZOS)
    return ImageEnhance.Brightness(bg).enhance(0.5).convert("RGBA")


def _logo_stats(logo):
    """Return (dark share, light share, median luma, opaque coverage) of a logo."""
    alpha = logo.getchannel("A")
    luma = logo.convert("L")
    lumas = [lum for lum, a in zip(luma.tobytes(), alpha.tobytes()) if a > 128]
    if not lumas:
        return 0.0, 0.0, 255, 0.0
    lumas.sort()
    total = float(len(lumas))
    dark = sum(1 for lum in lumas if lum < DARK_LUMA) / total
    light = sum(1 for lum in lumas if lum > LIGHT_LUMA) / total
    coverage = total / (logo.width * logo.height)
    return dark, light, lumas[len(lumas) // 2], coverage


def _trim_own_background(logo):
    """Crop an opaque logo to the content that differs from its corner colour.

    Many logos ship as a small mark centred in a large solid box; trimming
    lets the mark fill the tile instead of the box.
    """
    rgb = logo.convert("RGB")
    w, h = rgb.size
    corners = [rgb.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    bg = tuple(sorted(c[i] for c in corners)[1] for i in range(3))
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, bg)).convert("L")
    bbox = diff.point(lambda v: 255 if v > 40 else 0).getbbox()
    if not bbox:
        return logo
    pad = int(max(w, h) * 0.06)
    bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(w, bbox[2] + pad), min(h, bbox[3] + pad))
    return logo.crop(bbox)


def render_tile(path, background):
    logo = Image.open(path).convert("RGBA")
    bbox = logo.getchannel("A").point(lambda a: 255 if a > 10 else 0).getbbox()
    if bbox:
        logo = logo.crop(bbox)
    dark_share, light_share, median_luma, coverage = _logo_stats(logo)
    own_background = coverage >= OWN_BACKGROUND_COVERAGE
    if own_background:
        logo = _trim_own_background(logo)

    wide = logo.width > logo.height * 1.4
    very_wide = logo.width > logo.height * 3
    max_w = SIZE * (0.9 if very_wide else 0.84)
    max_h = SIZE * (0.45 if wide else 0.84)
    # thumbnail() never enlarges; scale explicitly so small marks fill the tile
    scale = min(max_w / logo.width, max_h / logo.height, MAX_UPSCALE)
    logo = logo.resize((max(1, int(logo.width * scale)), max(1, int(logo.height * scale))), Image.LANCZOS)
    pos = ((SIZE - logo.width) // 2, (SIZE - logo.height) // 2)

    # Plate when dark lettering dominates (e.g. Pornhub's black "Porn" next
    # to white-on-orange "hub"), or for low-contrast mid tones - but not for
    # logos that are largely white, which a light plate would swallow.
    needs_plate = not own_background and (
        (dark_share > DARK_SHARE_FOR_PLATE and dark_share >= light_share)
        or (median_luma < PLATE_BELOW_MEDIAN_LUMA and light_share < MAX_LIGHT_SHARE_FOR_PLATE)
    )
    tile = background.copy()
    if needs_plate:
        pad = 12
        plate = Image.new("RGBA", (SIZE, SIZE))
        x0, y0 = pos[0] - pad, pos[1] - pad
        ImageDraw.Draw(plate).rounded_rectangle(
            (x0, y0, x0 + logo.width + pad * 2, y0 + logo.height + pad * 2),
            radius=18,
            fill=PLATE_COLOR,
        )
        tile.alpha_composite(plate)
    else:
        glow_src = Image.new("RGBA", logo.size, GLOW_COLOR + (0,))
        glow_src.putalpha(logo.getchannel("A").point(lambda v: int(v * 0.55)))
        glow = Image.new("RGBA", (SIZE, SIZE))
        glow.paste(glow_src, pos)
        tile.alpha_composite(glow.filter(ImageFilter.GaussianBlur(12)))
    tile.alpha_composite(logo, pos)
    return tile.convert("RGB")


def contact_sheet(paths, out, cols=12, cell=128):
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rows * cell), (20, 20, 20))
    for i, p in enumerate(paths):
        img = Image.open(p).convert("RGB").resize((cell - 4, cell - 4), Image.LANCZOS)
        sheet.paste(img, ((i % cols) * cell + 2, (i // cols) * cell + 2))
    sheet.save(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("names", nargs="*", help="logo names (file stem) to render; default all")
    parser.add_argument("--sheet", help="also write a contact sheet PNG of the generated tiles")
    args = parser.parse_args(argv)

    TILES.mkdir(parents=True, exist_ok=True)
    background = _background()
    written = []
    for src in logo_sources(set(args.names) or None):
        out = TILES / (src.stem + ".jpg")
        render_tile(src, background).save(out, "JPEG", quality=JPEG_QUALITY, optimize=True)
        written.append(out)
    print("Wrote {} tiles to {}".format(len(written), TILES.relative_to(ROOT)))
    if args.sheet and written:
        contact_sheet(written, args.sheet)
        print("Contact sheet: {}".format(args.sheet))
    return 0


if __name__ == "__main__":
    sys.exit(main())
