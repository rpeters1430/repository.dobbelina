"""Tests for custom site zip installation helpers."""

import json
import os
import sqlite3
import tempfile
import zipfile

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
def favorites_module(temp_db, monkeypatch):
    import sys
    from resources.lib import basics

    original_favdb = basics.favoritesdb
    monkeypatch.setattr(basics, "favoritesdb", temp_db)
    if "resources.lib.favorites" in sys.modules:
        del sys.modules["resources.lib.favorites"]
    from resources.lib import favorites

    monkeypatch.setattr(favorites, "favoritesdb", temp_db)
    yield favorites
    basics.favoritesdb = original_favdb


def test_process_custom_site_zip_installs_files(favorites_module, tmp_path, monkeypatch):
    temp_dir = tmp_path / "temp"
    custom_dir = tmp_path / "custom"
    temp_dir.mkdir()
    custom_dir.mkdir()

    monkeypatch.setattr(favorites_module.basics, "tempDir", str(temp_dir))
    monkeypatch.setattr(favorites_module.basics, "customSitesDir", str(custom_dir))
    monkeypatch.setattr(favorites_module.basics, "clean_temp", lambda: None)

    meta = {
        "name": "mysite",
        "module_name": "site.py",
        "author": "me",
        "version": "1.0",
        "title": "My Site",
        "url": "https://example.com",
        "image": "image.png",
        "about": "about.txt",
    }

    zip_path = tmp_path / "site.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("meta.json", json.dumps(meta))
        zf.writestr("site.py", "# test\n")
        zf.writestr("image.png", b"img")
        zf.writestr("about.txt", "about")

    assert favorites_module.process_custom_site_zip(str(zip_path)) is True

    expected_module = custom_dir / "custom_1.py"
    expected_image = custom_dir / "me_mysite_img.png"
    expected_about = custom_dir / "me_mysite_about.txt"

    assert expected_module.exists()
    assert expected_image.exists()
    assert expected_about.exists()

    conn = sqlite3.connect(favorites_module.favoritesdb)
    c = conn.cursor()
    c.execute("SELECT name, title, version FROM custom_sites WHERE author = ?", ("me",))
    row = c.fetchone()
    conn.close()
    assert row == ("mysite", "My Site", "1.0")
