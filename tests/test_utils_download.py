"""Tests for downloadVideo in utils."""

import os

import pytest

from resources.lib import utils


class DummyDialog:
    def __init__(self):
        self.browse_calls = []
        self.ok_calls = []

    def browse(self, *args, **kwargs):
        self.browse_calls.append((args, kwargs))
        return ""

    def ok(self, *args, **kwargs):
        self.ok_calls.append((args, kwargs))

    def notification(self, *args, **kwargs):
        pass


class DummyProgress:
    def __init__(self):
        self.updates = []

    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        self.updates.append((args, kwargs))

    def close(self):
        pass

    def iscanceled(self):
        return False


class DummyFile:
    def __init__(self, path, mode):
        self._file = open(path, "wb")

    def write(self, data):
        self._file.write(data)

    def close(self):
        self._file.close()


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self._offset = 0
        self.headers = {
            "Content-Length": str(len(payload)),
            "Accept-Ranges": "bytes",
        }

    def read(self, size=-1):
        if self._offset >= len(self._payload):
            return b""
        if size is None or size < 0:
            size = len(self._payload) - self._offset
        chunk = self._payload[self._offset : self._offset + size]
        self._offset += len(chunk)
        return chunk


def test_download_video_success(tmp_path, monkeypatch):
    payload = b"a" * 20480
    response = FakeResponse(payload)

    def fake_urlopen(req, timeout=30):
        return response

    monkeypatch.setattr(utils, "urlopen", fake_urlopen)
    monkeypatch.setattr(utils.xbmcvfs, "File", DummyFile, raising=False)
    monkeypatch.setattr(utils.xbmcvfs, "rename", os.replace, raising=False)
    monkeypatch.setattr(
        utils.xbmcvfs, "delete", lambda path: os.remove(path), raising=False
    )
    monkeypatch.setattr(
        utils.xbmcvfs, "makeLegalFilename", lambda path: path, raising=False
    )
    monkeypatch.setattr(
        utils.xbmcvfs, "exists", lambda path: os.path.exists(path), raising=False
    )
    monkeypatch.setattr(utils.xbmcgui, "DialogProgress", DummyProgress)

    utils.addon._settings = {**utils.addon._settings, "download_path": str(tmp_path)}

    result = utils.downloadVideo("http://example.com/video.mp4", "Test Video")

    assert result is not None
    assert os.path.exists(result)
    assert os.path.getsize(result) == len(payload)


def test_download_video_returns_none_when_no_path(monkeypatch):
    utils.addon._settings = {**utils.addon._settings, "download_path": ""}
    dummy_dialog = DummyDialog()
    monkeypatch.setattr(utils, "dialog", dummy_dialog)

    result = utils.downloadVideo("http://example.com/video.mp4", "Test Video")

    assert result is None
