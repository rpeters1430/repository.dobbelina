from pathlib import Path


SITE_DIR = Path(__file__).resolve().parents[2] / "plugin.video.cumination" / "resources" / "lib" / "sites"

# Playwright must not be used in Kodi site runtime modules.
BLOCKED_PATTERNS = (
    "playwright",
    "playwright_helper",
    "fetch_with_playwright",
    "sniff_video_url",
    "@playwright/test",
    "npx",
)


def test_sites_do_not_reference_playwright():
    matches = []
    for path in sorted(SITE_DIR.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            lower_line = line.lower()
            if any(pattern in lower_line for pattern in BLOCKED_PATTERNS):
                rel_path = path.relative_to(Path(__file__).resolve().parents[2])
                matches.append(f"{rel_path}:{lineno}: {line.strip()}")

    assert not matches, "Playwright is not allowed in Kodi site modules:\n" + "\n".join(matches)
