# Author: Trevor Perrin
# See the LICENSE file for legal information regarding use of this file.

"""PyCrypto 3DES implementation."""

from .cryptomath import *
from .tripledes import *

_TRIPLEDES_DISABLED_MSG = "3DES is disabled because it is cryptographically weak"

if pycryptoLoaded:
    def new(key, mode, IV):
        raise NotImplementedError(_TRIPLEDES_DISABLED_MSG)

    class PyCrypto_TripleDES(TripleDES):

        def __init__(self, key, mode, IV):
            raise NotImplementedError(_TRIPLEDES_DISABLED_MSG)

        def encrypt(self, plaintext):
            raise NotImplementedError(_TRIPLEDES_DISABLED_MSG)

        def decrypt(self, ciphertext):
            raise NotImplementedError(_TRIPLEDES_DISABLED_MSG)