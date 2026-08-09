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
        except Exception as exc:
            self.capture_exception(exc)
            raise
        finally:
            self.finish_operation()
            self.current_context = None

    def finish_operation(self):
        if not self.enabled() or not self.current_context:
            return

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
