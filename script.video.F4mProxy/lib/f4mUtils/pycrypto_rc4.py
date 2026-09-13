# Author: Trevor Perrin
# See the LICENSE file for legal information regarding use of this file.

"""PyCrypto RC4 implementation."""

from .cryptomath import *
from .rc4 import *

if pycryptoLoaded:
    def new(key):
        raise NotImplementedError("RC4 is disabled because it is cryptographically weak")

    class PyCrypto_RC4(RC4):

        def __init__(self, key):
            raise NotImplementedError("RC4 is disabled because it is cryptographically weak")

        def encrypt(self, plaintext):
            raise NotImplementedError("RC4 is disabled because it is cryptographically weak")

        def decrypt(self, ciphertext):
            raise NotImplementedError("RC4 is disabled because it is cryptographically weak")