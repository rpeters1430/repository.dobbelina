# Author: Trevor Perrin
# See the LICENSE file for legal information regarding use of this file.

"""PyCrypto RC4 implementation."""

from .cryptomath import *
from .rc4 import *

_RC4_DISABLED_MSG = "RC4 is disabled because it is cryptographically weak"

if pycryptoLoaded:
    def new(key):
        raise NotImplementedError(_RC4_DISABLED_MSG)

    class PyCrypto_RC4(RC4):

        def __init__(self, key):
            raise NotImplementedError(_RC4_DISABLED_MSG)

        def encrypt(self, plaintext):
            raise NotImplementedError(_RC4_DISABLED_MSG)

        def decrypt(self, ciphertext):
            raise NotImplementedError(_RC4_DISABLED_MSG)