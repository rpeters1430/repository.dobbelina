"""Tests for favorites custom list helpers."""

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


def test_create_custom_list_inserts_row(favorites_module, temp_db, monkeypatch):
    monkeypatch.setattr(favorites_module.utils, "_get_keyboard", lambda **k: "My List")
    favorites_module.create_custom_list()
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("SELECT name FROM custom_lists WHERE name = ?", ("My List",))
    assert c.fetchone()[0] == "My List"
    conn.close()


def test_add_listitem_inserts_new(favorites_module, temp_db, monkeypatch):
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("INSERT INTO custom_lists VALUES (?)", ("Watch Later",))
    list_id = c.lastrowid
    conn.commit()
    conn.close()

    monkeypatch.setattr(
        favorites_module.utils, "selector", lambda *a, **k: str(list_id)
    )
    monkeypatch.setattr(
        favorites_module.utils.dialog, "yesno", lambda *a, **k: False, raising=False
    )

    favorites_module.add_listitem(
        "pornhub.Playvid",
        "Sample",
        "https://example.com/vid",
        "thumb.jpg",
    )

    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute(
        "SELECT name, url, mode, image, list_id FROM custom_listitems WHERE url = ?",
        ("https://example.com/vid",),
    )
    row = c.fetchone()
    conn.close()
    assert row == (
        "Sample",
        "https://example.com/vid",
        "pornhub.Playvid",
        "thumb.jpg",
        str(list_id),
    )


