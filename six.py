"""Lightweight test stub of the ``six`` helper module.

The real project ships ``six`` via Kodi dependencies, but the unit test
environment in this repository does not automatically expose it.  The
stub below implements only the helpers referenced by the test suite and
Cumination sources so pytest can import the addon modules without pulling
network dependencies."""

from __future__ import absolute_import

import html.parser as _html_parser
import http.cookiejar as _http_cookiejar
import io
import sys
import types
import urllib.error as _urllib_error
import urllib.parse as _urllib_parse
import urllib.request as _urllib_request

PY2 = False
PY3 = True

string_types = (str,)
text_type = str

BytesIO = io.BytesIO
StringIO = io.StringIO


def b(value):
    """Return ``bytes`` for ASCII literals (parity with six.b)."""
    if isinstance(value, bytes):
        return value
    return value.encode("latin-1")


def ensure_binary(value, encoding="utf-8", errors="strict"):
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode(encoding, errors)
    return bytes(value)


def ensure_str(value, encoding="utf-8", errors="strict"):
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode(encoding, errors)
    return str(value)


def ensure_text(value, encoding="utf-8", errors="strict"):
    return ensure_str(value, encoding, errors)


def unichr(value):  # pragma: no cover - trivial wrapper
    return chr(value)


def print_(*args, **kwargs):  # pragma: no cover - convenience alias
    print(*args, **kwargs)


moves = types.ModuleType("six.moves")
moves.urllib_parse = _urllib_parse
moves.urllib_request = _urllib_request
moves.urllib_error = _urllib_error
moves.html_parser = _html_parser
moves.http_cookiejar = _http_cookiejar
moves.range = range
moves.cStringIO = io.StringIO

sys.modules.setdefault("six.moves", moves)
