"""Playback state machine and monitor controller for Kodi player callbacks."""

STARTUP_TIMEOUT = 30.0
EARLY_STOP_WINDOW = 15.0
STABILITY_THRESHOLD = 30.0


class PlaybackStateMachine:

    def __init__(self, attempt, created_at=0.0):
        self.attempt = attempt or {}
        self.created_at = created_at
        self.started_at = None
        self.state = "pending"  # pending, started, stable, terminal
        self.terminal_outcome = None

    def _make_outcome(self, outcome_type, now_ts):
        start = self.started_at or self.created_at
        elapsed_ms = int(max(0, now_ts - start) * 1000)
        self.state = "terminal"
        self.terminal_outcome = {"outcome": outcome_type, "elapsed_ms": elapsed_ms, "attempt": self.attempt}
        return self.terminal_outcome

    def av_started(self, now_ts):
        if self.state == "terminal":
            return None
        self.state = "started"
        self.started_at = now_ts
        return None

    def playback_error(self, now_ts):
        if self.state == "terminal":
            return None
        return self._make_outcome("playback_failure", now_ts)

    def stopped(self, now_ts):
        if self.state == "terminal":
            return None

        if self.state == "pending":
            return self._make_outcome("probable_failure", now_ts)

        if self.state in ("started", "stable"):
            elapsed = now_ts - (self.started_at or self.created_at)
            if elapsed < EARLY_STOP_WINDOW:
                return self._make_outcome("probable_failure", now_ts)
            else:
                return self._make_outcome("completed", now_ts)

        return None

    def ended(self, now_ts):
        return self.stopped(now_ts)

    def tick(self, now_ts):
        if self.state == "terminal":
            return None

        if self.state == "pending" and (now_ts - self.created_at) >= STARTUP_TIMEOUT:
            return self._make_outcome("playback_failure", now_ts)

        if self.state == "started" and (now_ts - self.started_at) >= STABILITY_THRESHOLD:
            self.state = "stable"
            elapsed_ms = int((now_ts - self.started_at) * 1000)
            return {"outcome": "playback_success", "elapsed_ms": elapsed_ms, "attempt": self.attempt}

        return None
