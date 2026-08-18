"""
Unit tests for DNS-over-HTTPS (DoH) resolver module.
"""

from unittest.mock import MagicMock, patch
import json
from resources.lib import doh


def test_doh_resolve_cloudflare_success():
    doh.clear_doh_cache()
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({
        "Status": 0,
        "Answer": [
            {"name": "thothub.to", "type": 1, "TTL": 300, "data": "104.21.5.12"}
        ]
    }).encode("utf-8")

    with patch("six.moves.urllib_request.urlopen", return_value=mock_resp):
        ip = doh.resolve_doh("thothub.to", provider="cloudflare")
        assert ip == "104.21.5.12"

    # Test cache hit (should return cached IP without urlopen)
    with patch("six.moves.urllib_request.urlopen") as mock_open:
        cached_ip = doh.resolve_doh("thothub.to")
        assert cached_ip == "104.21.5.12"
        mock_open.assert_not_called()


def test_doh_resolve_empty_or_failed():
    doh.clear_doh_cache()
    assert doh.resolve_doh("") is None

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"Status": 3, "Answer": []}).encode("utf-8")

    with patch("six.moves.urllib_request.urlopen", return_value=mock_resp):
        ip = doh.resolve_doh("nonexistent-domain-xyz.com")
        assert ip is None


def test_doh_resolve_exception_handling():
    doh.clear_doh_cache()
    with patch("six.moves.urllib_request.urlopen", side_effect=Exception("Network down")):
        ip = doh.resolve_doh("thothub.to")
        assert ip is None
