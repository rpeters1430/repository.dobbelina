"""Kodi background service for diagnostic telemetry drain and player monitoring."""

import time

try:
    import xbmc
    import xbmcaddon
except ImportError:
    xbmc = None
    xbmcaddon = None

from resources.lib import telemetry


class TelemetryPlayer(xbmc.Player if xbmc else object):
    def __init__(self, controller):
        if xbmc:
            super(TelemetryPlayer, self).__init__()
        self.controller = controller

    def onAVStarted(self):
        try:
            self.controller.on_av_started()
        except Exception:
            pass

    def onPlayBackError(self):
        try:
            self.controller.on_playback_error()
        except Exception:
            pass

    def onPlayBackStopped(self):
        try:
            self.controller.on_playback_stopped()
        except Exception:
            pass

    def onPlayBackEnded(self):
        try:
            self.controller.on_playback_ended()
        except Exception:
            pass


class TelemetryController:
    def __init__(self, reporter):
        self.reporter = reporter
        self.sm = None
        self.active_id = None

    def tick(self):
        if not self.reporter.enabled():
            self.sm = None
            self.active_id = None
            return

        # Load attempt from file
        attempt = self.reporter.load_playback_attempt()
        if not attempt:
            if self.sm:
                try:
                    outcome = self.sm.tick(time.time())
                    if outcome:
                        self.reporter.playback_outcome(outcome)
                except Exception:
                    pass
                self.sm = None
                self.active_id = None
            return

        attempt_id = attempt.get("attempt_id")
        created_at = attempt.get("created_at", time.time())

        # If it's a new attempt
        if not self.sm or self.active_id != attempt_id:
            from resources.lib.playback_monitor import PlaybackStateMachine
            self.sm = PlaybackStateMachine(attempt, created_at=created_at)
            self.active_id = attempt_id

        try:
            outcome = self.sm.tick(time.time())
            if outcome:
                self.reporter.playback_outcome(outcome)
                if self.sm.state == "terminal":
                    self.sm = None
                    self.active_id = None
                    self.reporter.clear_playback_attempt()
        except Exception:
            pass

    def on_av_started(self):
        if self.sm:
            self.sm.av_started(time.time())

    def on_playback_error(self):
        if self.sm:
            try:
                outcome = self.sm.playback_error(time.time())
                if outcome:
                    self.reporter.playback_outcome(outcome)
            except Exception:
                pass
            self.sm = None
            self.active_id = None
            self.reporter.clear_playback_attempt()

    def on_playback_stopped(self):
        if self.sm:
            try:
                outcome = self.sm.stopped(time.time())
                if outcome:
                    self.reporter.playback_outcome(outcome)
            except Exception:
                pass
            self.sm = None
            self.active_id = None
            self.reporter.clear_playback_attempt()

    def on_playback_ended(self):
        if self.sm:
            try:
                outcome = self.sm.ended(time.time())
                if outcome:
                    self.reporter.playback_outcome(outcome)
            except Exception:
                pass
            self.sm = None
            self.active_id = None
            self.reporter.clear_playback_attempt()


def run_service():
    if not xbmc:
        return

    monitor = xbmc.Monitor()
    reporter = telemetry.get_reporter()
    controller = TelemetryController(reporter)
    # Keep the callback player alive for the lifetime of the service.
    _player = TelemetryPlayer(controller)
    
    last_drain = time.time()

    while not monitor.abortRequested():
        now = time.time()

        if reporter.enabled():
            # Advance playback state machine tick
            try:
                controller.tick()
            except Exception:
                pass

            # Drain queue every 15 seconds
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
