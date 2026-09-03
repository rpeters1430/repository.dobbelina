#!/usr/bin/env python3
"""Tests for scripts/pull_upstream_addons.py."""

import io
import sys

from scripts.pull_upstream_addons import (
    UPSTREAM_REGISTRY,
    SyncDiff,
    apply_sync,
    compare_trees,
    get_local_addon_version,
    is_excluded,
    main,
    resolve_addon_key,
)


def test_upstream_registry_structure():
    assert "resolveurl" in UPSTREAM_REGISTRY
    assert "resolveurlxxx" in UPSTREAM_REGISTRY
    assert "yt-dlp" in UPSTREAM_REGISTRY
    assert "f4mproxy" in UPSTREAM_REGISTRY

    required_keys = {"name", "addon_id", "repo_url", "default_branch", "source_path", "dest_path", "type", "exclude"}
    for key, spec in UPSTREAM_REGISTRY.items():
        assert required_keys.issubset(spec.keys()), f"Missing keys in {key}"
        assert spec["repo_url"].startswith("http")
        assert len(spec["exclude"]) > 0


def test_resolve_addon_key():
    assert resolve_addon_key("resolveurl") == "resolveurl"
    assert resolve_addon_key("RESOLVEURL") == "resolveurl"
    assert resolve_addon_key("resolveurlxxx") == "resolveurlxxx"
    assert resolve_addon_key("resolveurl.xxx") == "resolveurlxxx"
    assert resolve_addon_key("script.module.resolveurl") == "resolveurl"
    assert resolve_addon_key("script.module.resolveurl.xxx") == "resolveurlxxx"
    assert resolve_addon_key("ytdlp") == "yt-dlp"
    assert resolve_addon_key("script.module.yt-dlp") == "yt-dlp"
    assert resolve_addon_key("smr") == "smr_link_tester"
    assert resolve_addon_key("nonexistent_addon") == "nonexistent_addon"


def test_is_excluded():
    exclude = [".git*", "*.pyc", "__pycache__", "*.zip"]
    assert is_excluded(".git", exclude) is True
    assert is_excluded(".gitignore", exclude) is True
    assert is_excluded("test.pyc", exclude) is True
    assert is_excluded("module/__pycache__/cache.pyc", exclude) is True
    assert is_excluded("addon-1.0.0.zip", exclude) is True
    assert is_excluded("addon.xml", exclude) is False
    assert is_excluded("lib/default.py", exclude) is False


def test_get_local_addon_version(tmp_path):
    # Nonexistent path
    assert get_local_addon_version(tmp_path / "nonexistent") == "unknown"

    # Valid addon.xml
    addon_xml = tmp_path / "addon.xml"
    addon_xml.write_text('<addon id="test.addon" version="1.2.3"/>', encoding="utf-8")
    assert get_local_addon_version(tmp_path) == "1.2.3"
    assert get_local_addon_version(addon_xml) == "1.2.3"


def test_compare_trees_and_apply_sync(tmp_path):
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()

    # Setup source files
    (source_dir / "common.txt").write_text("v1", encoding="utf-8")
    (source_dir / "added.txt").write_text("new file", encoding="utf-8")
    (source_dir / "modified.txt").write_text("v2", encoding="utf-8")
    (source_dir / "ignored.pyc").write_text("bytecode", encoding="utf-8")

    # Setup dest files
    (dest_dir / "common.txt").write_text("v1", encoding="utf-8")
    (dest_dir / "modified.txt").write_text("v1", encoding="utf-8")
    (dest_dir / "removed.txt").write_text("old file", encoding="utf-8")

    exclude = ["*.pyc"]
    diff = compare_trees(source_dir, dest_dir, exclude)

    assert diff.has_changes is True
    assert diff.added == ["added.txt"]
    assert diff.modified == ["modified.txt"]
    assert diff.removed == ["removed.txt"]
    assert diff.unchanged == ["common.txt"]
    assert "ignored.pyc" not in diff.added

    # Dry-run apply sync does not change dest_dir
    apply_sync(source_dir, dest_dir, diff, dry_run=True)
    assert not (dest_dir / "added.txt").exists()
    assert (dest_dir / "removed.txt").exists()
    assert (dest_dir / "modified.txt").read_text(encoding="utf-8") == "v1"

    # Actual apply sync
    apply_sync(source_dir, dest_dir, diff, dry_run=False)
    assert (dest_dir / "added.txt").exists()
    assert (dest_dir / "added.txt").read_text(encoding="utf-8") == "new file"
    assert not (dest_dir / "removed.txt").exists()
    assert (dest_dir / "modified.txt").read_text(encoding="utf-8") == "v2"
    assert (dest_dir / "common.txt").read_text(encoding="utf-8") == "v1"

    # Second compare should have no changes
    diff2 = compare_trees(source_dir, dest_dir, exclude)
    assert diff2.has_changes is False
    assert diff2.added == []
    assert diff2.modified == []
    assert diff2.removed == []


