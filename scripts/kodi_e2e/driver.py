"""User actions against a running Kodi, over JSON-RPC.

Everything here goes through Kodi itself: directories are produced by Kodi
running the plugin, thumbnails are loaded by Kodi's texture loader (the
``/image/`` endpoint), and playback is Kodi's player. While a blocking call is
in flight, a watcher thread answers dialogs the way a user would (pick the
first source, type a search term, dismiss confirmations) and records them.
"""

from __future__ import annotations

import hashlib
import io
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from scripts.kodi_jsonrpc import KodiClient, KodiJSONRPCError
from scripts.kodi_e2e.logparse import parse_log_lines

# Kodi window ids (xbmc/guilib/WindowIDs.h)
WIN_HOME = 10000
WIN_YESNO = 10100
WIN_PROGRESS = 10101
WIN_KEYBOARD = 10103
WIN_NOTIFICATION = 10107
WIN_BUSY = 10138
WIN_TEXTVIEWER = 10147
WIN_EXT_PROGRESS = 10151
WIN_BUSY_NOCANCEL = 10160
WIN_SELECT = 12000
WIN_OK = 12002
WIN_FULLSCREEN_VIDEO = 12005
WIN_VIDEO_OSD = 12901
WIN_NUMERIC = 10109

PASSIVE_WINDOWS = {WIN_PROGRESS, WIN_BUSY, WIN_BUSY_NOCANCEL, WIN_EXT_PROGRESS,
                   WIN_NOTIFICATION, WIN_FULLSCREEN_VIDEO, WIN_VIDEO_OSD}

FILE_PROPS = ["title", "thumbnail", "art", "plot", "duration", "mimetype"]


def strip_markup(text: str) -> str:
    text = re.sub(r"\[/?(COLOR|B|I|UPPERCASE|LOWERCASE|CAPITALIZE|LIGHT)[^\]]*\]", "", text or "", flags=re.I)
    return text.replace("[CR]", " ").strip()


@dataclass
class StepResult:
    action: str
    target: str
    ok: bool = False
    elapsed: float = 0.0
    error: str | None = None
    items: list[dict] = field(default_factory=list)
    dialogs: list[dict] = field(default_factory=list)
    log: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

    def to_dict(self, keep_items: int = 0) -> dict:
        d = {
            "action": self.action, "target": self.target, "ok": self.ok,
            "elapsed": round(self.elapsed, 2), "error": self.error,
            "item_count": len(self.items), "dialogs": self.dialogs,
            "log": self.log, **self.extra,
        }
        if keep_items:
            d["items"] = [
                {"label": strip_markup(i.get("label", "")), "filetype": i.get("filetype"),
                 "thumbnail": i.get("thumbnail", ""), "file": i.get("file", "")}
                for i in self.items[:keep_items]
            ]
        return d


class DialogWatcher(threading.Thread):
    """Answers dialogs while a blocking JSON-RPC call runs."""

    def __init__(self, url: str, search_term: str, poll: float = 0.4):
        super().__init__(daemon=True)
        self.client = KodiClient(url, timeout=5)
        self.search_term = search_term
        self.poll = poll
        self.events: list[dict] = []
        self._halt = threading.Event()
        self._handled_at: dict[int, float] = {}

    def stop(self):
        self._halt.set()

    def _labels(self, *labels: str) -> dict:
        try:
            return self.client.call("XBMC.GetInfoLabels", {"labels": list(labels)}) or {}
        except Exception:
            return {}

    def _record(self, kind: str, **info):
        info = {k: strip_markup(v) if isinstance(v, str) else v for k, v in info.items()}
        self.events.append({"t": round(time.time(), 1), "kind": kind, **info})

    def handle_once(self) -> None:
        try:
            win = self.client.call("GUI.GetProperties", {"properties": ["currentwindow"]})["currentwindow"]
        except Exception:
            return
        wid = win.get("id", 0)
        if wid < 10099 or wid in PASSIVE_WINDOWS:
            return
        # give Kodi a moment to populate the dialog, and don't double-handle
        now = time.time()
        if now - self._handled_at.get(wid, 0) < 1.0:
            return
        time.sleep(0.3)
        c = self.client
        if wid == WIN_KEYBOARD:
            lab = self._labels("Control.GetLabel(311)", "Control.GetLabel(1)")
            self._record("keyboard", heading=lab.get("Control.GetLabel(311)") or lab.get("Control.GetLabel(1)", ""),
                         typed=self.search_term)
            c.call("Input.SendText", {"text": self.search_term, "done": True})
        elif wid == WIN_SELECT:
            lab = self._labels("Control.GetLabel(1)", "Container(3).NumItems", "Container(6).NumItems",
                               "Container(3).ListItem(0).Label", "Container(6).ListItem(0).Label",
                               "Container(3).ListItem(1).Label", "Container(6).ListItem(1).Label")
            options = [lab.get(f"Container({n}).ListItem({i}).Label") for i in (0, 1) for n in (3, 6)]
            options = [o for o in options if o]
            count = lab.get("Container(3).NumItems") or lab.get("Container(6).NumItems") or "?"
            self._record("select", heading=lab.get("Control.GetLabel(1)", ""), options=count,
                         chose=strip_markup(options[0]) if options else "first")
            c.call("Input.Select")
        elif wid in (WIN_OK, WIN_YESNO):
            lab = self._labels("Control.GetLabel(1)", "Control.GetLabel(9)")
            kind = "ok" if wid == WIN_OK else "yesno"
            self._record(kind, heading=lab.get("Control.GetLabel(1)", ""), text=lab.get("Control.GetLabel(9)", ""))
            c.call("Input.Select" if wid == WIN_OK else "Input.Back")
        elif wid == WIN_TEXTVIEWER:
            lab = self._labels("Control.GetLabel(1)")
            self._record("textviewer", heading=lab.get("Control.GetLabel(1)", ""))
            c.call("Input.Back")
        elif wid == WIN_NUMERIC:
            self._record("numeric", heading=self._labels("Control.GetLabel(1)").get("Control.GetLabel(1)", ""))
            c.call("Input.Back")
        else:
            # Unknown dialog: only act if it sticks around.
            first = self._handled_at.setdefault(-wid, now)
            if now - first > 4:
                self._record("unknown_dialog", window=win.get("label", ""), id=wid)
                c.call("Input.Back")
                self._handled_at.pop(-wid, None)
            return
        self._handled_at[wid] = time.time()

    def run(self):
        while not self._halt.is_set():
            try:
                self.handle_once()
            except Exception:
                pass
            self._halt.wait(self.poll)