def test_add_listitem_updates_existing(favorites_module, temp_db, monkeypatch):
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("INSERT INTO custom_lists VALUES (?)", ("Watch Later",))
    list_id = c.lastrowid
    c.execute(
        "INSERT INTO custom_listitems VALUES (?,?,?,?,?)",
        ("Old", "https://example.com/vid", "pornhub.Playvid", "old.jpg", str(list_id)),
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr(
        favorites_module.utils, "selector", lambda *a, **k: str(list_id)
    )
    monkeypatch.setattr(
        favorites_module.utils.dialog, "yesno", lambda *a, **k: True, raising=False
    )

    favorites_module.add_listitem(
        "pornhub.Playvid",
        "New",
        "https://example.com/vid",
        "new.jpg",
    )

    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute(
        "SELECT name, image FROM custom_listitems WHERE url = ?",
        ("https://example.com/vid",),
    )
    row = c.fetchone()
    conn.close()
    assert row == ("New", "new.jpg")


def test_move_and_remove_listitems(favorites_module, temp_db, monkeypatch):
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("INSERT INTO custom_lists VALUES (?)", ("List A",))
    list_a = c.lastrowid
    c.execute("INSERT INTO custom_lists VALUES (?)", ("List B",))
    list_b = c.lastrowid
    c.execute(
        "INSERT INTO custom_listitems VALUES (?,?,?,?,?)",
        ("Item", "https://example.com/vid", "mode", "img", str(list_a)),
    )
    item_id = c.lastrowid
    conn.commit()
    conn.close()

    monkeypatch.setattr(favorites_module.utils, "selector", lambda *a, **k: str(list_b))
    favorites_module.move_listitem(item_id)

    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("SELECT list_id FROM custom_listitems WHERE rowid = ?", (item_id,))
    assert c.fetchone()[0] == str(list_b)
    conn.close()

    favorites_module.remove_listitem(item_id)
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("SELECT count(*) FROM custom_listitems WHERE rowid = ?", (item_id,))
    assert c.fetchone()[0] == 0
    conn.close()


def test_remove_list_cascades_items(favorites_module, temp_db):
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("INSERT INTO custom_lists VALUES (?)", ("List A",))
    list_id = c.lastrowid
    c.execute(
        "INSERT INTO custom_listitems VALUES (?,?,?,?,?)",
        ("Item", "https://example.com/vid", "mode", "img", str(list_id)),
    )
    conn.commit()
    conn.close()

    favorites_module.remove_list(list_id)

    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("SELECT count(*) FROM custom_lists WHERE rowid = ?", (list_id,))
    assert c.fetchone()[0] == 0
    c.execute("SELECT count(*) FROM custom_listitems WHERE list_id = ?", (list_id,))
    assert c.fetchone()[0] == 0
    conn.close()


def test_moveup_and_movedown_listitems(favorites_module, temp_db):
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("INSERT INTO custom_lists VALUES (?)", ("List A",))
    list_id = c.lastrowid
    items = [("First", "url1"), ("Second", "url2"), ("Third", "url3")]
    for name, url in items:
        c.execute(
            "INSERT INTO custom_listitems VALUES (?,?,?,?,?)",
            (name, url, "mode", "img", str(list_id)),
        )
    conn.commit()
    c.execute("SELECT rowid FROM custom_listitems WHERE url = ?", ("url2",))
    second_id = c.fetchone()[0]
    conn.close()

    favorites_module.moveup_listitem(second_id)

    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute(
        "SELECT name FROM custom_listitems WHERE list_id = ? ORDER BY rowid ASC",
        (str(list_id),),
    )
    assert [row[0] for row in c.fetchall()] == ["Second", "First", "Third"]
    c.execute("SELECT rowid FROM custom_listitems WHERE url = ?", ("url2",))
    second_id = c.fetchone()[0]
    conn.close()

    favorites_module.movedown_listitem(second_id)

    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute(
        "SELECT name FROM custom_listitems WHERE list_id = ? ORDER BY rowid ASC",
        (str(list_id),),
    )
    assert [row[0] for row in c.fetchall()] == ["First", "Second", "Third"]
    conn.close()


def test_moveup_and_movedown_lists(favorites_module, temp_db):
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("INSERT INTO custom_lists VALUES (?)", ("List One",))
    list_one_id = c.lastrowid
    c.execute("INSERT INTO custom_lists VALUES (?)", ("List Two",))
    list_two_id = c.lastrowid
    c.execute(
        "INSERT INTO custom_listitems VALUES (?,?,?,?,?)",
        ("Item One", "url1", "mode", "img", str(list_one_id)),
    )
    c.execute(
        "INSERT INTO custom_listitems VALUES (?,?,?,?,?)",
        ("Item Two", "url2", "mode", "img", str(list_two_id)),
    )
    conn.commit()
    conn.close()

    favorites_module.moveup_list(list_two_id)

    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("SELECT rowid, name FROM custom_lists ORDER BY rowid ASC")
    lists = c.fetchall()
    assert [row[1] for row in lists] == ["List Two", "List One"]
    c.execute(
        "SELECT list_id FROM custom_listitems WHERE url = ?",
        ("url2",),
    )
    assert c.fetchone()[0] == str(lists[0][0])
    conn.close()

    favorites_module.movedown_list(lists[0][0])

    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("SELECT rowid, name FROM custom_lists ORDER BY rowid ASC")
    lists = c.fetchall()
    assert [row[1] for row in lists] == ["List One", "List Two"]
    c.execute(
        "SELECT list_id FROM custom_listitems WHERE url = ?",
        ("url2",),
    )
    assert c.fetchone()[0] == str(lists[1][0])
    conn.close()


def test_edit_list_updates_name(favorites_module, temp_db, monkeypatch):
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("INSERT INTO custom_lists VALUES (?)", ("Old Name",))
    rowid = c.lastrowid
    conn.commit()
    conn.close()

    monkeypatch.setattr(favorites_module.utils, "_get_keyboard", lambda **_: "New Name")
    favorites_module.edit_list(rowid)

    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("SELECT name FROM custom_lists WHERE rowid = ?", (rowid,))
    assert c.fetchone()[0] == "New Name"
    conn.close()


def test_load_custom_list_adds_items(favorites_module, temp_db, monkeypatch):
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute(
        "INSERT INTO custom_listitems VALUES (?,?,?,?,?)",
        ("Item One", "https://example.com/1", "pornhub.Playvid", "thumb.png", "main"),
    )
    conn.commit()
    conn.close()

    class DummySite:
        def __init__(self):
            self.default_mode = "pornhub.Playvid"
            self.custom = True
            self.about = "About"
            self.title = "Pornhub"

    captured = {}

    def fake_add_dir(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs

    monkeypatch.setattr(
        favorites_module.AdultSite, "get_site_by_name", lambda *a: DummySite()
    )
    monkeypatch.setattr(favorites_module.basics, "addDir", fake_add_dir)
    monkeypatch.setattr(favorites_module.basics, "cum_image", lambda *a, **k: "fixed")
    monkeypatch.setattr(
        favorites_module.basics.addon, "getSetting", lambda *a, **k: "true"
    )
    monkeypatch.setattr(favorites_module.utils, "eod", lambda *a, **k: None)

    favorites_module.load_custom_list("main")

    assert captured["args"][0] == "Item One"
