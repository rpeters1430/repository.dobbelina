"""Structured diagnostic telemetry reporter facade."""

import contextlib
import datetime
import os
import sys
import uuid
from resources.lib import telemetry_privacy as privacy
from resources.lib import telemetry_store as store_mod
from resources.lib import telemetry_transport as transport_mod

_REPORTER_INSTANCE = None


def get_reporter(addon_dir=None, profile_dir=None):
    global _REPORTER_INSTANCE
    if _REPORTER_INSTANCE is None:
        _REPORTER_INSTANCE = TelemetryReporter(addon_dir=addon_dir, profile_dir=profile_dir)
    return _REPORTER_INSTANCE


class TelemetryReporter:

    def __init__(self, addon_dir=None, profile_dir=None, enabled_override=None):
        if not addon_dir:
            addon_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if not profile_dir:
            profile_dir = addon_dir

        self.addon_dir = addon_dir
        self.profile_dir = profile_dir
        self.enabled_override = enabled_override

        self.config = transport_mod.load_telemetry_config(self.addon_dir)
        self.store = store_mod.TelemetryStore(self.profile_dir)
        self.current_context = None
        self.breadcrumbs = []

    def enabled(self):
        if self.enabled_override is not None:
            return self.enabled_override

        try:
            import xbmcaddon

            addon = xbmcaddon.Addon()
            val = addon.getSetting("telemetry_enabled")
            return str(val).lower() == "true"
        except Exception:
            return False

    def cleanup_if_disabled(self):
        if not self.enabled():
            self.store.clear()
            self.breadcrumbs = []
            self.current_context = None

    def add_breadcrumb(self, category, message, data=None):
        if not self.enabled():
            return
        crumb = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "category": str(category),
            "message": privacy.sanitize_text(message, addon_root=self.addon_dir),
        }
        if isinstance(data, dict):
            crumb["data"] = {
                k: privacy.sanitize_text(v, addon_root=self.addon_dir)
                for k, v in data.items()
                if not privacy.SECRET_KEY_PATTERN.match(k)
            }
        self.breadcrumbs.append(crumb)
        if len(self.breadcrumbs) > 30:
            self.breadcrumbs.pop(0)

    @contextlib.contextmanager
    def operation_scope(self, mode, queries):
        if not self.enabled():
            yield
            return

        site = (mode or "main").split(".")[0]
        op = (mode or "main").split(".")[-1]
        self.current_context = {
            "site": site,
            "operation": op,
            "started": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "items": 0,
        }
        try:
            yield
            self.finish_operation()
        except Exception as exc:
            self.capture_exception(exc)
            raise
        finally:
            self.current_context = None

    def capture_exception(self, exc):
        if not self.enabled():
            return

        event_id = uuid.uuid4().hex
        site = self.current_context.get("site", "main") if self.current_context else "main"
        op = self.current_context.get("operation", "main") if self.current_context else "main"

        safe_exc = privacy.safe_exception(exc, addon_root=self.addon_dir)
        top_frame = safe_exc.get("frames", [{}])[-1].get("function", "unknown") if safe_exc.get("frames") else "unknown"
        fingerprint = f"addon_exception|{site}|{op}|{safe_exc.get('type')}|{top_frame}"

        allowed, suppressed = self.store.allow(fingerprint, "addon_exception")
        if not allowed:
            return

        event = {
            "event_id": event_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": "error",
            "logger": "cumination.telemetry.v1",
            "release": "1.1.449",
            "environment": self.config.get("environment", "production"),
            "message": safe_exc.get("value", "Exception"),
            "fingerprint": [fingerprint],
            "tags": {
                "event_type": "addon_exception",
                "site": site,
                "operation": op,
                "installation_id": self.store.installation_id(),
            },
            "contexts": {
                "runtime": {"python_version": sys.version.split()[0]},
            },
            "exception": safe_exc,
            "breadcrumbs": list(self.breadcrumbs),
        }
        if suppressed > 0:
            event["tags"]["suppressed_count"] = str(suppressed)

        sanitized = privacy.sanitize_event(event, addon_root=self.addon_dir)
        self.store.enqueue(sanitized)
        self.drain_once(limit=3)

    def note_listing_item(self):
        """Track that one listing item was successfully generated."""
        if not self.enabled() or not self.current_context:
            return
        self.current_context["items"] = self.current_context.get("items", 0) + 1

    def finish_operation(self):
        if not self.enabled() or not self.current_context:
            return

        op = self.current_context.get("operation", "")
        # Empty listings for List/Search operations are classified as load failures
        if op in ("List", "Search") and self.current_context.get("items", 0) == 0:
            if op == "List":
                self.http_outcome(
                    url="https://" + self.current_context.get("site", "unknown") + ".com",
                    classification="empty_listing"
                )

    def http_outcome(self, url, classification, status=0, elapsed_ms=0, final_url=""):
        """Record site load (HTTP/network) outcomes and empty listing detections."""
        if not self.enabled():
            return

        site = self.current_context.get("site", "main") if self.current_context else "main"
        op = self.current_context.get("operation", "main") if self.current_context else "main"

        from six.moves import urllib_parse
        parsed = urllib_parse.urlparse(url)
        domain = parsed.netloc.split(":")[0] if parsed.netloc else ""

        fingerprint = f"site_load_failure|{site}|{op}|{classification}|{status}|{domain}"
        allowed, suppressed = self.store.allow(fingerprint, "site_load_failure")
        if not allowed:
            return

        event_id = uuid.uuid4().hex
        event = {
            "event_id": event_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": "warning" if classification == "empty_listing" else "error",
            "logger": "cumination.telemetry.v1",
            "release": "1.1.449",
            "environment": self.config.get("environment", "production"),
            "message": f"Site load failure: {classification}",
            "fingerprint": [fingerprint],
            "tags": {
                "event_type": "site_load_failure",
                "site": site,
                "operation": op,
                "installation_id": self.store.installation_id(),
                "classification": classification,
            },
            "contexts": {
                "http": {
                    "url": url,
                    "status_code": status,
                    "method": "GET",
                    "elapsed_ms": int(elapsed_ms),
                },
                "runtime": {"python_version": sys.version.split()[0]},
            },
        }
        if suppressed > 0:
            event["tags"]["suppressed_count"] = str(suppressed)

        sanitized = privacy.sanitize_event(event, addon_root=self.addon_dir)
        self.store.enqueue(sanitized)

    def resolve_failure(self, resolver_name, classification, error_msg=""):
        """Record stream resolution or handoff failures."""
        if not self.enabled():
            return

        site = self.current_context.get("site", "main") if self.current_context else "main"
        op = self.current_context.get("operation", "main") if self.current_context else "main"

        fingerprint = f"resolve_failure|{site}|{op}|{resolver_name}|{classification}"
        allowed, suppressed = self.store.allow(fingerprint, "resolve_failure")
        if not allowed:
            return

        event_id = uuid.uuid4().hex
        event = {
            "event_id": event_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": "error",
            "logger": "cumination.telemetry.v1",
            "release": "1.1.449",
            "environment": self.config.get("environment", "production"),
            "message": f"Resolve failure: {classification}",
            "fingerprint": [fingerprint],
            "tags": {
                "event_type": "resolve_failure",
                "site": site,
                "operation": op,
                "installation_id": self.store.installation_id(),
                "resolver": resolver_name,
            },
            "contexts": {
                "resolver": {
                    "error_message": error_msg,
                },
                "runtime": {"python_version": sys.version.split()[0]},
            },
        }
        if suppressed > 0:
            event["tags"]["suppressed_count"] = str(suppressed)

        sanitized = privacy.sanitize_event(event, addon_root=self.addon_dir)
        self.store.enqueue(sanitized)

    def start_playback_attempt(self, url, inputstream_addon=None):
        """Save playback metadata details atomically with a unique attempt ID."""
        if not self.enabled():
            return

        from six.moves import urllib_parse
        parsed = urllib_parse.urlparse(url)
        scheme = parsed.scheme or ""
        netloc = parsed.netloc
        if "@" in netloc:
            netloc = netloc.split("@")[-1]
        domain = netloc.split(":")[0] if ":" in netloc else netloc

        protocol = "progressive"
        url_lower = url.lower()
        if ".m3u8" in url_lower or "hlsv2" in url_lower or "hls" in url_lower:
            protocol = "hls"
        elif ".mpd" in url_lower:
            protocol = "dash"
        elif ".ism" in url_lower:
            protocol = "smooth"

        attempt = {
            "attempt_id": uuid.uuid4().hex,
            "created_at": self.store.now(),
            "site": self.current_context.get("site", "main") if self.current_context else "main",
            "operation": self.current_context.get("operation", "main") if self.current_context else "main",
            "domain": domain,
            "scheme": scheme,
            "protocol": protocol,
            "inputstream": inputstream_addon,
        }
        self.store.save_playback_attempt(attempt)

    def load_playback_attempt(self):
        """Load atomic playback attempt details."""
        if not self.enabled():
            return None
        return self.store.load_playback_attempt()

    def clear_playback_attempt(self):
        """Clear atomic playback attempt file."""
        if not self.enabled():
            return
        self.store.clear_playback_attempt()

    def playback_outcome(self, outcome):
        """Report a playback failure or sampled success to GlitchTip."""
        if not self.enabled():
            return

        outcome_type = outcome.get("outcome")
        if not outcome_type:
            return

        attempt = outcome.get("attempt") or {}
        site = attempt.get("site", "main")
        op = attempt.get("operation", "main")
        attempt_id = attempt.get("attempt_id", "")

        if outcome_type == "playback_success":
            # 10% deterministic sampling rate
            import hashlib
            h = hashlib.sha256(attempt_id.encode("utf-8")).hexdigest()[:8]
            val = int(h, 16) % 100
            if val >= 10:
                return

        fingerprint = f"playback_outcome|{site}|{op}|{outcome_type}"
        allowed, suppressed = self.store.allow(fingerprint, outcome_type)
        if not allowed:
            return

        event_id = uuid.uuid4().hex
        event = {
            "event_id": event_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": "info" if outcome_type == "playback_success" else "warning",
            "logger": "cumination.telemetry.v1",
            "release": "1.1.449",
            "environment": self.config.get("environment", "production"),
            "message": f"Playback outcome: {outcome_type}",
            "fingerprint": [fingerprint],
            "tags": {
                "event_type": outcome_type,
                "site": site,
                "operation": op,
                "installation_id": self.store.installation_id(),
            },
            "contexts": {
                "playback": {
                    "attempt_id": attempt_id,
                    "elapsed_ms": int(outcome.get("elapsed_ms", 0)),
                    "protocol": attempt.get("protocol", "progressive"),
                    "inputstream": attempt.get("inputstream", "none") or "none",
                },
                "runtime": {"python_version": sys.version.split()[0]},
            },
        }
        if suppressed > 0:
            event["tags"]["suppressed_count"] = str(suppressed)

        sanitized = privacy.sanitize_event(event, addon_root=self.addon_dir)
        self.store.enqueue(sanitized)

    def send_test_report(self):
        event_id = uuid.uuid4().hex
        event = {
            "event_id": event_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "level": "info",
            "logger": "cumination.telemetry.v1",
            "release": "1.1.449",
            "environment": self.config.get("environment", "production"),
            "message": "Cumination Diagnostic Test Report",
            "fingerprint": ["test_report"],
            "tags": {
                "event_type": "test_report",
                "installation_id": self.store.installation_id(),
            },
        }
        sanitized = privacy.sanitize_event(event, addon_root=self.addon_dir)
        return transport_mod.send_event(sanitized, self.config.get("dsn", ""))

    def drain_once(self, limit=5):
        if not self.enabled():
            self.cleanup_if_disabled()
            return

        ready = self.store.peek(limit=limit)
        for item in ready:
            ev = item.get("event", {})
            res = transport_mod.send_event(ev, self.config.get("dsn", ""))
            if res.ok:
                self.store.ack(res.event_id)
            elif not res.retryable:
                self.store.ack(res.event_id)
            else:
                self.store.retry(res.event_id)
