import pytest


def test_detect_and_unpack_simple():
    from resources.lib import jsunpack

    packed = "eval(function(p,a,c,k,e,d){})"
    assert jsunpack.detect(packed) is True
    assert jsunpack.detect("plain text") is False

    source = "}('0 1',2,2,'foo|bar'.split('|'))"
    assert jsunpack.unpack(source) == "foo bar"


def test_unpack_errors_and_string_replacement():
    from resources.lib import jsunpack

    with pytest.raises(jsunpack.UnpackingError):
        jsunpack.unpack("}('0',2,3,'a|b'.split('|'))")

    replaced = jsunpack._replacestrings('var _x=["a","b"];_x[0]+_x[1]')
    assert replaced == '"a"+"b"'


def test_unbaser_variants():
    from resources.lib import jsunpack

    assert jsunpack.Unbaser(36)("10") == 36
    assert jsunpack.Unbaser(62)("a") == 10

    with pytest.raises(TypeError):
        jsunpack.Unbaser(120)
