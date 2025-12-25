#!/usr/bin/env python
"""
Analyze logo dimensions using PIL
"""

import os
from collections import Counter

try:
    from PIL import Image
except ImportError:
    print("PIL/Pillow not installed. Install with: pip install Pillow")
    exit(1)

IMAGES_DIR = r"C:\Users\James\Desktop\repository.dobbelina\plugin.video.cumination\resources\images"


def analyze_dimensions():
    """Analyze all logo dimensions"""
    dimensions = []
    widths = []
    heights = []

    # Skip the cum-* utility icons
    skip_prefixes = ("cum-",)

    for filename in os.listdir(IMAGES_DIR):
        if filename.lower().endswith(
            (".png", ".jpg", ".gif")
        ) and not filename.startswith(skip_prefixes):
            filepath = os.path.join(IMAGES_DIR, filename)
            try:
                with Image.open(filepath) as img:
                    width, height = img.size
                    dimensions.append((width, height, filename))
                    widths.append(width)
                    heights.append(height)
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    if not dimensions:
        print("No images found")
        return

    # Sort by size (width * height)
    dimensions.sort(key=lambda x: x[0] * x[1])

    print("=" * 80)
    print("LOGO DIMENSIONS ANALYSIS")
    print("=" * 80)
    print()

    print(f"Total logos analyzed: {len(dimensions)}")
    print()

    # Statistics
    print("Width statistics:")
    print(f"  Min:    {min(widths):4d}px")
    print(f"  Max:    {max(widths):4d}px")
    print(f"  Average: {sum(widths) // len(widths):4d}px")
    print(f"  Median:  {sorted(widths)[len(widths) // 2]:4d}px")
    print()

    print("Height statistics:")
    print(f"  Min:    {min(heights):4d}px")
    print(f"  Max:    {max(heights):4d}px")
    print(f"  Average: {sum(heights) // len(heights):4d}px")
    print(f"  Median:  {sorted(heights)[len(heights) // 2]:4d}px")
    print()

    # Common dimensions
    dim_counter = Counter((w, h) for w, h, _ in dimensions)
    print("Most common dimensions:")
    for (w, h), count in dim_counter.most_common(10):
        print(f"  {w:4d}x{h:4d}px: {count:2d} logos")
    print()

    # Show smallest logos
    print("Smallest logos:")
    for w, h, name in dimensions[:10]:
        print(f"  {w:4d}x{h:4d}px - {name}")
    print()

    # Show largest logos
    print("Largest logos:")
    for w, h, name in dimensions[-10:]:
        print(f"  {w:4d}x{h:4d}px - {name}")
    print()

    # Aspect ratio analysis
    aspect_ratios = []
    for w, h, name in dimensions:
        ratio = w / h if h > 0 else 0
        aspect_ratios.append((ratio, name))

    print("Extreme aspect ratios (non-square logos):")
    aspect_ratios.sort(key=lambda x: abs(x[0] - 1.0), reverse=True)
    for ratio, name in aspect_ratios[:15]:
        print(f"  {ratio:5.2f}:1 - {name}")
    print()


if __name__ == "__main__":
    analyze_dimensions()
