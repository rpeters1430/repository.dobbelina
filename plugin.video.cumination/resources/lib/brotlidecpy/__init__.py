from __future__ import absolute_import

__version__ = "1.0.3"

__all__ = ['decompress']

# noinspection PyUnresolvedReferences
from .decode import brotli_decompress_buffer as decompress
