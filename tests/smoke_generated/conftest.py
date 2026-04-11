
# Add to tests/conftest.py or create tests/smoke/conftest.py

import sys
from pathlib import Path
import json
import pytest

KODI_ARGV = ["plugin.video.cumination", "1", ""]
ROOT = Path(__file__).resolve().parents[2]


def _fallback_html():
    return """
    <html>
        <head>
            <title>Test Listing</title>
            <script>
                window.initials={"layoutPage":{"videoListProps":{"videoThumbProps":[{"title":"Test Video 1","pageURL":"https://xhamster.com/videos/test-video-1","thumbURL":"https://example.com/thumb-xhamster.jpg","duration":123,"isHD":true}]},"paginationProps":{"currentPageNumber":1,"lastPageNumber":2,"pageLinkTemplate":"https://xhamster.com/newest/{#}"}}};
            </script>
        </head>
        <body>
            <a class="th item" href="/videos/test-allclassic" title="Test AllClassic">
                <img src="/thumb-allclassic.jpg" data-src="/thumb-allclassic-lazy.jpg" alt="Test AllClassic">
                <span class="th-description">Test AllClassic Video</span>
                <span><i class="la-clock-o"></i>10:01</span>
            </a>

            <div class="list-videos">
                <div class="item">
                    <a class="popup-video-link" href="/videos/test-analdin" thumb="/thumb-analdin.jpg" title="Test Analdin Video">Test Analdin Video</a>
                    <div class="title">Test Analdin Video</div>
                    <img src="/thumb-analdin-fallback.jpg" data-original="/thumb-analdin.jpg">
                </div>
            </div>

            <div class="video-block">
                <a class="video-link" href="https://beemtube.com/videos/test-beemtube">
                    <img data-src="/thumb-beemtube.jpg" src="/thumb-beemtube-fallback.jpg" alt="Test BeemTube">
                    <strong>Test BeemTube Video</strong>
                </a>
                <div class="duration">06:16</div>
                <span class="hd_video"></span>
            </div>

            <article data-video-id="100" data-main-thumb="https://example.com/thumb-article-main.jpg">
                <a href="https://example.com/watch/test-article-video" title="Test Article Video">
                    <img src="https://example.com/thumb-article.jpg" data-src="https://example.com/thumb-article-lazy.jpg" alt="Test Article Video">
                </a>
                <div class="duration">04:44</div>
                <span class="hd-video">HD</span>
                <i class="fa-clock-o">04:44</i>
            </article>

            <div class="album" id="album-1">
                <img src="https://www.erome.com/thumb-erome.jpg" alt="Test Erome Album">
                <a class="album-title" href="https://www.erome.com/a/test-erome-album">Test Erome Album</a>
                <div class="album-images">12</div>
                <div class="album-videos">3</div>
            </div>

            <div class="media-group">
                <div class="video">
                    <video class="video-splash-mov" poster="https://www.erome.com/thumb-erome-video.jpg"></video>
                    <source src="https://cdn.erome.com/test-erome-video.mp4" label='720'>
                    <div class="duration">07:20</div>
                </div>
                <div class="clearfix"></div>
            </div>

            <div class="thumi">
                <a href="https://www.freeomovie.to/test-video" title="Test FreeOMovie">
                    <img src="/thumb-freeomovie.jpg" data-src="/thumb-freeomovie-lazy.jpg" alt="Test FreeOMovie">
                </a>
            </div>

            <div class="thumbs-inner">
                <a href="https://freshporno.org/test-freshporno" title="Test FreshPorno Video">
                    <img data-original="https://freshporno.org/thumb-freshporno.jpg" src="https://freshporno.org/thumb-freshporno-fallback.jpg" alt="Test FreshPorno Video">
                </a>
            </div>

            <li id="post-1">
                <a class="image" href="/video/123" alt="Test Porno365">
                    <img src="/thumb-porno365.jpg" alt="Test Porno365">
                    <span class="duration">09:59</span>
                </a>
            </li>

            <div class="item_cont">
                <a href="/videos/test-pornxp" class="item_link">
                    <img class="item_img" data-src="/thumb-pornxp.jpg" src="/thumb-pornxp-fallback.jpg" />
                    <div class="item_title">Test PornXP</div>
                    <div class="item_dur">08:00</div>
                </a>
            </div>

            <a class="item" href="https://www.heavy-r.com/videos/test-heavyr">
                <img src="/thumb-heavyr.jpg" data-src="/thumb-heavyr-lazy.jpg" />
                <div class="title">Test HeavyR Video</div>
            </a>

            <figure>
                <a class="img" href="https://jizzbunker.com/watch/test-jizzbunker">
                    <img data-original="/thumb-jizzbunker.jpg" src="/thumb-jizzbunker-fallback.jpg" />
                </a>
                <figcaption>
                    <a href="https://jizzbunker.com/watch/test-jizzbunker">Test Jizzbunker Video</a>
                </figcaption>
                <li class="dur"><time>05:55</time></li>
            </figure>

            <article class="post" data-post-id="1">
                <a href="https://premiumporn.org/test-video" title="Test PremiumPorn">
                    <img data-src="/thumb-premiumporn.jpg" src="/thumb-premiumporn-fallback.jpg" />
                    <div class="title">Test PremiumPorn</div>
                    <div class="duration">12:00</div>
                </a>
            </article>

            <div wire:key="video-test-1">
                <a href="/videos/test-hentaistream">
                    <img src="/gallery/test-hentaistream-0-thumbnail.jpg" alt="Test Hentaistream Video">
                    <p class="quality">1080p</p>
                </a>
            </div>

            <a class="clip-link" href="https://www.hitprn.com/test-hitprn" title="Test Hitprn Video">
                <img src="https://www.hitprn.com/thumb-hitprn.jpg" data-original="https://www.hitprn.com/thumb-hitprn-lazy.jpg">
            </a>

            <div class="video-thumb">
                <a class="frame video" href="/videos/test-youjizz">
                    <img class="lazy" data-original="//example.com/thumb-youjizz.jpg" src="//example.com/thumb-youjizz-fallback.jpg" alt="Test YouJizz Video">
                </a>
                <div class="video-title"><a href="/videos/test-youjizz">Test YouJizz Video</a></div>
                <div class="time">08:08</div>
            </div>

            <div class="v">
                <a href="https://xxdbx.com/video/test-xxdbx">
                    <img data-src="//example.com/thumb-xxdbx.jpg" src="//example.com/thumb-xxdbx-fallback.jpg">
                    <div class="v_title">Test xxdbx</div>
                    <div class="v_dur">07:07</div>
                </a>
            </div>

            <div class="item">
                <a href="https://www.wow.xxx/videos/test-longvideos" title="Test LongVideos">
                    <img src="https://example.com/thumb-longvideos.jpg">
                </a>
                <span class="duration">11:11</span>
                <div class="FHD"></div>
            </div>

            <div class="list-videos">
                <div class="item">
                    <a href="https://hornyfap.tv/video/test-hornyfap" title="Test HornyFap Video">
                        <strong class="title">Test HornyFap Video</strong>
                        <img class="thumb" src="/thumb-hornyfap.jpg" data-src="/thumb-hornyfap-lazy.jpg">
                        <div class="duration">03:33</div>
                    </a>
                </div>
            </div>

            <div class="video-item">
                <a href="/video/456" title="Test Generic Video">Test Generic Video
                    <img src="/thumb-generic.jpg" data-src="/thumb-generic-lazy.jpg" alt="Test Generic Video">
                </a>
            </div>

            <li class="pcVideoListItem js-pop videoBox">
                <a href="/view_video.php?viewkey=testpornhubkey" title="Test Pornhub Video">
                    <img data-thumb-url="https://ei.phncdn.com/thumbs/test-pornhub.jpg" src="https://ei.phncdn.com/thumbs/test-pornhub-fallback.jpg" alt="Test Pornhub Video">
                </a>
                <span class="title">Test Pornhub Video</span>
                <var class="duration">10:10</var>
            </li>

            <li class="thumbnail-card">
                <a class="video_link" href="/redtube/test-redtube">
                    <img data-src="https://ei.phncdn.com/thumbs/test-redtube.jpg" src="https://ei.phncdn.com/thumbs/test-redtube-fallback.jpg" alt="Test RedTube Video">
                </a>
                <a class="video-title-text" href="/redtube/test-redtube">Test RedTube Video</a>
                <div class="duration"><span>09:19</span></div>
            </li>

            <div class="video-box thumbnail-card">
                <a class="video-box-image" href="/watch/test-youporn">
                    <img class="thumb-image" src="//example.com/thumb-youporn.jpg" alt="Test YouPorn Video" />
                </a>
                <div class="video-title-text"><span>Test YouPorn Video</span></div>
                <div class="video-duration"><span>09:09</span></div>
            </div>

            <div class="well well-sm">
                <a class="video-link" href="/video/test-yrprno" title="Test YRPRNO Video">
                    <img data-original="https://example.com/thumb-yrprno.jpg" src="https://example.com/thumb-yrprno-fallback.jpg" alt="Test YRPRNO Video">
                </a>
                <div class="title-new">Test XFreeHD Video</div>
                <div class="duration">07:07</div>
                <div class="duration-new">07:07</div>
                <span class="badge">HD</span>
            </div>

            <div class="list-videos">
                <div class="item">
                    <a href="https://xmegadrive.com/videos/test-xmegadrive" title="Test XMegaDrive Video">
                        <strong class="title">Test XMegaDrive Video</strong>
                        <img data-original="https://example.com/thumb-xmegadrive.jpg" src="https://example.com/thumb-xmegadrive-fallback.jpg" alt="Test XMegaDrive Video">
                        <div class="duration">05:05</div>
                    </a>
                </div>
            </div>

            <a href="/page/2" class="next">Next</a>
            <a href="/page/2" rel="next">Next</a>
            <a class="prevnext" href="/page2.html">Next</a>
        </body>
    </html>
    """


def _fallback_json(url):
    if "search.htv-services.com" in url:
        return json.dumps({
            "hits": json.dumps([
                {
                    "name": "Test Hanime Video",
                    "is_censored": False,
                    "slug": "test-hanime-video",
                    "cover_url": "https://highwinds-cdn.com/test-hanime-cover.jpg",
                    "poster_url": "https://highwinds-cdn.com/test-hanime-poster.jpg",
                    "description": "<p>Test Hanime description</p>",
                    "tags": ["HD", "Vanilla"],
                }
            ])
        })
    if "externulls.com/facts/tag" in url:
        return json.dumps([
            {
                "fc_facts": [{"fc_thumbs": [1], "fc_start": None, "fc_end": None}],
                "tags": [{"is_owner": True, "tg_name": "TestTag", "tg_slug": "test-tag", "id": 1}],
                "file": {
                    "id": 999,
                    "fl_duration": 123,
                    "fl_height": 720,
                    "data": [
                        {"cd_column": "sf_name", "cd_value": "Test Beeg Video"},
                        {"cd_column": "sf_story", "cd_value": "Test story"},
                    ],
                },
            }
        ])
    if "posts/load_more_posts" in url:
        return json.dumps({
            "success": True,
            "content": '<section><a href="/video/test-porndig">Test Porndig Video</a><img src="/thumb-porndig.jpg"><div class="duration"><span>06:06</span></div></section>'
        })
    if "load_more_studios" in url or "load_more_pornstars" in url:
        return '<div id="_1"><img src="/thumb-porndig-studio.jpg" alt="Test Studio"><p>10 videos</p></div>'
    return None


def _archivebate_requests_stub():
    class _ArchivebateResponse:
        def __init__(self, text="", url="https://archivebate.com/", payload=None):
            self.text = text
            self.url = url
            self._payload = payload or {}

        def json(self):
            return self._payload

    class _ArchivebateSession:
        def __init__(self):
            self.headers = {}

        def get(self, url, timeout=None):
            text = (
                '<meta name="csrf-token" content="csrf-test">'
                ' <div wire:initial-data="{&quot;fingerprint&quot;:{&quot;name&quot;:&quot;videos&quot;},&quot;serverMemo&quot;:{}}" wire:init="loadVideos"></div>'
            )
            return _ArchivebateResponse(text=text, url=url)

        def post(self, url, json=None, headers=None, timeout=None):
            fragment = (
                '<section class="video_item">'
                '<a href="https://archivebate.com/watch/test-archivebate"></a>'
                '<video class="video-splash-mov" poster="https://archivebate.com/thumb-archivebate.jpg"></video>'
                '<a href="https://archivebate.com/profile/test-performer">Test Archivebate Performer</a>'
                '</section>'
            )
            return _ArchivebateResponse(payload={"effects": {"html": fragment}})

    return _ArchivebateSession


def _site_name_from_request(request):
    module_name = request.module.__name__.split(".")[-1]
    if module_name.startswith("test_smoke_"):
        return module_name[len("test_smoke_"):]
    return module_name


def _fixture_candidates(site_name):
    site_dir = ROOT / "tests" / "fixtures" / "sites" / site_name
    candidates = [
        site_dir / "listing.html",
        site_dir / "list.html",
        site_dir / "index.html",
        site_dir / "search.html",
        ROOT / "tests" / "fixtures" / f"{site_name}_list.html",
        ROOT / "tests" / "fixtures" / f"{site_name}_listing.html",
    ]
    return [path for path in candidates if path.exists()]


@pytest.fixture(autouse=True)
def _set_kodi_argv(monkeypatch):
    """Ensure addon imports see Kodi-style argv during smoke tests."""
    monkeypatch.setattr(sys, 'argv', KODI_ARGV.copy())


@pytest.fixture
def mock_gethtml(monkeypatch, request, _set_kodi_argv):
    """Mock getHtml to use a site fixture when available, else a broad fallback."""
    from resources.lib import utils
    site_name = _site_name_from_request(request)
    fixture_paths = _fixture_candidates(site_name)
    fallback_html = _fallback_html()

    def fake_gethtml(url, *args, **kwargs):
        json_payload = _fallback_json(url)
        if json_payload is not None:
            return json_payload
        for fixture_path in fixture_paths:
            return fixture_path.read_text(encoding="utf-8")
        return fallback_html

    monkeypatch.setattr(utils, 'getHtml', fake_gethtml)
    if hasattr(utils, '_getHtml'):
        monkeypatch.setattr(utils, '_getHtml', fake_gethtml)
    if hasattr(utils, 'postHtml'):
        monkeypatch.setattr(utils, 'postHtml', fake_gethtml)
    if hasattr(utils, '_postHtml'):
        monkeypatch.setattr(utils, '_postHtml', fake_gethtml)
    if site_name == "archivebate":
        import resources.lib.sites.archivebate as archivebate
        monkeypatch.setattr(archivebate.requests, "Session", _archivebate_requests_stub())
    return fake_gethtml
