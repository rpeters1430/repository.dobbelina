import pytest


def test_pkcs7_encode_adds_padding():
    from resources.lib.jscrypto.pkcs7 import PKCS7Encoder

    encoder = PKCS7Encoder(k=8)
    padded = encoder.encode(b"abcd")

    assert isinstance(padded, bytes)
    assert padded.startswith(b"abcd")
    assert len(padded) == 8


def test_pkcs7_decode_strips_padding_for_text():
    from resources.lib.jscrypto.pkcs7 import PKCS7Encoder

    encoder = PKCS7Encoder(k=8)
    text = "abcd" + "\x04" * 4
    assert encoder.decode(text) == "abcd"


def test_pkcs7_decode_rejects_invalid_padding():
    from resources.lib.jscrypto.pkcs7 import PKCS7Encoder

    encoder = PKCS7Encoder(k=4)
    with pytest.raises(ValueError):
        encoder.decode("abc" + "\x05")
