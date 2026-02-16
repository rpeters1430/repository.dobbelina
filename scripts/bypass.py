import os
from pathlib import Path

from playwright.sync_api import sync_playwright

try:
    # Older playwright-stealth API.
    from playwright_stealth import stealth_sync as _legacy_stealth_sync

    def apply_stealth(page, context) -> None:
        _legacy_stealth_sync(page)

except ImportError:
    # Newer playwright-stealth API.
    from playwright_stealth import Stealth

    _stealth = Stealth()

    def apply_stealth(page, context) -> None:
        _stealth.apply_stealth_sync(context)


def run(url: str = "https://ask4porn.cc/", headless: bool = False) -> None:
    with sync_playwright() as p:
        profile_path = Path(os.getcwd()) / "browser_profile"
        profile_path.mkdir(parents=True, exist_ok=True)

        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )

        try:
            page = context.pages[0] if context.pages else context.new_page()
            apply_stealth(page, context)

            print(f"Navigating to {url}... solve challenge if it appears.")
            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            page.pause()
        finally:
            context.close()

if __name__ == "__main__":
    run()
