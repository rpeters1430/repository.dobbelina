"""End-to-end testing of Cumination inside a real, headless Kodi.

Pieces:
    profile.py  - build a throwaway Kodi home with the addon + dependencies
    runner.py   - start/stop Kodi under Xvfb, JSON-RPC readiness, log capture
    driver.py   - "user" actions over JSON-RPC: browse, handle dialogs, play
    checks.py   - pure heuristics that turn a listing/playback into issues
    crawler.py  - walks each site the way a user would and records issues
    report.py   - JSON + HTML summary

Entry point: ``python -m scripts.kodi_e2e --help``
"""
