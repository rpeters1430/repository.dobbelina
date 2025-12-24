# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/xhamster.py

import base64
import codecs
import itertools
import string
from resources.lib import utils


def to_signed_32(n):
    return n % ((-1 if n < 0 else 1) * 2**32)


class _ByteGenerator:
    def __init__(self, algo_id, seed):
        try:
            self._algorithm = getattr(self, f"_algo{algo_id}")
        except AttributeError:
            raise ValueError(f"Unknown algorithm ID: {algo_id}")
        self._s = to_signed_32(seed)

    def _algo1(self, s):
        # LCG (a=1664525, c=1013904223, m=2^32)
        # Ref: https://en.wikipedia.org/wiki/Linear_congruential_generator
        s = self._s = to_signed_32(s * 1664525 + 1013904223)
        return s

    def _algo2(self, s):
        # xorshift32
        # Ref: https://en.wikipedia.org/wiki/Xorshift
        s = to_signed_32(s ^ (s << 13))
        s = to_signed_32(s ^ ((s & 0xFFFFFFFF) >> 17))
        s = self._s = to_signed_32(s ^ (s << 5))
        return s

    def _algo3(self, s):
        # Ref: https://en.wikipedia.org/wiki/Weyl_sequence
        # https://commons.apache.org/proper/commons-codec/jacoco/org.apache.commons.codec.digest/MurmurHash3.java.html
        s = self._s = to_signed_32(s + 0x9E3779B9)
        s = to_signed_32(s ^ ((s & 0xFFFFFFFF) >> 16))
        s = to_signed_32(s * to_signed_32(0x85EBCA77))
        s = to_signed_32(s ^ ((s & 0xFFFFFFFF) >> 13))
        s = to_signed_32(s * to_signed_32(0xC2B2AE3D))
        return to_signed_32(s ^ ((s & 0xFFFFFFFF) >> 16))

    def _algo4(self, s):
        # Custom scrambling function involving a left rotation (ROL)
        s = self._s = to_signed_32(s + 0x6D2B79F5)
        s = to_signed_32((s << 7) | ((s & 0xFFFFFFFF) >> 25))  # ROL 7
        s = to_signed_32(s + 0x9E3779B9)
        s = to_signed_32(s ^ ((s & 0xFFFFFFFF) >> 11))
        s = to_signed_32(s * 0x27D4EB2D)
        return s

    def _algo5(self, s):
        # xorshift variant with a final addition
        s = to_signed_32(s ^ (s << 7))
        s = to_signed_32(s ^ ((s & 0xFFFFFFFF) >> 9))
        s = to_signed_32(s ^ (s << 8))
        s = self._s = to_signed_32(s + 0xA5A5A5A5)
        return s

    def _algo6(self, s):
        # LCG (a=0x2c9277b5, c=0xac564b05) with a variable right shift scrambler
        s = self._s = to_signed_32(
            s * to_signed_32(0x2C9277B5) + to_signed_32(0xAC564B05)
        )
        s2 = to_signed_32(s ^ ((s & 0xFFFFFFFF) >> 18))
        shift = (s & 0xFFFFFFFF) >> 27 & 31
        return to_signed_32((s2 & 0xFFFFFFFF) >> shift)

    def _algo7(self, s):
        # Weyl Sequence (k=0x9e3779b9) + custom multiply-xor-shift mixing function
        s = self._s = to_signed_32(s + to_signed_32(0x9E3779B9))
        e = to_signed_32(s ^ (s << 5))
        e = to_signed_32(e * to_signed_32(0x7FEB352D))
        e = to_signed_32(e ^ ((e & 0xFFFFFFFF) >> 15))
        e = to_signed_32(e * to_signed_32(0x846CA68B))
        return e

    def __next__(self):
        return self._algorithm(self._s) & 0xFF


def try_call(*funcs, expected_type=None, args=[], kwargs={}):
    for f in funcs:
        try:
            val = f(*args, **kwargs)
        except (
            AttributeError,
            KeyError,
            TypeError,
            IndexError,
            ValueError,
            ZeroDivisionError,
        ):
            pass
        else:
            if expected_type is None or isinstance(val, expected_type):
                return val


_XOR_KEY = b"xh7999"


def deobfuscate_url(format_url):
    if all(char in string.hexdigits for char in format_url):
        byte_data = bytes.fromhex(format_url)
        seed = int.from_bytes(byte_data[1:5], byteorder="little", signed=True)
        byte_gen = _ByteGenerator(byte_data[0], seed)
        return bytearray(byte ^ next(byte_gen) for byte in byte_data[5:]).decode(
            "latin-1"
        )

    cipher_type, _, ciphertext = (
        try_call(lambda: base64.b64decode(format_url).decode().partition("_"))
        or [None] * 3
    )

    if not cipher_type or not ciphertext:
        utils.kodilog("Failed to decipher URL")
        return None

    if cipher_type == "xor":
        return bytes(
            a ^ b for a, b in zip(ciphertext.encode(), itertools.cycle(_XOR_KEY))
        ).decode()

    if cipher_type == "rot13":
        return codecs.decode(ciphertext, cipher_type)

    utils.kodilog(f'Unsupported cipher type "{cipher_type}"')
    return None
