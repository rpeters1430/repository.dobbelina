"""Tests for custom site management helpers."""

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
    c.executescript(
        """
        CREATE TABLE IF NOT EXISTS favorites (name, url, mode, image, duration, quality);
        CREATE TABLE IF NOT EXISTS keywords (keyword);
        CREATE TABLE IF NOT EXISTS custom_sites (author, name, title, url, image, about, version, installed_at, enabled, module_file);
        CREATE TABLE IF NOT EXISTS custom_lists (name);
        CREATE TABLE IF NOT EXISTS custom_listitems (name, url, mode, image, list_id);
        """
    )
    conn.commit()
    conn.close()
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def favorites_module(temp_db, monkeypatch, tmp_path):
    import sys
    from resources.lib import basics

    original_favdb = basics.favoritesdb
    monkeypatch.setattr(basics, "favoritesdb", temp_db)
    monkeypatch.setattr(basics, "customSitesDir", str(tmp_path / "custom"))
    (tmp_path / "custom").mkdir()

    if "resources.lib.favorites" in sys.modules:
        del sys.modules["resources.lib.favorites"]
    from resources.lib import favorites

    monkeypatch.setattr(favorites, "favoritesdb", temp_db)
    yield favorites
    basics.favoritesdb = original_favdb


def _insert_custom_site(db_path, author, name, title, enabled):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "INSERT INTO custom_sites VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            author,
            name,
            title,
            "https://example.com",
            "image.png",
            "about",
            "1.0",
            "now",
            enabled,
            "custom_1",
        ),
    )
    conn.commit()
    conn.close()


def test_enable_custom_site(favorites_module, monkeypatch):
    _insert_custom_site(favorites_module.favoritesdb, "me", "site", "My Site", 0)

    monkeypatch.setattr(favorites_module.utils.dialog, "yesno", lambda *a, **k: True)
    monkeypatch.setattr(
        favorites_module.utils,
        "selector",
        lambda *a, **k: ["me", "site", "My Site"],
    )
    monkeypatch.setattr(favorites_module.utils, "notify", lambda *a, **k: None)

    favorites_module.enable_custom_site()

    conn = sqlite3.connect(favorites_module.favoritesdb)
    c = conn.cursor()
    c.execute("SELECT enabled FROM custom_sites WHERE name = ?", ("site",))
    assert c.fetchone()[0] == 1
    conn.close()


def test_disable_custom_site(favorites_module, monkeypatch):
    _insert_custom_site(favorites_module.favoritesdb, "me", "site", "My Site", 1)

    monkeypatch.setattr(
        favorites_module.utils,
        "selector",
        lambda *a, **k: ["me", "site", "My Site"],
    )
    monkeypatch.setattr(favorites_module.utils, "notify", lambda *a, **k: None)

    favorites_module.disable_custom_site()

    conn = sqlite3.connect(favorites_module.favoritesdb)
    c = conn.cursor()
    c.execute("SELECT enabled FROM custom_sites WHERE name = ?", ("site",))
    assert c.fetchone()[0] == 0
    conn.close()


def test_enable_all_custom_sites(favorites_module, monkeypatch):
    _insert_custom_site(favorites_module.favoritesdb, "me", "site1", "Site 1", 0)
    _insert_custom_site(favorites_module.favoritesdb, "me", "site2", "Site 2", 0)

    monkeypatch.setattr(favorites_module.utils.dialog, "yesno", lambda *a, **k: True)
    monkeypatch.setattr(favorites_module.utils, "textBox", lambda *a, **k: None)
    monkeypatch.setattr(favorites_module.utils, "notify", lambda *a, **k: None)

    favorites_module.enable_all_custom_sites()

    conn = sqlite3.connect(favorites_module.favoritesdb)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM custom_sites WHERE enabled = 1")
    assert c.fetchone()[0] == 2
    conn.close()


