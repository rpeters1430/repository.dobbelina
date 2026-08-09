"""Durable queue, cooldown tracking, sampling, and ID management for telemetry."""

import hashlib
import json
import os
import random
import shutil
import time


class TelemetryStore:

    def __init__(
        self,
        profile_dir,
        now=time.time,
        random_bytes=os.urandom,
        random_value=random.random,
        max_events=100,
        max_bytes=524288,
    ):
        self.profile_dir = profile_dir
        self.telemetry_dir = os.path.join(profile_dir, "telemetry")
        self.queue_file = os.path.join(self.telemetry_dir, "queue.json")
        self.rate_file = os.path.join(self.telemetry_dir, "rate.json")
        self.id_file = os.path.join(self.telemetry_dir, "installation_id")
        self.now = now
        self.random_bytes = random_bytes
        self.random_value = random_value
        self.max_events = max_events
        self.max_bytes = max_bytes

    def _ensure_dir(self):
        if not os.path.exists(self.telemetry_dir):
            os.makedirs(self.telemetry_dir, exist_ok=True)

    def _atomic_write_json(self, filepath, data):
        self._ensure_dir()
        tmp_file = filepath + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_file, filepath)

    def _read_json(self, filepath, default):
        if not os.path.exists(filepath):
            return default
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def installation_id(self):
        """Lazy-get or create a 32-hex random installation ID."""
        if os.path.exists(self.id_file):
            try:
                with open(self.id_file, "r", encoding="utf-8") as f:
                    val = f.read().strip()
                    if len(val) == 32:
                        return val
            except Exception:
                pass

        self._ensure_dir()
        new_id = self.random_bytes(16).hex()
        tmp_file = self.id_file + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write(new_id)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_file, self.id_file)
        return new_id

    def enqueue(self, event):
        """Atomically enqueue a sanitized telemetry event with queue caps."""
        queue = self._read_json(self.queue_file, [])
        item = {
            "event": event,
            "retries": 0,
            "next_attempt": 0,
            "created_at": self.now(),
        }
        queue.append(item)

        # Evict if exceeding max events
        while len(queue) > self.max_events:
            # Try evicting oldest success event first
            success_idx = next(
                (
                    i
                    for i, q in enumerate(queue)
                    if q.get("event", {}).get("tags", {}).get("event_type") == "playback_success"
                ),
                0,
            )
            queue.pop(success_idx)

        # Check total bytes cap
        while len(json.dumps(queue)) > self.max_bytes and queue:
            queue.pop(0)

        self._atomic_write_json(self.queue_file, queue)

    def peek(self, limit=5):
        """Return ready items for delivery."""
        queue = self._read_json(self.queue_file, [])
        now_ts = self.now()
        ready = [q for q in queue if q.get("next_attempt", 0) <= now_ts]
        return ready[:limit]

    def ack(self, event_id):
        """Acknowledge and remove an event from queue."""
        queue = self._read_json(self.queue_file, [])
        queue = [q for q in queue if q.get("event", {}).get("event_id") != event_id]
        self._atomic_write_json(self.queue_file, queue)

    def retry(self, event_id):
        """Increment retries and set next_attempt backoff, drop if retries >= 8."""
        queue = self._read_json(self.queue_file, [])
        new_queue = []
        for q in queue:
            if q.get("event", {}).get("event_id") == event_id:
                retries = q.get("retries", 0) + 1
                if retries >= 8:
                    continue  # drop
                delay = min(3600, (2**retries) * 5) * (0.8 + 0.4 * self.random_value())
                q["retries"] = retries
                q["next_attempt"] = self.now() + delay
            new_queue.append(q)
        self._atomic_write_json(self.queue_file, new_queue)

    def allow(self, fingerprint, event_type):
        """Check cooldown windows and track suppressed count.

        Returns (allowed: bool, suppressed_count: int).
        """
        rates = self._read_json(self.rate_file, {})
        now_ts = self.now()
        cooldown = 3600 if event_type == "playback_success" else 300

        record = rates.get(fingerprint, {"last_sent": 0, "suppressed": 0})
        last_sent = record.get("last_sent", 0)
        suppressed = record.get("suppressed", 0)

        if now_ts - last_sent < cooldown:
            record["suppressed"] = suppressed + 1
            rates[fingerprint] = record
            self._atomic_write_json(self.rate_file, rates)
            return False, record["suppressed"]

        res_suppressed = suppressed
        rates[fingerprint] = {"last_sent": now_ts, "suppressed": 0}
        self._atomic_write_json(self.rate_file, rates)
        return True, res_suppressed

    def sample_success(self, attempt_id):
        """Deterministic 10% sampling using SHA-256 hash of attempt_id."""
        if not attempt_id:
            return False
        h = hashlib.sha256(attempt_id.encode("utf-8")).hexdigest()
        val = int(h[:8], 16) % 100
        return val < 10

    def clear(self):
        """Completely remove all telemetry directory state."""
        if os.path.exists(self.telemetry_dir):
            try:
                shutil.rmtree(self.telemetry_dir)
            except Exception:
                pass