def test_main_does_not_crash_on_non_utf8_console(monkeypatch):
    """Windows consoles without UTF-8 configured default stdout to cp1252,
    which raised UnicodeEncodeError on the emoji status markers (checked
    live: `python pull_upstream_addons.py --dry-run --addon resolveurl`
    crashed with `UnicodeEncodeError: 'charmap' codec can't encode
    character '\U0001f504'`). main() must reconfigure stdout to UTF-8
    before printing any of those markers.
    """
    changes_diff = SyncDiff(added=["new.py"], modified=["existing.py"], removed=[])
    up_to_date_diff = SyncDiff()

    def fake_pull(addon_key, spec, branch=None, dry_run=False, **kwargs):
        if addon_key == "yt-dlp":
            return {
                "addon_key": addon_key,
                "name": spec.get("name", addon_key),
                "success": False,
                "message": "simulated clone failure",
            }
        if addon_key == "f4mproxy":
            return {
                "addon_key": addon_key,
                "name": spec.get("name", addon_key),
                "success": True,
                "changes": False,
                "local_version": "1.0.0",
                "remote_version": "1.0.0",
                "head_commit": "abcdef12",
                "diff": up_to_date_diff,
                "dry_run": dry_run,
            }
        return {
            "addon_key": addon_key,
            "name": spec.get("name", addon_key),
            "success": True,
            "changes": True,
            "version_before": "1.0.0",
            "version_after": "1.0.1",
            "head_commit": "abcdef12",
            "diff": changes_diff,
            "dry_run": dry_run,
        }

    monkeypatch.setattr("scripts.pull_upstream_addons.pull_addon_upstream", fake_pull)

    # Simulate a Windows console with no UTF-8 configured: encoding raw
    # bytes through cp1252 with strict errors is exactly what raised
    # UnicodeEncodeError before the fix.
    raw = io.BytesIO()
    cp1252_stdout = io.TextIOWrapper(raw, encoding="cp1252", errors="strict")
    monkeypatch.setattr(sys, "stdout", cp1252_stdout)
    monkeypatch.setattr(
        sys, "argv", ["pull_upstream_addons.py", "--addon", "resolveurl,f4mproxy,yt-dlp", "--dry-run"]
    )

    try:
        exit_code = main()
    finally:
        cp1252_stdout.flush()
        output = raw.getvalue().decode("utf-8", errors="strict")

    assert exit_code == 0
    assert "Changes detected" in output
    assert "Already up to date" in output
    assert "Error syncing" in output


def test_bump_version_string():
    from scripts.pull_upstream_addons import bump_version_string

    assert bump_version_string("1.1.470") == "1.1.471"
    assert bump_version_string("2026.10.04-2") == "2026.10.04-3"
    assert bump_version_string("1.0.6") == "1.0.7"
    assert bump_version_string("2.0.01") == "2.0.02"
    assert bump_version_string("5.1.209") == "5.1.210"
    assert bump_version_string("release") == "release.1"


def test_bump_addon_xml_version(tmp_path):
    from scripts.pull_upstream_addons import bump_addon_xml_version

    addon_xml = tmp_path / "addon.xml"
    addon_xml.write_text('<addon id="test.addon" version="1.0.0"/>\n', encoding="utf-8")

    res = bump_addon_xml_version(tmp_path)
    assert res == ("1.0.0", "1.0.1")
    assert '<addon id="test.addon" version="1.0.1"' in addon_xml.read_text(encoding="utf-8")
