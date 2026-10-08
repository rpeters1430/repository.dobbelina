"""Shared helpers for site tests that run against saved real-page fixtures."""

from unittest.mock import MagicMock

from resources.lib import utils
from tests.conftest import read_fixture


class SiteRecorder:
    """Capture what a site module would list, notify and play.

    The player is a ``MagicMock`` spec'd on the real ``utils.VideoPlayer`` so a
    site calling a playback method that does not exist fails the test instead
    of being silently accepted by a hand-written dummy.
    """

    def __init__(self, monkeypatch, module, pages=None):
        self.videos = []
        self.dirs = []
        self.notifications = []
        self.requests = []
        self.pages = pages or {}

        self.player = MagicMock(spec=utils.VideoPlayer)
        self.player.progress = MagicMock()
        self.player.resolveurl = MagicMock()

        monkeypatch.setattr(module.site, "add_download_link", self._add_video)
        monkeypatch.setattr(module.site, "add_dir", self._add_dir)
        monkeypatch.setattr(module.utils, "eod", lambda *a, **k: None)
        monkeypatch.setattr(
            module.utils, "notify", lambda *a, **k: self.notifications.append(a)
        )
        monkeypatch.setattr(module.utils, "getHtml", self._get_html)
        monkeypatch.setattr(
            module.utils, "VideoPlayer", lambda *a, **k: self.player
        )

    def _add_video(self, name, url, mode, iconimage, desc="", **kwargs):
        self.videos.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "icon": iconimage,
                "duration": kwargs.get("duration", ""),
                "quality": kwargs.get("quality", ""),
            }
        )

    def _add_dir(self, name, url, mode, iconimage=None, *args, **kwargs):
        self.dirs.append({"name": name, "url": url, "mode": mode, "icon": iconimage})

    def _get_html(self, url, referer="", *args, **kwargs):
        self.requests.append((url, referer))
        for needle, fixture in self.pages.items():
            if needle in url:
                return read_fixture(fixture)
        return ""

    def dirs_for(self, mode):
        return [d for d in self.dirs if d["mode"] == mode]

    @property
    def next_page(self):
        pages = [d for d in self.dirs if d["name"].startswith("Next Page")]
        return pages[-1]["url"] if pages else None

    @property
    def played(self):
        """Return ``(method_name, first_argument)`` for each playback call."""
        return [
            (call[0], call[1][0] if call[1] else None)
            for call in self.player.method_calls
            if call[0].startswith("play_from")
        ]
