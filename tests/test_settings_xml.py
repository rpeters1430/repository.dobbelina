import xml.etree.ElementTree as ET
from pathlib import Path


def test_cumination_settings_xml_uses_addon_settings_schema():
    settings_path = (
        Path(__file__).resolve().parents[1]
        / "plugin.video.cumination"
        / "resources"
        / "settings.xml"
    )

    root = ET.fromstring(settings_path.read_text())

    categories = root.findall("category")
    assert categories
    assert categories[0].attrib["label"] != "ResolveURL"

    settings = categories[0].findall("setting")
    assert any(setting.attrib.get("id") == "download_path" for setting in settings)

    all_settings = root.findall(".//setting")
    assert any(setting.attrib.get("id") == "open_smr_settings" for setting in all_settings)
    assert not any(
        "plugin://script.module.resolveurl/" in setting.attrib.get("action", "")
        for setting in all_settings
    )
