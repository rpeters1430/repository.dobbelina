import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESOLVER_PATH = (
    ROOT / "script.module.resolveurl.xxx" / "resources" / "plugins" / "pornhub.py"
)


def _load_resolver_module():
    common_module = types.ModuleType("resolveurl.common")
    common_module.RAND_UA = "TestUA"

    helpers_module = types.ModuleType("resolveurl.lib.helpers")
    helpers_module.sort_sources_list = lambda sources: sorted(
        sources,
        key=lambda item: int("".join(ch for ch in str(item[0]) if ch.isdigit()) or "0"),
    )
    helpers_module.pick_source = lambda sources: sources[-1][1]
    helpers_module.append_headers = lambda headers: "|" + "&".join(
        "{}={}".format(key, headers[key]) for key in sorted(headers)
    )

    resolver_module = types.ModuleType("resolveurl.resolver")

    class ResolveUrl(object):
        def _default_get_url(self, host, media_id, template):
            return template.format(host=host, media_id=media_id)

    class ResolverError(Exception):
        pass

    resolver_module.ResolveUrl = ResolveUrl
    resolver_module.ResolverError = ResolverError

    resolveurl_module = types.ModuleType("resolveurl")
    resolveurl_module.common = common_module

    lib_module = types.ModuleType("resolveurl.lib")
    lib_module.helpers = helpers_module

    sys.modules["resolveurl"] = resolveurl_module
    sys.modules["resolveurl.common"] = common_module
    sys.modules["resolveurl.lib"] = lib_module
    sys.modules["resolveurl.lib.helpers"] = helpers_module
    sys.modules["resolveurl.resolver"] = resolver_module

    spec = importlib.util.spec_from_file_location("test_pornhub_resolver_module", RESOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Response:
    def __init__(self, content):
        self.content = content


class _Net:
    def __init__(self, html):
        self.html = html
        self.calls = []

    def http_GET(self, url, headers=None):
        self.calls.append((url, headers or {}))
        return _Response(self.html)


def test_resolver_parses_multiline_media_definitions_and_sets_origin():
    module = _load_resolver_module()
    resolver = module.PornHubResolver()
    resolver.net = _Net(
        """
        <script>
        flashvars_123 = {
          "mediaDefinitions": [
            {"quality": "240", "videoUrl": "https://cdn.example.com/240.mp4"},
            {"quality": "720", "videoUrl": "https://cdn.example.com/720.mp4"}
          ]
        };
        </script>
        """
    )

    result = resolver.get_media_url("pornhub.com", "ph123")

    assert result == (
        "https://cdn.example.com/720.mp4"
        "|Cookie=accessAgeDisclaimerPH=1; accessAgeDisclaimerUK=1"
        "&Origin=https://www.pornhub.com"
        "&Referer=https://www.pornhub.com/"
        "&User-Agent=TestUA"
    )


def test_resolver_parses_multiline_quality_items():
    module = _load_resolver_module()
    resolver = module.PornHubResolver()
    resolver.net = _Net(
        """
        <script>
        var qualityItems_987 = [
          {"text": "480p", "url": "https://cdn.example.com/480.mp4"},
          {"text": "1080p", "url": "https://cdn.example.com/1080.mp4"}
        ];
        </script>
        """
    )

    result = resolver.get_media_url("pornhub.com", "ph456")

    assert result.startswith("https://cdn.example.com/1080.mp4|")
