#!/usr/bin/env python3
"""Tests for build_repo_addons.py."""

import hashlib
import xml.etree.ElementTree as ET
import zipfile

import pytest

from build_repo_addons import (
    build_zip,
    find_addons,
    is_excluded,
    read_addon_meta,
    update_addons_index,
)


def test_is_excluded(tmp_path):
    addon_root = tmp_path / "plugin.video.test"
    addon_root.mkdir()

    assert is_excluded(addon_root / ".git" / "config", addon_root) is True
    assert is_excluded(addon_root / "lib" / "__pycache__" / "a.pyc", addon_root) is True
    assert is_excluded(addon_root / "old.zip", addon_root) is True
    assert is_excluded(addon_root / ".DS_Store", addon_root) is True
    assert is_excluded(addon_root / "addon.xml", addon_root) is False
    assert is_excluded(addon_root / "resources" / "lib" / "default.py", addon_root) is False


def test_read_addon_meta(tmp_path):
    addon_dir = tmp_path / "plugin.video.test"
    addon_dir.mkdir()
    (addon_dir / "addon.xml").write_text(
        '<addon id="plugin.video.test" version="2.3.4" name="Test"/>',
        encoding="utf-8",
    )

    assert read_addon_meta(addon_dir) == ("plugin.video.test", "2.3.4")

    missing_dir = tmp_path / "missing"
    missing_dir.mkdir()
    with pytest.raises(FileNotFoundError):
        read_addon_meta(missing_dir)


def test_build_zip_structure_and_exclusions(tmp_path):
    addon_dir = tmp_path / "plugin.video.sample"
    (addon_dir / "resources" / "lib").mkdir(parents=True)
    (addon_dir / "__pycache__").mkdir()

    (addon_dir / "addon.xml").write_text(
        '<addon id="plugin.video.sample" version="1.2.3" name="Sample"/>',
        encoding="utf-8",
    )
    (addon_dir / "default.py").write_text("print('ok')\n", encoding="utf-8")
    (addon_dir / "resources" / "lib" / "helper.py").write_text("x = 1\n", encoding="utf-8")
    (addon_dir / "changelog.txt").write_text("1.2.3\n- initial\n", encoding="utf-8")
    (addon_dir / "__pycache__" / "default.cpython-312.pyc").write_bytes(b"pyc")
    (addon_dir / "stale.zip").write_bytes(b"zip")

    out_dir = tmp_path / "out"
    zip_path = build_zip(addon_dir, out_dir)

    assert zip_path == out_dir / "plugin.video.sample" / "plugin.video.sample-1.2.3.zip"
    assert zip_path.is_file()
    assert (out_dir / "plugin.video.sample" / "changelog.txt").is_file()

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()

    assert "plugin.video.sample/addon.xml" in names
    assert "plugin.video.sample/default.py" in names
    assert "plugin.video.sample/resources/lib/helper.py" in names
    assert all("\\" not in name for name in names)
    assert not any("__pycache__" in name or name.endswith(".zip") for name in names)


def test_find_addons_and_update_index(tmp_path):
    addon_a = tmp_path / "plugin.video.a"
    addon_b = tmp_path / "plugin.video.b"
    addon_a.mkdir()
    addon_b.mkdir()
    (tmp_path / "not_an_addon").mkdir()

    (addon_a / "addon.xml").write_text(
        '<addon id="plugin.video.a" version="1.0.1" name="A"/>',
        encoding="utf-8",
    )
    (addon_b / "addon.xml").write_text(
        '<addon id="plugin.video.b" version="2.0.0" name="B"/>',
        encoding="utf-8",
    )

    found = find_addons(tmp_path, filter_ids={"plugin.video.a"})
    assert found == [addon_a]

    addons_xml = tmp_path / "addons.xml"
    addons_xml.write_text(
        '<?xml version="1.0" encoding="utf-8"?>'
        '<addons><addon id="plugin.video.a" version="1.0.0" name="A"/></addons>',
        encoding="utf-8",
    )

    update_addons_index(
        addons_xml,
        updated=[("plugin.video.a", "1.0.1"), ("plugin.video.b", "2.0.0")],
        addon_dirs=[addon_a, addon_b],
    )

    root = ET.parse(addons_xml).getroot()
    versions = {el.get("id"): el.get("version") for el in root.findall("addon")}
    assert versions == {"plugin.video.a": "1.0.1", "plugin.video.b": "2.0.0"}

    md5_path = tmp_path / "addons.xml.md5"
    assert md5_path.read_text(encoding="utf-8") == hashlib.md5(addons_xml.read_bytes()).hexdigest()
