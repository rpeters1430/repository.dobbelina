import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESOLVEURL_PATH = ROOT / "script.module.resolveurl" / "lib"
if str(RESOLVEURL_PATH) not in sys.path:
    sys.path.append(str(RESOLVEURL_PATH))

import xbmc  # noqa: E402
import xbmcaddon  # noqa: E402
import xbmcgui  # noqa: E402


xbmc.executeJSONRPC = lambda *args, **kwargs: '{"result": {"version": {"major": 19}}}'
xbmc.getSupportedMedia = lambda *args, **kwargs: ".mp4|.m3u8"
xbmcaddon.Addon.openSettings = lambda self: None
xbmcgui.WindowXMLDialog = getattr(xbmcgui, "WindowXMLDialog", type("WindowXMLDialog", (), {}))
xbmcgui.WindowDialog = getattr(xbmcgui, "WindowDialog", type("WindowDialog", (), {}))

from resolveurl.plugins.doodstream import DoodStreamResolver  # noqa: E402


def test_nowplay_root_embed_matches_doodstream_resolver():
    resolver = DoodStreamResolver()

    match = re.search(resolver.pattern, "https://nowplay.to/embrikgfauqud4q")

    assert match
    assert match.groups() == ("nowplay.to", "embrikgfauqud4q")