def test_disable_all_custom_sites(favorites_module, monkeypatch):
    _insert_custom_site(favorites_module.favoritesdb, "me", "site1", "Site 1", 1)
    _insert_custom_site(favorites_module.favoritesdb, "me", "site2", "Site 2", 1)

    monkeypatch.setattr(favorites_module.utils.dialog, "yesno", lambda *a, **k: True)
    monkeypatch.setattr(favorites_module.utils, "textBox", lambda *a, **k: None)
    monkeypatch.setattr(favorites_module.utils, "notify", lambda *a, **k: None)

    favorites_module.disable_all_custom_sites()

    conn = sqlite3.connect(favorites_module.favoritesdb)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM custom_sites WHERE enabled = 0")
    assert c.fetchone()[0] == 2
    conn.close()


def test_list_custom_sites(favorites_module, monkeypatch):
    _insert_custom_site(favorites_module.favoritesdb, "me", "site1", "Site 1", 1)
    _insert_custom_site(favorites_module.favoritesdb, "me", "site2", "Site 2", 0)

    captured = {}

    def _capture_textbox(_title, text):
        captured["text"] = text

    monkeypatch.setattr(favorites_module.utils, "textBox", _capture_textbox)
    monkeypatch.setattr(favorites_module.utils, "notify", lambda *a, **k: None)

    favorites_module.list_custom_sites()

    assert "Enabled sites" in captured["text"]
    assert "Disabled sites" in captured["text"]


def test_uninstall_custom_site(favorites_module, monkeypatch, tmp_path):
    _insert_custom_site(favorites_module.favoritesdb, "me", "site", "My Site", 1)

    monkeypatch.setattr(
        favorites_module.utils,
        "selector",
        lambda *a, **k: ["me", "site", "My Site"],
    )
    monkeypatch.setattr(favorites_module.utils, "notify", lambda *a, **k: None)

    favorites_module.uninstall_custom_site()

    conn = sqlite3.connect(favorites_module.favoritesdb)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM custom_sites WHERE name = ?", ("site",))
    assert c.fetchone()[0] == 0
    conn.close()


def test_install_custom_site_success(favorites_module, monkeypatch, tmp_path):
    zip_path = tmp_path / "dummy.zip"
    zip_path.write_text("placeholder", encoding="utf-8")

    _insert_custom_site(favorites_module.favoritesdb, "me", "site", "My Site", 1)

    monkeypatch.setattr(favorites_module.utils.dialog, "yesno", lambda *a, **k: True)
    monkeypatch.setattr(
        favorites_module.utils.dialog,
        "browseSingle",
        lambda *a, **k: str(zip_path),
        raising=False,
    )
    monkeypatch.setattr(
        favorites_module, "process_custom_site_zip", lambda *a, **k: True
    )
    monkeypatch.setattr(favorites_module.utils, "notify", lambda *a, **k: None)

    favorites_module.install_custom_site()


def test_install_custom_sites_from_folder(favorites_module, monkeypatch, tmp_path):
    folder = tmp_path / "zips"
    folder.mkdir()
    (folder / "one.zip").write_text("a", encoding="utf-8")
    (folder / "two.zip").write_text("b", encoding="utf-8")

    class DummyProgress:
        def create(self, *args, **kwargs):
            pass

        def update(self, *args, **kwargs):
            pass

        def close(self):
            pass

    monkeypatch.setattr(favorites_module.utils.dialog, "yesno", lambda *a, **k: True)
    monkeypatch.setattr(
        favorites_module.utils.xbmcgui.Dialog,
        "browseSingle",
        lambda *a, **k: str(folder),
        raising=False,
    )
    monkeypatch.setattr(favorites_module.utils, "progress", DummyProgress())
    monkeypatch.setattr(favorites_module.utils, "textBox", lambda *a, **k: None)
    monkeypatch.setattr(
        favorites_module, "process_custom_site_zip", lambda *a, **k: True
    )

    favorites_module.install_custom_sites_from_folder()
