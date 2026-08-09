"""GlitchTip / Sentry envelope transport layer."""

import json
import os
from collections import namedtuple
import requests
import urllib.parse as urllib_parse

DsnParts = namedtuple("DsnParts", ["endpoint", "public_key", "project_id"])
DeliveryResult = namedtuple("DeliveryResult", ["ok", "retryable", "status_code", "event_id", "message"])


def load_telemetry_config(addon_dir):
    """Load telemetry configuration from resources/telemetry.json."""
    config_path = os.path.join(addon_dir, "resources", "telemetry.json")
    if not os.path.exists(config_path):
        return {"dsn": "", "environment": "production"}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"dsn": "", "environment": "production"}


def parse_dsn(dsn_str):
    """Parse Sentry/GlitchTip DSN into DsnParts.

    Examples:
        https://37da8a0bff7e4f50a42174c51c2d9697@glitchtip.tailb94d9.ts.net/1
        -> endpoint: https://glitchtip.tailb94d9.ts.net/api/1/envelope/
    """
    if not dsn_str or not isinstance(dsn_str, str):
        return None

    try:
        parsed = urllib_parse.urlsplit(dsn_str)
        if parsed.scheme not in ("http", "https"):
            return None

        public_key = parsed.username or ""
        path = parsed.path.strip("/")
        if not path:
            return None

        parts = path.split("/")
        project_id = parts[-1]

        # Construct endpoint
        netloc = parsed.hostname
        if parsed.port:
            netloc += f":{parsed.port}"

        base_path = "/".join(parts[:-1])
        if base_path:
            base_path = "/" + base_path

        endpoint = f"{parsed.scheme}://{netloc}{base_path}/api/{project_id}/envelope/"
        return DsnParts(endpoint=endpoint, public_key=public_key, project_id=project_id)
    except Exception:
        return None


def build_envelope(event, dsn_str):
    """Build Sentry envelope byte payload (3 newline-separated JSON objects)."""
    header = {"dsn": dsn_str, "event_id": event.get("event_id", "")}
    item_header = {"type": "event", "content_type": "application/json"}

    lines = [
        json.dumps(header),
        json.dumps(item_header),
        json.dumps(event),
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def send_event(event, dsn_str):
    """Send event envelope to GlitchTip endpoint."""
    if not dsn_str:
        return DeliveryResult(
            ok=False,
            retryable=False,
            status_code=0,
            event_id=event.get("event_id", ""),
            message="Telemetry backend is not configured (empty DSN)",
        )

    dsn_parts = parse_dsn(dsn_str)
    if not dsn_parts:
        return DeliveryResult(
            ok=False,
            retryable=False,
            status_code=0,
            event_id=event.get("event_id", ""),
            message="Invalid GlitchTip DSN format",
        )

    envelope = build_envelope(event, dsn_str)

    headers = {"Content-Type": "application/x-sentry-envelope"}
    if dsn_parts.public_key:
        headers["X-Sentry-Auth"] = f"Sentry sentry_version=7, sentry_client=cumination/1.0, sentry_key={dsn_parts.public_key}"

    try:
        resp = requests.post(
            dsn_parts.endpoint,
            data=envelope,
            headers=headers,
            timeout=(2, 3),
        )

        status = resp.status_code
        if 200 <= status < 300:
            return DeliveryResult(
                ok=True,
                retryable=False,
                status_code=status,
                event_id=event.get("event_id", ""),
                message="Accepted",
            )
        elif status in (408, 425, 429) or status >= 500:
            return DeliveryResult(
                ok=False,
                retryable=True,
                status_code=status,
                event_id=event.get("event_id", ""),
                message=f"Transient server response HTTP {status}",
            )
        else:
            return DeliveryResult(
                ok=False,
                retryable=False,
                status_code=status,
                event_id=event.get("event_id", ""),
                message=f"Permanent reject HTTP {status}",
            )

    except requests.RequestException as exc:
        return DeliveryResult(
            ok=False,
            retryable=True,
            status_code=0,
            event_id=event.get("event_id", ""),
            message=f"Network transport error: {exc.__class__.__name__}",
        )
