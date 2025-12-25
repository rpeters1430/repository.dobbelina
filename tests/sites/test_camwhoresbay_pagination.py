from resources.lib.sites import camwhoresbay


def _sample_page(current_page="1", last_page="10"):
    return f"""
    <html>
    <body>
        <div class="video-item">
            <a href="/video/123" title="Sample Video">
                <img data-original="https://cdn.camwhoresbay.com/thumb.jpg" />
            </a>
            <span class="duration">08:00</span>
            <span class="hd">HD</span>
        </div>
        <div class="pagination">
            <span class="page-current"><span>{current_page}</span></span>
            <a class="next"><span data-block-id="list_videos" data-parameters="from_videos:{current_page.zfill(2)};sort_by:mr">Next</span></a>
            <span class="last">Last {last_page}</span>
        </div>
    </body>
    </html>
    """


def test_list_builds_async_next_page(monkeypatch):
    html = _sample_page(current_page="1", last_page="10")
    captured_downloads = []
    captured_dirs = []

    monkeypatch.setattr(
        camwhoresbay.utils, "getHtml", lambda url, ref=None, headers=None: html
    )
    monkeypatch.setattr(camwhoresbay.utils, "eod", lambda *args, **kwargs: None)
    monkeypatch.setattr(camwhoresbay.time, "time", lambda: 1234.0)

    def add_download(name, url, mode, iconimage, desc="", *args, **kwargs):
        captured_downloads.append(
            {
                "name": name,
                "url": url,
                "mode": camwhoresbay.site.get_full_mode(mode),
                "icon": iconimage,
                "duration": kwargs.get("duration"),
                "quality": kwargs.get("quality"),
            }
        )

    def add_dir(name, url, mode, *args, **kwargs):
        captured_dirs.append(
            {
                "name": name,
                "url": url,
                "mode": camwhoresbay.site.get_full_mode(mode),
                "context": kwargs.get("contextm"),
            }
        )

    monkeypatch.setattr(camwhoresbay.site, "add_download_link", add_download)
    monkeypatch.setattr(camwhoresbay.site, "add_dir", add_dir)

    camwhoresbay.List("https://www.camwhoresbay.com/latest-updates/", page=1)

    assert captured_downloads == [
        {
            "name": "Sample Video",
            "url": "https://www.camwhoresbay.com/video/123",
            "mode": "camwhoresbay.Playvid",
            "icon": "https://cdn.camwhoresbay.com/thumb.jpg",
            "duration": "08:00",
            "quality": "HD",
        }
    ]

    assert len(captured_dirs) == 1
    next_entry = captured_dirs[0]
    assert next_entry["name"].startswith("[COLOR hotpink]Next Page...[/COLOR] (2")
    assert "from_videos=2" in next_entry["url"]
    assert "_=1234000" in next_entry["url"]
    assert next_entry["mode"] == "camwhoresbay.List"
    assert next_entry["context"][0][0].startswith("[COLOR violet]Goto Page #")


def test_gotopage_updates_page_param(monkeypatch):
    commands = []
    import urllib.parse

    class DummyDialog:
        def numeric(self, *_args, **_kwargs):
            return "5"

    monkeypatch.setattr(camwhoresbay.xbmcgui, "Dialog", DummyDialog)
    monkeypatch.setattr(
        camwhoresbay.xbmc, "executebuiltin", lambda cmd: commands.append(cmd)
    )

    camwhoresbay.GotoPage(
        url="https://www.camwhoresbay.com/latest-updates/?mode=async&function=get_block&block_id=list_videos&from_videos=2&_=1234000",
        np="2",
        lp="10",
    )

    assert commands
    decoded = urllib.parse.unquote(commands[0])
    assert "from_videos=5" in decoded


def test_playvid_decodes_and_plays(monkeypatch):
    html = """
    <html><body>
    license_code: 'LIC123'
    video_url: 'ENC720' some text video_url_text: '720p'
    video_alt_url: 'ENC480' other text video_alt_url_text: '480p'
    </body></html>
    """
    played = {}

    class DummyVP:
        def __init__(self, name, download):
            self.name = name
            self.download = download
            self.progress = type("P", (), {"update": lambda *a, **k: None})

        def play_from_direct_link(self, url):
            played["url"] = url

    monkeypatch.setattr(
        camwhoresbay.utils, "getHtml", lambda url, ref=None, headers=None: html
    )
    monkeypatch.setattr(camwhoresbay.utils, "VideoPlayer", DummyVP)
    monkeypatch.setattr(
        camwhoresbay, "kvs_decode", lambda surl, lic: f"decoded:{surl}:{lic}"
    )

    def select(prompt, sources, **kwargs):
        # Should choose highest quality (720p) by default
        return sources["720p"]

    monkeypatch.setattr(camwhoresbay.utils, "selector", select)

    camwhoresbay.Playvid("https://www.camwhoresbay.com/video/123", "Sample Video")

    assert (
        played["url"]
        == "decoded:ENC720:LIC123|Referer=https://www.camwhoresbay.com/video/123"
    )
