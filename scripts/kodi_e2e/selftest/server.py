"""Local HTTP server + media for the harness self-test (no internet needed)."""

from __future__ import annotations

import json
import shutil
import subprocess
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

GOOD_TITLES = [
    "Sunset beach walk", "Morning yoga session", "City lights tour", "Mountain cabin weekend",
    "Poolside afternoon", "Road trip diaries", "Rainy day indoors", "Garden party",
    "Studio photoshoot", "Lakeside picnic", "Rooftop evening", "Desert drive",
]


def make_media(root: Path) -> None:
    """Thumbnails (Pillow) and a short H.264 clip (ffmpeg)."""
    from PIL import Image, ImageDraw

    media = root / "media"
    media.mkdir(parents=True, exist_ok=True)
    for i in range(40):
        im = Image.new("RGB", (320, 180), ((i * 53) % 255, (i * 97) % 255, (i * 31) % 255))
        ImageDraw.Draw(im).text((10, 10), f"thumb {i}", fill=(255, 255, 255))
        im.save(media / f"t{i}.jpg", quality=80)
    Image.new("RGB", (40, 30), (120, 120, 120)).save(media / "tiny.jpg")
    clip = media / "video.mp4"
    if not clip.exists():
        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg is needed for the self-test clip (apt install ffmpeg)")
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=640x360:rate=25",
             "-t", "30", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "ultrafast",
             "-movflags", "+faststart", str(clip)],
            check=True,
        )


class Handler(SimpleHTTPRequestHandler):
    base = ""

    def log_message(self, *a):  # quiet
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        u = urlsplit(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        b = self.base
        if u.path in ("/good/list", "/good/search"):
            page = int(q.get("page", 1))
            if u.path == "/good/search" and not q.get("q"):
                return self._json({"videos": [], "page": page})
            offset = (page - 1) * 12 + (100 if q.get("cat") else 0) + (200 if q.get("q") else 0)
            vids = [{"title": f"{GOOD_TITLES[i % 12]} part {chr(65 + (offset + i) % 26)}{page}",
                     "url": f"{b}/media/video.mp4?v={offset + i}",
                     "thumb": f"{b}/media/t{(offset + i) % 40}.jpg"} for i in range(12)]
            nxt = f"{b}{u.path}?" + "&".join(f"{k}={v}" for k, v in {**q, "page": page + 1}.items())
            return self._json({"videos": vids, "page": page, "next": nxt if page < 3 else None})
        if u.path == "/good/cats":
            return self._json({"categories": [
                {"name": n, "url": f"{b}/good/list?cat={n.lower()}&page=1", "thumb": f"{b}/media/t{30 + i}.jpg"}
                for i, n in enumerate(["Outdoor", "Travel", "Studio"])]})
        if u.path == "/broken/list":
            if q.get("q") or q.get("cat"):
                return self._json({"videos": []})
            titles = ["Hot &amp; Wild 1", "12:34 Beach day 88123456", "08:15 Pool party 77123456",
                      "<b>Studio</b> session", "22:10 Picnic 55123456", "Garden 11:02",
                      "Lake trip 99123456", "Road 44123456", "Cabin 33123456 21:00", "Night out 66123456"]
            thumbs = [f"{b}/media/missing{i}.jpg" for i in range(5)] + [f"{b}/media/tiny.jpg"] * 5
            return self._json({"videos": [
                {"title": t, "url": f"{b}/broken/video{i}", "thumb": thumbs[i]} for i, t in enumerate(titles)]})
        if u.path == "/broken/search":
            return self._json({"videos": []})
        if u.path == "/broken/cats":
            return self._json({"categories": [
                {"name": "", "url": f"{b}/broken/list?cat=x", "thumb": ""},
                {"name": "", "url": f"{b}/broken/list?cat=y", "thumb": ""},
                {"name": "Empty Cat", "url": f"{b}/broken/list?cat=empty", "thumb": f"{b}/media/tiny.jpg"},
                {"name": "Crash Cat", "url": f"{b}/broken/crash", "thumb": f"{b}/media/tiny.jpg", "mode": "Crash"},
            ]})
        if u.path.startswith("/broken/video"):
            body = b"<html><body><p>This video has been removed.</p></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if u.path.startswith("/media/"):
            self.path = u.path  # drop query string for static files
            return super().do_GET()
        self.send_error(404)

    do_HEAD = SimpleHTTPRequestHandler.do_HEAD


class QuietServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        # Kodi drops the video connection when playback is stopped; not an error.
        pass


def serve(root: Path, port: int) -> ThreadingHTTPServer:
    make_media(root)
    handler = partial(type("H", (Handler,), {"base": f"http://127.0.0.1:{port}"}), directory=str(root))
    httpd = QuietServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd
