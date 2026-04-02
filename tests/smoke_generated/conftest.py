
# Add to tests/conftest.py or create tests/smoke/conftest.py

import sys
import pytest

KODI_ARGV = ["plugin.video.cumination", "1", ""]


@pytest.fixture(autouse=True)
def _set_kodi_argv(monkeypatch):
    """Ensure addon imports see Kodi-style argv during smoke tests."""
    monkeypatch.setattr(sys, 'argv', KODI_ARGV.copy())


@pytest.fixture
def mock_gethtml(monkeypatch, _set_kodi_argv):
    """Mock getHtml to return minimal HTML instead of making real requests"""
    from resources.lib import utils

    def fake_gethtml(url, *args, **kwargs):
        # Return minimal valid HTML
        return """
        <html>
            <body>
                <div class="video-item">
                    <a href="/video/123" title="Test Video 1">
                        <img src="/thumb1.jpg" data-src="/thumb1-lazy.jpg" alt="Test Video 1">
                    </a>
                </div>
                <div class="video-item">
                    <a href="/video/456" title="Test Video 2">
                        <img src="/thumb2.jpg" alt="Test Video 2">
                    </a>
                </div>
                <a href="/page/2" class="next">Next</a>
            </body>
        </html>
        """

    monkeypatch.setattr(utils, 'getHtml', fake_gethtml)
    return fake_gethtml
