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
from resources.lib import utils
from unittest.mock import patch, MagicMock


def test_nowplay_root_embed_matches_doodstream_resolver():
    resolver = DoodStreamResolver()

    match = re.search(resolver.pattern, "https://nowplay.to/embrikgfauqud4q")

    assert match
    assert match.groups() == ("nowplay.to", "embrikgfauqud4q")


def test_solve_doodstream_nowplay():
    # Mock player instance
    player = utils.VideoPlayer("test video", None)
    
    # Mock getHtml response representing nowplay.to with packed jwplayer setup
    nowplay_html = """
    <html>
    <script type='text/javascript'>
    eval(function(p,a,c,k,e,d){while(c--)if(k[c])p=p.replace(new RegExp('\\\\b'+c.toString(a)+'\\\\b','g'),k[c]);return p}('jwplayer("vplayer").setup({sources:[{file:"https://cloud.nowplay.to/hls2/01/00000/irhfhr29bvz4_n/master.m3u8?t=token&s=123&e=3600"}],image:"https://thumb.nowplay.to/irhfhr29bvz4.jpg"});',36,36,'||||||||||||||||||||||||||||||||||||'.split('|')));
    </script>
    </html>
    """
    
    with (
        patch("resources.lib.utils.getHtml", return_value=nowplay_html) as mock_gethtml,
        patch("resources.lib.utils.get_cookies_string", return_value="foo=bar") as mock_cookies,
    ):
        result = player._solve_doodstream("https://nowplay.to/embirhfhr29bvz4")
        
        assert result is not None
        assert "https://cloud.nowplay.to/hls2/01/00000/irhfhr29bvz4_n/master.m3u8?t=token&s=123&e=3600" in result
        assert "Referer=https%3A//nowplay.to/embirhfhr29bvz4" in result
        assert "Cookie=foo%3Dbar" in result
        mock_gethtml.assert_called_once_with("https://nowplay.to/embirhfhr29bvz4")


def test_solve_doodstream_standard():
    player = utils.VideoPlayer("test video", None)
    
    # Mock DoodStream html with hotkeys
    dood_html = """
    <html>
    <script>
    dsplayer.hotkeys('/pass_md5/12345-token', 'my_token');
    function makePlay() { return 'dummy'; }
    </script>
    </html>
    """
    
    # Mock secondary pass_md5 response
    pass_md5_response = "https://cloud.dood.to/video/direct_link.mp4"
    
    def fake_get_html(url, referer=None, **kwargs):
        if "/pass_md5/" in url:
            return pass_md5_response
        return dood_html
        
    with (
        patch("resources.lib.utils.getHtml", side_effect=fake_get_html) as mock_gethtml,
        patch("resources.lib.utils.get_cookies_string", return_value="") as mock_cookies,
    ):
        result = player._solve_doodstream("https://dood.to/d/12345")
        
        assert result is not None
        # Should start with direct_link.mp4, followed by 10 random letters, then the token "my_token"
        assert "https://cloud.dood.to/video/direct_link.mp4" in result
        assert "my_token" in result
        assert "Referer=https%3A//dood.to/e/12345" in result
