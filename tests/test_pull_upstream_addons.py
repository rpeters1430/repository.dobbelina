#!/usr/bin/env python3
"""Tests for scripts/pull_upstream_addons.py."""

import io
import sys

from scripts.pull_upstream_addons import (
    UPSTREAM_REGISTRY,
    SyncDiff,
    apply_sync,
    compare_trees,
    compare_versions,
    get_local_addon_version,
    is_excluded,
    is_meaningful_change,
    is_preserved,
    main,
    resolve_addon_key,
    set_addon_xml_version,
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


def test_is_preserved():
    # Global settings patterns are preserved
    assert is_preserved("resources/settings.xml") is True
    assert is_preserved("settings.xml") is True
    assert is_preserved("advancedsettings.xml") is True
    assert is_preserved("resources/settings-new.xml") is True

    # Per-addon custom preserve patterns
    addon_preserve = ["*pornhub.py*", "*cipherfactory.py"]
    assert is_preserved("lib/resolvers/pornhub.py", addon_preserve) is True
    assert is_preserved("lib/cipherfactory.py", addon_preserve) is True

    # Standard addon code/metadata is NOT preserved (can be safely synced)
    assert is_preserved("addon.xml", addon_preserve) is False
    assert is_preserved("default.py", addon_preserve) is False
    assert is_preserved("lib/resolvers/spankbang.py", addon_preserve) is False


def test_compare_trees_and_apply_sync_preservation(tmp_path):
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()

    # Source has an updated code file
    (source_dir / "default.py").write_text("v2", encoding="utf-8")
    # Source does NOT have settings.xml (e.g. upstream ResolveURL has no settings.xml committed)

    # Dest has existing files: default.py, settings.xml, and a preserved patch file
    (dest_dir / "default.py").write_text("v1", encoding="utf-8")
    (dest_dir / "settings.xml").write_text("<settings>user config</settings>", encoding="utf-8")
    (dest_dir / "custom_patch.py").write_text("# local patch", encoding="utf-8")

    diff = compare_trees(
        source_dir,
        dest_dir,
        exclude_patterns=[],
        preserve_patterns=["custom_patch.py"],
    )

    # settings.xml and custom_patch.py should be marked as preserved, NOT removed
    assert "settings.xml" in diff.preserved
    assert "custom_patch.py" in diff.preserved
    assert "settings.xml" not in diff.removed
    assert "custom_patch.py" not in diff.removed
    assert "default.py" in diff.modified

    # Apply sync
    apply_sync(source_dir, dest_dir, diff, preserve_patterns=["custom_patch.py"], dry_run=False)

    # Preserved files remain untouched
    assert (dest_dir / "settings.xml").exists()
    assert (dest_dir / "settings.xml").read_text(encoding="utf-8") == "<settings>user config</settings>"
    assert (dest_dir / "custom_patch.py").exists()
    assert (dest_dir / "custom_patch.py").read_text(encoding="utf-8") == "# local patch"
    # Modified file was updated
    assert (dest_dir / "default.py").read_text(encoding="utf-8") == "v2"


def test_upstream_sync_keeps_custom_settings_and_resolver_but_removes_obsolete_code(tmp_path):
    upstream = tmp_path / "upstream"
    local = tmp_path / "local"
    for root in (upstream, local):
        (root / "lib" / "resolveurl" / "plugins").mkdir(parents=True)
        (root / "resources").mkdir()
    (upstream / "resources" / "settings.xml").write_text("<settings>upstream</settings>")
    (local / "resources" / "settings.xml").write_text("<settings>local</settings>")
    resolver = "lib/resolveurl/plugins/doodstream.py"
    (upstream / resolver).write_text("# upstream resolver")
    (local / resolver).write_text("# locally patched resolver")
    (upstream / "lib" / "current.py").write_text("new")
    (local / "lib" / "obsolete.py").write_text("old")

    diff = compare_trees(upstream, local, [], preserve_patterns=[resolver])
    assert "lib/obsolete.py" in diff.removed
    assert resolver in diff.preserved
    assert "resources/settings.xml" in diff.preserved
    apply_sync(upstream, local, diff, preserve_patterns=[resolver])
    assert (local / resolver).read_text() == "# locally patched resolver"
    assert (local / "resources" / "settings.xml").read_text() == "<settings>local</settings>"
    assert (local / "lib" / "current.py").read_text() == "new"
    assert not (local / "lib" / "obsolete.py").exists()


def test_compare_versions():
    assert compare_versions("1.0.0", "1.0.0") == 0
    assert compare_versions("5.1.210", "5.1.209") == 1
    assert compare_versions("5.1.209", "5.1.210") == -1
    assert compare_versions("2.1.45", "2.1.44") == 1
    assert compare_versions("2026.10.04-6", "2026.10.04-5") == 1
    assert compare_versions("unknown", "1.0.0") == -1
    assert compare_versions("1.0.0", "unknown") == 1


def test_set_addon_xml_version(tmp_path):
    addon_dir = tmp_path / "addon"
    addon_dir.mkdir()
    addon_xml = addon_dir / "addon.xml"
    addon_xml.write_text('<addon id="test.addon" version="1.0.0"/>\n', encoding="utf-8")

    res = set_addon_xml_version(addon_dir, "1.0.5")
    assert res == ("1.0.0", "1.0.5")
    assert '<addon id="test.addon" version="1.0.5"' in addon_xml.read_text(encoding="utf-8")

    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    assert set_addon_xml_version(empty_dir, "1.0.5") is None



def test_pull_addon_upstream_does_not_downgrade(tmp_path, monkeypatch):
    from scripts.pull_upstream_addons import check_addon_upstream, pull_addon_upstream

    # Setup upstream repo directory
    upstream_root = tmp_path / "upstream"
    upstream_root.mkdir()
    (upstream_root / "addon.xml").write_text('<addon id="test.addon" version="5.1.209"/>\n', encoding="utf-8")
    (upstream_root / "code.py").write_text("# upstream modified code\n", encoding="utf-8")

    # Setup local addon directory (local is ahead at 5.1.210)
    dest_path = tmp_path / "local"
    dest_path.mkdir()
    (dest_path / "addon.xml").write_text('<addon id="test.addon" version="5.1.210"/>\n', encoding="utf-8")
    (dest_path / "code.py").write_text("# old code\n", encoding="utf-8")
    (dest_path / "settings.xml").write_text("<settings>keep me</settings>\n", encoding="utf-8")

    spec = {
        "name": "Test Addon",
        "addon_id": "test.addon",
        "repo_url": "https://example.com/test.git",
        "default_branch": "master",
        "source_path": ".",
        "dest_path": dest_path,
        "type": "module",
        "exclude": [],
        "preserve": [],
    }

    monkeypatch.setattr(
        "scripts.pull_upstream_addons.fetch_upstream_repo",
        lambda repo_url, branch="master", target_temp_dir=None: (0, "commithash123", upstream_root),
    )

    # Status check should report LOCAL_AHEAD_WITH_DIFF
    status_res = check_addon_upstream("test_addon", spec)
    assert status_res["status"] == "LOCAL_AHEAD_WITH_DIFF"
    assert status_res["local_version"] == "5.1.210"
    assert status_res["remote_version"] == "5.1.209"

    # Pull with auto_bump=True should bump the local version (5.1.210 -> 5.1.211), not downgrade!
    pull_res = pull_addon_upstream("test_addon", spec, auto_bump=True, dry_run=False)
    assert pull_res["success"] is True
    assert pull_res["changes"] is True
    assert pull_res["version_before"] == "5.1.210"
    assert pull_res["version_after"] == "5.1.211"

    # Destination addon.xml must have 5.1.211
    dest_xml = (dest_path / "addon.xml").read_text(encoding="utf-8")
    assert 'version="5.1.211"' in dest_xml

    # Code should be updated from upstream
    assert (dest_path / "code.py").read_text(encoding="utf-8") == "# upstream modified code\n"

    # Preserved settings file must still exist and be intact
    assert (dest_path / "settings.xml").read_text(encoding="utf-8") == "<settings>keep me</settings>\n"


def test_is_meaningful_change():
    # Python code and translation files are meaningful
    assert is_meaningful_change("lib/resolveurl/plugins/flyfile.py") is True
    assert is_meaningful_change("extractor/shahid.py") is True
    assert is_meaningful_change("resources/language/resource.language.en_us/strings.po") is True

    # Metadata and images are NOT meaningful code changes
    assert is_meaningful_change("icon.png") is False
    assert is_meaningful_change("resources/images/DialogBack2.png") is False
    assert is_meaningful_change("fanart.jpg") is False
    assert is_meaningful_change("addon.xml") is False
    assert is_meaningful_change("changelog.txt") is False
    assert is_meaningful_change("README.md") is False

    # Preserved files are NOT treated as meaningful sync changes
    assert is_meaningful_change("resources/settings.xml") is False
    assert is_meaningful_change("lib/custom.py", preserve_patterns=["lib/custom.py"]) is False


