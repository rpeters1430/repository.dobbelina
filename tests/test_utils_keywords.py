"""Tests for keyword helpers in utils."""

import json
import os
import sqlite3
import tempfile

import pytest


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS keywords (keyword)")
    conn.commit()
    conn.close()
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def utils_module(temp_db, monkeypatch):
    from resources.lib import basics
    from resources.lib import utils

    monkeypatch.setattr(basics, "favoritesdb", temp_db)
    monkeypatch.setattr(utils, "favoritesdb", temp_db)

    utils.addon._settings = {**utils.addon._settings, "compressbackup": "false"}
    return utils


class DummyDialog:
    def __init__(self):
        self._browse_return = None
        self._yesno_return = True
        self.notifications = []
        self.ok_calls = []

    def browseSingle(self, *args, **kwargs):
        return self._browse_return

    def yesno(self, *args, **kwargs):
        return self._yesno_return

    def ok(self, *args, **kwargs):
        self.ok_calls.append((args, kwargs))

    def notification(self, *args, **kwargs):
        self.notifications.append((args, kwargs))


class DummyProgress:
    def __init__(self):
        self.created = []
        self.updated = []
        self.closed = False

    def create(self, *args, **kwargs):
        self.created.append((args, kwargs))

    def update(self, *args, **kwargs):
        self.updated.append((args, kwargs))

    def close(self):
        self.closed = True

    def iscanceled(self):
        return False


def _fetch_keywords(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT keyword FROM keywords")
    rows = [row[0] for row in c.fetchall()]
    conn.close()
    return rows


def test_add_update_delete_keyword(utils_module, temp_db):
    utils_module.addKeyword("alpha")
    assert utils_module.check_if_keyword_exists("alpha") is True

    utils_module.updateKeyword("alpha", "beta")
    rows = _fetch_keywords(temp_db)
    assert rows == ["beta"]

    utils_module.delKeyword("beta")
    assert _fetch_keywords(temp_db) == []


def test_add_keyword_duplicate_is_ignored(utils_module, temp_db):
    utils_module.addKeyword("dup")
    utils_module.addKeyword("dup")
    rows = _fetch_keywords(temp_db)
    assert rows == ["dup"]


def test_delallkeyword_clears_when_confirmed(utils_module, temp_db, monkeypatch):
    utils_module.addKeyword("keep")
    dialog = DummyDialog()
    dialog._yesno_return = True
    monkeypatch.setattr(utils_module, "dialog", dialog)

    utils_module.delallKeyword()

    assert _fetch_keywords(temp_db) == []


def test_backup_and_restore_keywords_roundtrip(
    utils_module, temp_db, tmp_path, monkeypatch
):
    utils_module.addKeyword("first")
    utils_module.addKeyword("second")

    dialog = DummyDialog()
    progress = DummyProgress()
    backup_dir = tmp_path / "backup"
    backup_dir.mkdir()
    dialog._browse_return = str(backup_dir) + os.sep

    monkeypatch.setattr(utils_module, "dialog", dialog)
    monkeypatch.setattr(utils_module, "progress", progress)

    utils_module.backup_keywords()

    backups = list(backup_dir.iterdir())
    assert len(backups) == 1

    dialog._browse_return = str(backups[0])
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("DELETE FROM keywords")
    conn.commit()
    conn.close()

    utils_module.restore_keywords()

    rows = sorted(_fetch_keywords(temp_db))
    assert rows == ["first", "second"]


def test_restore_keywords_skips_existing(utils_module, temp_db, tmp_path, monkeypatch):
    utils_module.addKeyword("alpha")

    backup = {
        "meta": {"type": "cumination-keywords", "version": 1, "datetime": "now"},
        "data": [{"keyword": "alpha"}, {"keyword": "beta"}],
    }
    backup_path = tmp_path / "keywords.bak"
    backup_path.write_text(json.dumps(backup), encoding="utf-8")

    dialog = DummyDialog()
    dialog._browse_return = str(backup_path)
    monkeypatch.setattr(utils_module, "dialog", dialog)

    utils_module.restore_keywords()

    rows = sorted(_fetch_keywords(temp_db))
    assert rows == ["alpha", "beta"]


def test_one_search_builds_container_update(utils_module, monkeypatch):
    monkeypatch.setattr(utils_module, "_get_keyboard", lambda **k: "term")

    captured = {}

    def _capture(cmd):
        captured["cmd"] = cmd

    monkeypatch.setattr(utils_module.xbmc, "executebuiltin", _capture)

    utils_module.oneSearch("https://example.com", 1, "demo.Search")

    assert "Container.Update" in captured["cmd"]
    assert "demo.Search" in captured["cmd"]


def test_new_search_adds_or_updates(utils_module, monkeypatch):
    monkeypatch.setattr(utils_module, "_get_keyboard", lambda **k: "newterm")
    calls = {"add": 0, "update": 0}

    monkeypatch.setattr(
        utils_module, "addKeyword", lambda *a, **k: calls.update(add=calls["add"] + 1)
    )
    monkeypatch.setattr(
        utils_module,
        "updateKeyword",
        lambda *a, **k: calls.update(update=calls["update"] + 1),
    )
    monkeypatch.setattr(utils_module.xbmc, "executebuiltin", lambda *a, **k: None)

    utils_module.newSearch(keyword=None)
    utils_module.newSearch(keyword="oldterm")

    assert calls["add"] == 1
    assert calls["update"] == 1


def test_copy_search_always_adds(utils_module, monkeypatch):
    monkeypatch.setattr(utils_module, "_get_keyboard", lambda **k: "copyterm")
    calls = {"add": 0}
    monkeypatch.setattr(
        utils_module, "addKeyword", lambda *a, **k: calls.update(add=calls["add"] + 1)
    )
    monkeypatch.setattr(utils_module.xbmc, "executebuiltin", lambda *a, **k: None)

    utils_module.copySearch(keyword="existing")

    assert calls["add"] == 1


def test_clear_search_calls_delall(utils_module, monkeypatch):
    called = {}
    monkeypatch.setattr(
        utils_module, "delallKeyword", lambda *a, **k: called.update(done=True)
    )
    monkeypatch.setattr(utils_module.xbmc, "executebuiltin", lambda *a, **k: None)

    utils_module.clearSearch()

    assert called.get("done") is True


def test_alphabetical_search_lists_keys(utils_module, monkeypatch):
    monkeypatch.setattr(utils_module, "keys", lambda: {"a": 2, "b": 1})
    calls = []
    monkeypatch.setattr(utils_module, "addDir", lambda *a, **k: calls.append((a, k)))
    monkeypatch.setattr(utils_module, "eod", lambda *a, **k: None)

    utils_module.alphabeticalSearch("https://example.com", "demo.Search", keyword=None)

    assert calls
