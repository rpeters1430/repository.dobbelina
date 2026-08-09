"""Kodi background service for diagnostic telemetry drain and player monitoring."""

import sys
import time

try:
    import xbmc
    import xbmcaddon
except ImportError:
    xbmc = None
    xbmcaddon = None

from resources.lib import telemetry


def run_service():
    if not xbmc:
        return

    monitor = xbmc.Monitor()
    reporter = telemetry.get_reporter()
    last_drain = time.time()

    while not monitor.abortRequested():
        now = time.time()

        if reporter.enabled():
            if now - last_drain >= 15.0:
                try:
                    reporter.drain_once(limit=5)
                except Exception:
                    pass
                last_drain = now
        else:
            reporter.cleanup_if_disabled()

        if monitor.waitForAbort(1.0):
            break


if __name__ == "__main__":
    run_service()
