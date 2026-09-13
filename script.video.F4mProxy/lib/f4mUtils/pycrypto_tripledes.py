# Author: Trevor Perrin
# See the LICENSE file for legal information regarding use of this file.

"""PyCrypto 3DES implementation."""

from .cryptomath import *
from .tripledes import *

if pycryptoLoaded:
    def new(key, mode, IV):
        raise NotImplementedError("3DES is disabled because it is cryptographically weak")

    class PyCrypto_TripleDES(TripleDES):

        def __init__(self, key, mode, IV):
            raise NotImplementedError("3DES is disabled because it is cryptographically weak")

        def encrypt(self, plaintext):
            raise NotImplementedError("3DES is disabled because it is cryptographically weak")

        def decrypt(self, ciphertext):
            raise NotImplementedError("3DES is disabled because it is cryptographically weak")