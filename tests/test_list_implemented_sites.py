from pathlib import Path

import list_implemented_sites


def test_extract_site_handles_multiline_adultsite_with_url_constant(tmp_path: Path):
    site_file = tmp_path / "example.py"
    site_file.write_text(
        '''
from resources.lib.adultsite import AdultSite

bu = "https://example.test/"
site = AdultSite(
    "example",
    "[COLOR hotpink]Example Site[/COLOR]",
    bu,
    "example.png",
    category="Video Tubes",
)
''',
        encoding="utf-8",
    )

    assert list_implemented_sites.extract_site(site_file) == {
        "file": "example.py",
        "internal_name": "example",
        "name": "Example Site",
        "url": "https://example.test/",
        "category": "Video Tubes",
    }
