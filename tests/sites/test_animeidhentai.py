import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugin.video.cumination"
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

if len(sys.argv) < 3 or not str(sys.argv[1]).isdigit():
    sys.argv = ["plugin.video.cumination", "1", ""]

MODULE_PATH = PLUGIN_ROOT / "resources" / "lib" / "sites" / "animeidhentai.py"
spec = importlib.util.spec_from_file_location("animeidhentai", MODULE_PATH)
animeidhentai = importlib.util.module_from_spec(spec)
if spec and spec.loader:
    spec.loader.exec_module(animeidhentai)
    sys.modules["animeidhentai"] = animeidhentai


FIXTURE_BASE = (
    Path(__file__).resolve().parents[1] / "fixtures" / "sites" / "animeidhentai"
)


def load_fixture(name: str) -> str:
    return (FIXTURE_BASE / name).read_text(encoding="utf-8")


def test_list_uses_beautifulsoup(monkeypatch):
    html = load_fixture("list.html")
    downloads = []
    dirs = []

    monkeypatch.setattr(animeidhentai.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(animeidhentai.utils, "eod", lambda: None)

    def record_download(name, url, mode, thumb, desc="", **kwargs):
        downloads.append(
            {
                "name": name,
                "url": url,
                "mode": mode,
                "thumb": thumb,
                "desc": desc,
                "quality": kwargs.get("quality"),
            }
        )

    monkeypatch.setattr(animeidhentai.site, "add_download_link", record_download)
    monkeypatch.setattr(animeidhentai.site, "add_dir", lambda *a, **k: dirs.append(a))

    animeidhentai.animeidhentai_list("https://animeidhentai.com/")

    assert [d["name"] for d in downloads] == [
        "Video One [COLOR hotpink][I]Uncensored[/I][/COLOR] [COLOR blue](2023)[/COLOR]",
        "Video Two [COLOR blue](2020)[/COLOR]",
    ]
    assert downloads[0]["quality"] == "HD"
    assert downloads[1]["quality"] == "FHD"
    assert downloads[0]["desc"].startswith("First plot")

    next_dirs = [entry for entry in dirs if entry[2] == "animeidhentai_list"]
    assert next_dirs and "Next Page" in next_dirs[0][0]


def test_genres_include_counts(monkeypatch):
    html = load_fixture("genres.html")
    dirs = []

    monkeypatch.setattr(animeidhentai.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(animeidhentai.utils, "eod", lambda: None)
    monkeypatch.setattr(animeidhentai.site, "add_dir", lambda *a, **k: dirs.append(a))

    animeidhentai.animeidhentai_genres("https://animeidhentai.com/genres/")

    labels = [entry[0] for entry in dirs]
    assert labels == [
        "Action [COLOR cyan]12 Videos[/COLOR]",
        "Romance [COLOR cyan]8 Videos[/COLOR]",
    ]


def test_years_uses_selector(monkeypatch):
    html = load_fixture("years.html")
    selected = {}
    called_urls = []

    monkeypatch.setattr(animeidhentai.utils, "getHtml", lambda *a, **k: html)

    def fake_selector(prompt, options, reverse=False):
        selected["prompt"] = prompt
        selected["options"] = options
        selected["reverse"] = reverse
        return "2022"

    monkeypatch.setattr(animeidhentai.utils, "selector", fake_selector)
    monkeypatch.setattr(
        animeidhentai, "animeidhentai_list", lambda url: called_urls.append(url)
    )

    animeidhentai.Years("https://animeidhentai.com/?s=")

    assert selected["reverse"] is True
    assert "2022" in selected["options"]
    assert called_urls == ["https://animeidhentai.com/year/2022/"]


def test_play_prefers_nhplayer_sources(monkeypatch):
    html_map = {
        "https://animeidhentai.com/watch/video": load_fixture("play_main.html"),
        "https://nhplayer.com/embed/abc123": load_fixture("play_nhplayer.html"),
        "https://nhplayer.com/videos/abc123.m3u8": load_fixture("play_source.html"),
    }

    captured = {}

    def fake_get_html(url, *args, **kwargs):
        return html_map[url]

    class DummyVP:
        def __init__(self, name, download=None):
            self.progress = type(
                "P",
                (),
                {
                    "update": lambda *a, **k: None,
                    "close": lambda *a, **k: captured.setdefault("closed", True),
                },
            )()
            self.direct_regex = None

        def __setattr__(self, name, value):
            if name == "direct_regex":
                captured["direct_regex"] = value
            super().__setattr__(name, value)

        def play_from_html(self, html):
            captured["html_played"] = html

        def play_from_link_to_resolve(self, url):
            captured["resolved_url"] = url

    monkeypatch.setattr(animeidhentai.utils, "VideoPlayer", DummyVP)
    monkeypatch.setattr(animeidhentai.utils, "getHtml", fake_get_html)
    monkeypatch.setattr(
        animeidhentai.utils,
        "notify",
        lambda *a, **k: captured.setdefault("notified", True),
    )

    animeidhentai.animeidhentai_play("https://animeidhentai.com/watch/video", "Sample")

    assert "video.m3u8" in captured.get("html_played", "")
    assert captured.get("direct_regex") == r'file:\s*"([^"]+)"'
    assert "resolved_url" not in captured
    assert captured.get("closed") is True
