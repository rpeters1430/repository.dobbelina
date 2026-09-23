import xml.etree.ElementTree as ET
import zipfile

from scripts.validate_addon_packages import validate_packages
from scripts.check_site_regressions import confirmed_regressions


def test_packaged_metadata_and_dependencies_match_index(tmp_path):
    packages = tmp_path / "packages"
    archive_dir = packages / "plugin.video.example"
    archive_dir.mkdir(parents=True)
    addon = '<addon id="plugin.video.example" version="1.2"><requires><import addon="xbmc.python"/></requires></addon>'
    index = tmp_path / "addons.xml"
    index.write_text(f"<addons>{addon}</addons>", encoding="utf-8")
    archive = archive_dir / "plugin.video.example-1.2.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("plugin.video.example/addon.xml", addon)
    assert validate_packages(packages, index) == []
    index.write_text('<addons><addon id="plugin.video.example" version="1.3"/></addons>')
    assert any("version differs" in error for error in validate_packages(packages, index))
    ET.parse(index)


def test_matching_strict_failures_are_confirmed():
    history = {"sites": {"broken": {"runs": [
        {"state": "BROKEN", "failure_signature": "same"},
        {"state": "BROKEN", "failure_signature": "same"}]},
        "flaky": {"runs": [{"state": "BROKEN", "failure_signature": "a"},
                           {"state": "BROKEN", "failure_signature": "b"}]}}}
    assert confirmed_regressions(history) == ["broken"]
