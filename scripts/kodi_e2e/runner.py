"""Start and stop a real Kodi (under Xvfb) against a throwaway profile."""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import time
from pathlib import Path

from scripts.kodi_jsonrpc import KodiClient, KodiJSONRPCError

DIALOG_YESNO = 10100


def log(msg: str) -> None:
    print(f"[kodi] {msg}", flush=True)


class LogCursor:
    """Read kodi.log incrementally so each step gets only its own lines."""

    def __init__(self, path: Path):
        self.path = path
        self.pos = 0

    def mark(self) -> int:
        try:
            self.pos = self.path.stat().st_size
        except FileNotFoundError:
            self.pos = 0
        return self.pos

    def read_since(self, pos: int | None = None) -> list[str]:
        start = self.pos if pos is None else pos
        try:
            if self.path.stat().st_size < start:
                start = 0  # Kodi rotated kodi.log (restart)
            with open(self.path, "r", encoding="utf-8", errors="replace") as fh:
                fh.seek(start)
                data = fh.read()
        except FileNotFoundError:
            return []
        return data.splitlines()


class KodiInstance:
    def __init__(
        self,
        profile: Path,
        port: int = 8080,
        kodi_bin: str = "kodi",
        use_xvfb: bool | None = None,
        screen: str = "1280x720x24",
        extra_env: dict[str, str] | None = None,
    ):
        self.profile = profile.resolve()
        self.port = port
        self.kodi_bin = kodi_bin
        # Default: Xvfb unless a real display exists and the caller wants it.
        self.use_xvfb = (not os.environ.get("DISPLAY")) if use_xvfb is None else use_xvfb
        self.screen = screen
        self.extra_env = extra_env or {}
        self.proc: subprocess.Popen | None = None
        self.url = f"http://127.0.0.1:{port}/jsonrpc"
        self.client = KodiClient(self.url, timeout=15)
        self.log_path = self.profile / ".kodi" / "temp" / "kodi.log"
        self.cursor = LogCursor(self.log_path)
        self.stdout_path = self.profile / "kodi_stdout.log"
        manifest = self.profile / "kodi_e2e_manifest.json"
        self.manifest = json.loads(manifest.read_text()) if manifest.exists() else {}

    # -- lifecycle ---------------------------------------------------------
    def _env(self) -> dict[str, str]:
        env = dict(os.environ)
        env.update({
            "HOME": str(self.profile),
            "KODI_AE_SINK": "NULL",          # no audio device needed
            "LIBGL_ALWAYS_SOFTWARE": "1",
        })
        # Never send localhost (JSON-RPC, local test servers) through a proxy.
        for key in ("no_proxy", "NO_PROXY"):
            cur = env.get(key, "")
            if "127.0.0.1" not in cur:
                env[key] = ",".join(x for x in (cur, "127.0.0.1,localhost") if x)
        env.update(self.extra_env)
        return env

    def start(self, timeout: float = 120.0) -> None:
        if self.proc and self.proc.poll() is None:
            return
        cmd = [self.kodi_bin, "--standalone"]
        if self.use_xvfb:
            if not shutil.which("xvfb-run"):
                raise RuntimeError("xvfb-run not found (apt install xvfb xauth)")
            cmd = ["xvfb-run", "-a", "-s", f"-screen 0 {self.screen}"] + cmd
        log(f"starting: {' '.join(cmd)} (HOME={self.profile}, port {self.port})")
        out = open(self.stdout_path, "ab")
        self.proc = subprocess.Popen(
            cmd, env=self._env(), stdout=out, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        if not self.client.wait_until_ready(timeout=timeout, poll_interval=1.0):
            self.stop()
            raise RuntimeError(
                f"Kodi did not answer JSON-RPC on port {self.port} within {timeout}s; "
                f"see {self.log_path} and {self.stdout_path}"
            )
        self._enable_addons()
        self.settle()
        ver = self.client.call("Application.GetProperties", {"properties": ["version", "name"]})
        self.version = ver.get("version", {}) if isinstance(ver, dict) else {}
        log(f"ready: Kodi {self.version.get('major')}.{self.version.get('minor')}")

    def _enable_addons(self) -> None:
        for aid in self.manifest.get("enable", []):
            try:
                self.client.call("Addons.SetAddonEnabled", {"addonid": aid, "enabled": True})
            except KodiJSONRPCError as exc:
                log(f"could not enable {aid}: {exc}")
        main = "plugin.video.cumination"
        det = self.client.call("Addons.GetAddonDetails", {"addonid": main, "properties": ["enabled", "version"]})
        if not det.get("addon", {}).get("enabled"):
            raise RuntimeError(f"{main} is not enabled in Kodi")

    def settle(self, quiet_for: float = 3.0, timeout: float = 30.0) -> None:
        """Dismiss start-up prompts (e.g. 'enable this add-on?') until the
        GUI has been dialog-free for `quiet_for` seconds."""
        deadline = time.time() + timeout
        quiet_since = time.time()
        while time.time() < deadline:
            win = self.current_window()
            if win and win.get("id", 10000) >= 10099 and win.get("id") not in (10138, 10160):
                # addons are enabled over JSON-RPC already; answer "No" to prompts
                self.client.call("Input.Back")
                quiet_since = time.time()
            elif time.time() - quiet_since >= quiet_for:
                return
            time.sleep(0.5)

    def current_window(self) -> dict | None:
        try:
            res = self.client.call("GUI.GetProperties", {"properties": ["currentwindow"]})
            return res.get("currentwindow")
        except Exception:
            return None

    def alive(self) -> bool:
        if not self.proc or self.proc.poll() is not None:
            return False
        try:
            return self.client.call("JSONRPC.Ping") == "pong"
        except Exception:
            return False

    def stop(self, timeout: float = 20.0) -> None:
        if not self.proc:
            return
        if self.proc.poll() is None:
            try:
                KodiClient(self.url, timeout=3).call("Application.Quit")
            except Exception:
                pass
            try:
                self.proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                pass
        # Always clean the whole session group: xvfb-run leaves Xvfb behind
        # even after kodi.bin has exited.
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(self.proc.pid, sig)
            except (ProcessLookupError, PermissionError):
                break
            time.sleep(1)
        self.proc = None

    def restart(self) -> None:
        log("restarting Kodi")
        self.stop()
        time.sleep(2)
        self.start()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()
