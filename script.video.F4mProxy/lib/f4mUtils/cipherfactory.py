# Author: Trevor Perrin
# See the LICENSE file for legal information regarding use of this file.

"""Factory functions for symmetric cryptography."""

from tlslite.utils import python_aes

from tlslite.utils import cryptomath

if cryptomath.m2cryptoLoaded:
    from tlslite.utils import openssl_aes

if cryptomath.pycryptoLoaded:
    from tlslite.utils import pycrypto_aes

# **************************************************************************
# Factory Functions for AES
# **************************************************************************

def createAES(key, IV, implList=None):
    """Create a new AES object.

    @type key: str
    @param key: A 16, 24, or 32 byte string.

    @type IV: str
    @param IV: A 16 byte string

    @rtype: L{tlslite.utils.AES}
    @return: An AES object.
    """
    if implList == None:
        implList = ["openssl", "pycrypto", "python"]

    for impl in implList:
        if impl == "openssl" and cryptomath.m2cryptoLoaded:
            return openssl_aes.new(key, 2, IV)
        elif impl == "pycrypto" and cryptomath.pycryptoLoaded:
            return pycrypto_aes.new(key, 2, IV)
        elif impl == "python":
            return python_aes.new(key, 2, IV)
    raise NotImplementedError()

def createRC4(key, IV, implList=None):
    """Create a new RC4 object.

    @type key: str
    @param key: A 16 to 32 byte string.

    @type IV: object
    @param IV: Ignored, whatever it is.

    @rtype: L{tlslite.utils.RC4}
    @return: An RC4 object.
    """
    raise NotImplementedError("RC4 is disabled because it is cryptographically weak")

#Create a new TripleDES instance
def createTripleDES(key, IV, implList=None):
    """Create a new 3DES object.

    @type key: str
    @param key: A 24 byte string.

    @type IV: str
    @param IV: An 8 byte string

    @rtype: L{tlslite.utils.TripleDES}
    @return: A 3DES object.
    """
    raise NotImplementedError("3DES is disabled because it is cryptographically weak")