class KodiDriver:
    def __init__(self, kodi, search_term: str = "blonde"):
        self.kodi = kodi
        self.url = kodi.url
        self.search_term = search_term
        self.base = self.url.rsplit("/", 1)[0]

    # -- helpers -----------------------------------------------------------
    def _client(self, timeout: float) -> KodiClient:
        return KodiClient(self.url, timeout=timeout)

    def _run_blocking(self, fn, timeout: float, watch: bool = True):
        """Run fn() in a thread with the dialog watcher active."""
        out: dict[str, Any] = {}
        mark = self.kodi.cursor.mark()

        def target():
            try:
                out["result"] = fn()
            except Exception as exc:  # noqa: BLE001
                out["error"] = exc

        watcher = DialogWatcher(self.url, self.search_term) if watch else None
        if watcher:
            watcher.start()
        t0 = time.time()
        th = threading.Thread(target=target, daemon=True)
        th.start()
        th.join(timeout)
        elapsed = time.time() - t0
        if th.is_alive():
            out["error"] = TimeoutError(f"no answer from Kodi after {timeout:.0f}s")
        if watcher:
            watcher.stop()
            watcher.join(2)
        lines = self.kodi.cursor.read_since(mark)
        return out, elapsed, (watcher.events if watcher else []), parse_log_lines(lines)

    def reset_ui(self) -> None:
        c = self._client(5)
        for _ in range(4):
            try:
                players = c.call("Player.GetActivePlayers") or []
                for p in players:
                    c.call("Player.Stop", {"playerid": p["playerid"]})
                win = c.call("GUI.GetProperties", {"properties": ["currentwindow"]})["currentwindow"]
                if win["id"] in (WIN_HOME,) or win["id"] < 10099 and not players:
                    break
                c.call("Input.Back")
            except Exception:
                pass
            time.sleep(0.5)
        try:
            c.call("GUI.ActivateWindow", {"window": "home"})
        except Exception:
            pass

    # -- actions -----------------------------------------------------------
    def get_directory(self, url: str, timeout: float = 90.0, label: str = "") -> StepResult:
        client = self._client(timeout + 5)

        def call():
            try:
                return client.call("Files.GetDirectory", {
                    "directory": url, "media": "files", "properties": FILE_PROPS})
            except KodiJSONRPCError as exc:
                # older Kodi versions reject some fields: retry with a minimal set
                if exc.code == -32602 and "Item.Fields" in str(exc.message):
                    return client.call("Files.GetDirectory", {
                        "directory": url, "media": "files", "properties": ["title", "thumbnail", "art"]})
                raise

        out, elapsed, dialogs, logres = self._run_blocking(call, timeout)
        step = StepResult("list", label or url, elapsed=elapsed, dialogs=dialogs, log=logres)
        if "error" in out:
            err = out["error"]
            step.error = f"{type(err).__name__}: {err}"
            # Kodi answers -32602 "Invalid params" when the plugin fails or
            # returns endOfDirectory(succeeded=False).
            if isinstance(err, KodiJSONRPCError) and err.code == -32602:
                step.error = "Plugin returned an error (Kodi: invalid directory)"
        else:
            res = out.get("result") or {}
            step.items = res.get("files", []) or []
            step.ok = True
        return step

    def play(self, url: str, label: str = "", timeout: float = 75.0, min_seconds: float = 4.0) -> StepResult:
        """Start playback like selecting the item, then wait until the playhead moves."""
        self.reset_ui()
        client = self._client(10)
        state: dict[str, Any] = {"started": False}

        def call():
            client.call("Player.Open", {"item": {"file": url}})
            t_open = time.time()
            deadline = t_open + timeout
            fail_hint_at = None
            idle_since = None
            while time.time() < deadline:
                players = client.call("Player.GetActivePlayers") or []
                video = [p for p in players if p.get("type") == "video"] or players
                if video:
                    pid = video[0]["playerid"]
                    props = client.call("Player.GetProperties", {"playerid": pid, "properties": [
                        "time", "totaltime", "speed", "currentvideostream", "live"]})
                    t = _secs(props.get("time"))
                    state.update(started=True, position=t, total=_secs(props.get("totaltime")),
                                 live=props.get("live", False),
                                 stream=props.get("currentvideostream") or {})
                    if not state.get("file"):
                        item = client.call("Player.GetItem", {"playerid": pid, "properties": ["file"]})
                        state["file"] = (item or {}).get("item", {}).get("file", "")
                    if t >= min_seconds:
                        state["playing"] = True
                        return state
                else:
                    # Stop early once the failure is visible (Kodi error
                    # dialog or an addon notification) and nothing started.
                    tail = parse_log_lines(self.kodi.cursor.read_since())
                    if (tail.get("playback_errors") or tail.get("notifications")) and not state["started"]:
                        fail_hint_at = fail_hint_at or time.time()
                        if time.time() - fail_hint_at > 6:
                            return state
                    # Kodi logs nothing when a plugin exits without handing
                    # over a stream; what's visible is that the busy/progress
                    # dialog is gone and no player exists.
                    win = client.call("GUI.GetProperties", {"properties": ["currentwindow"]})["currentwindow"]
                    if win.get("id") in (WIN_BUSY, WIN_BUSY_NOCANCEL, WIN_PROGRESS, WIN_EXT_PROGRESS,
                                         WIN_SELECT, WIN_KEYBOARD):
                        idle_since = None
                    else:
                        idle_since = idle_since or time.time()
                        if time.time() - idle_since > 10 and time.time() - t_open > 12:
                            state["gave_up"] = "the addon finished without starting a video (no stream handed to Kodi)"
                            return state
                time.sleep(0.5)
            return state

        out, elapsed, dialogs, logres = self._run_blocking(call, timeout + 15)
        step = StepResult("play", label or url, elapsed=elapsed, dialogs=dialogs, log=logres)
        if "error" in out:
            step.error = f"{type(out['error']).__name__}: {out['error']}"
        st = out.get("result") or state
        step.ok = bool(st.get("playing"))
        stream = st.get("stream") or {}
        step.extra = {
            "started": bool(st.get("started")),
            "position": st.get("position"),
            "duration": st.get("total"),
            "live": st.get("live"),
            "resolved": redact(st.get("file", "")),
            "width": stream.get("width"), "height": stream.get("height"),
            "codec": stream.get("codec"),
        }
        if st.get("gave_up"):
            step.extra["gave_up"] = st["gave_up"]
        self.reset_ui()
        return step

    def fetch_image(self, image_url: str, timeout: float = 30.0) -> dict:
        """Ask Kodi to load a thumbnail exactly as the skin would."""
        res: dict[str, Any] = {"thumb": redact(unwrap_image(image_url))}
        if not image_url:
            res.update(ok=False, status="missing")
            return res
        wrapped = image_url if image_url.startswith("image://") else \
            "image://" + urllib.parse.quote(image_url, safe="") + "/"
        url = f"{self.base}/image/{urllib.parse.quote(wrapped, safe='')}"
        t0 = time.time()
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = r.read()
            res.update(status=200, bytes=len(data), sha1=hashlib.sha1(data).hexdigest()[:12])
            try:
                from PIL import Image
                with Image.open(io.BytesIO(data)) as im:
                    res.update(width=im.width, height=im.height)
                res["ok"] = True
            except ImportError:
                res["ok"] = len(data) > 0
            except Exception:
                res.update(ok=False, status="not-an-image")
        except urllib.error.HTTPError as exc:
            res.update(ok=False, status=exc.code)
        except Exception as exc:  # noqa: BLE001
            res.update(ok=False, status=type(exc).__name__)
        res["elapsed"] = round(time.time() - t0, 2)
        return res


def _secs(t: dict | None) -> float:
    if not t:
        return 0.0
    return t.get("hours", 0) * 3600 + t.get("minutes", 0) * 60 + t.get("seconds", 0) + t.get("milliseconds", 0) / 1000


def unwrap_image(img: str) -> str:
    if img.startswith("image://"):
        return urllib.parse.unquote(img[len("image://"):].rstrip("/"))
    return img


def redact(url: str) -> str:
    """Keep scheme/host/path shape, drop query strings and header pipes
    (they can contain tokens)."""
    if not url:
        return ""
    url = url.split("|", 1)[0]
    try:
        p = urllib.parse.urlsplit(url)
        if p.scheme in ("http", "https"):
            path = p.path if len(p.path) < 80 else p.path[:77] + "..."
            return f"{p.scheme}://{p.netloc}{path}"
    except ValueError:
        pass
    return url[:120]
