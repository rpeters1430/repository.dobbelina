"""
    urlresolver XBMC Addon
    Copyright (C) 2013 Bstrdsmkr

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Adapted for use in xbmc from:
    https://github.com/einars/js-beautify/blob/master/python/jsbeautifier/unpackers/packer.py

    usage:

    if detect(some_string):
        unpacked = unpack(some_string)


Unpacker for Dean Edward's p.a.c.k.e.r
"""

import re


def detect(source):
    """Detects whether `source` is P.A.C.K.E.R. coded."""
    source = source.replace(" ", "")
    if re.search(r"eval\(function\(p,a,c,k,e,(?:r|d)", source):
        return True
    else:
        return False


def unpack(source):
    """Unpacks P.A.C.K.E.R. packed js code."""
    payload, symtab, radix, count = _filterargs(source)

    if count != len(symtab):
        raise UnpackingError("Malformed p.a.c.k.e.r. symtab.")

    try:
        unbase = Unbaser(radix)
    except TypeError:
        raise UnpackingError("Unknown p.a.c.k.e.r. encoding.")

    def lookup(match):
        """Look up symbols in the synthetic symtab."""
        word = match.group(0)
        return symtab[unbase(word)] or word

    source = re.sub(r"\b\w+\b", lookup, payload)
    return _replacestrings(source)


def _filterargs(source):
    """Juice from a source file the four args needed by decoder."""
    argsregex = r"}\('(.*)', *(\d+), *(\d+), *'(.*?)'\.split\('\|'\)"
    args = re.search(argsregex, source, re.DOTALL).groups()

    try:
        return args[0], args[3].split("|"), int(args[1]), int(args[2])
    except ValueError:
        raise UnpackingError("Corrupted p.a.c.k.e.r. data.")


def _replacestrings(source):
    """Strip string lookup table (list) and replace values in source."""
    match = re.search(r'var *(_\w+)\=\["(.*?)"\];', source, re.DOTALL)

    if match:
        varname, strings = match.groups()
        startpoint = len(match.group(0))
        lookup = strings.split('","')
        variable = "%s[%%d]" % varname
        for index, value in enumerate(lookup):
            source = source.replace(variable % index, '"%s"' % value)
        return source[startpoint:]
    return source


class Unbaser(object):
    """Functor for a given base. Will efficiently convert
    strings to natural numbers."""

    ALPHABET = {
        62: "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        95: (
            " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            r"[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        ),
    }

    def __init__(self, base):
        self.base = base

        # If base can be handled by int() builtin, let it do it for us
        if 2 <= base <= 36:
            self.unbase = lambda string: int(string, base)
        else:
            if base < 62:
                self.ALPHABET[base] = self.ALPHABET[62][0:base]
            elif 62 < base < 95:
                self.ALPHABET[base] = self.ALPHABET[95][0:base]
            # Build conversion dictionary cache
            try:
                self.dictionary = dict(
                    (cipher, index) for index, cipher in enumerate(self.ALPHABET[base])
                )
            except KeyError:
                raise TypeError("Unsupported base encoding.")

            self.unbase = self._dictunbaser

    def __call__(self, string):
        return self.unbase(string)

    def _dictunbaser(self, string):
        """Decodes a  value to an integer."""
        ret = 0
        for index, cipher in enumerate(string[::-1]):
            ret += (self.base**index) * self.dictionary[cipher]
        return ret


class UnpackingError(Exception):
    """Badly packed source or general error. Argument is a
    meaningful description."""

    pass


if __name__ == "__main__":
    test = """eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('q.r(s(\'%h%t%a%p%u%6%c%n%0%5%l%4%2%4%7%j%0%8%1%o%b%3%7%m%1%8%a%7%b%3%d%6%1%f%0%v%1%5%D%9%0%5%c%g%0%4%A%9%0%f%k%z%2%8%1%C%2%i%d%6%2%3%k%j%2%3%y%e%x%w%g%B%E%F%i%h%e\'));',42,42,'5a|4d|4f|54|6a|44|33|6b|57|7a|56|4e|68|55|3e|47|69|65|6d|32|45|46|31|6f|30|75|document|write|unescape|6e|62|6c|2f|3c|22|79|63|66|78|59|72|61'.split('|'),0,{}))"""
    print((unpack(test)))
