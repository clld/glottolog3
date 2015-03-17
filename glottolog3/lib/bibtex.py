# -*- coding: utf-8 -*-
import re

from six import PY3

from clld.lib.bibtex import u_unescape
from clld.lib import latex
latex.register()


if PY3:  # pragma: no cover
    unicode = str
    unichr = chr


# FIXME: resolve remaining code duplication with clld.lib.bibtex


RE_XML_ILLEGAL = re.compile(
    u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' +
    u'|' +
    u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' %
    (
        unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
        unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
        unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
    ))


def stripctrlchars(string):
    """remove unicode invalid characters

    >>> stripctrlchars(u'a\u0008\u000ba')
    u'aa'
    """
    try:
        return RE_XML_ILLEGAL.sub("", string)
    except TypeError:  # pragma: no cover
        return string


SYMBOLS = {
    r'\plusminus{}': u'\xb1',
    r'\middot{}': u'\xb7',
    r'\textopeno{}': u"\u0254",
    r'\dh{}': u"\u00f0",
    r'\DH{}': u"\u00d0",
    r'\textthorn{}': u"\u00fe",
    r'\textless{}': u"<",
    r'\textgreater{}': u">",
    r'\circ{}': u"\u00b0",
    r'\textltailn{}': u"\u0272",
    r'\textlambda{}': u"\u03BB",
    r'\textepsilon{}': u'\u025b',
    r'\textquestiondown{}': u'\xbf',
    r'\textschwa{}': u'\u0259',
    r'\textsubdot{o}': u'\u1ecd',
    r'\textrhooktopd{}': u'\u0257',
    #r'\eurosign{}': u'\u20ac',
    r'\eurosign{}': u'\u2021',
    r'\textquestiondown': u'\xbf',
    r'\textquotedblleft': u'\u201c',
    r'\textquotedblright': u'\u201d',
    r'\textquoteleft': u'\u2018',
    r'\textquoteright': u'\u2019',

    r'\textsubdot{D}': u'\u1e0c',
    r'\textsubdot{E}': u'\u1eb8',
    r'\textsubdot{H}': u'\u1e24',
    r'\textsubdot{I}': u'\u1eca',
    r'\textsubdot{O}': u'\u1ecc',
    r'\textsubdot{T}': u'\u1e6c',
    r'\textsubdot{d}': u'\u1e0d',
    r'\textsubdot{b}': u'\u1e05',
    r'\textsubdot{e}': u'\u1eb9',
    r'\textsubdot{h}': u'\u1e25',
    r'\textsubdot{i}': u'\u1ecb',
    r'\textsubdot{n}': u'\u1e47',
    r'\textsubdot{r}': u'\u1e5b',
    r'\textsubdot{s}': u'\u1e63',
    r'\textsubdot{t}': u'\u1e6d',
    r'\ng{}': u'\u014b',
    r'\oslash{}': u'\u00f8',
    r'\Oslash{}': u'\u00d8',
    r'\textdoublebarpipe{}': u'\u01c2',
    #r'\dots': '',
    r'\Aa{}': u'\xc5',
    u'\\Aa{}Rsj\xd6': u'\xc5rsj\xf6',

    r'\guillemotleft': u'\xab',
    r'\guillemotleft{}': u'\xab',
    r'\guillemotright': u'\xbb',
}

"""
latlig["textsuperscript{h}"] = "#x2b0"
latlig["textsuperscript{j}"] = "#x2b2"
latlig["textsuperscript{w}"] = "#x2b7"
latlig['textlambda'] = "lambda"
latlig['texthtd'] = "#599"
latlig['texthtb'] = "#595"
latlig['textrhooktopb'] = "#595"
latlig['texthtd'] = "#599"
latlig['texthtb'] = "#595"
latlig['textbari'] = "#616"
latlig['textbaru'] = "#649"
latlig['textbarI'] = "#407"
latlig['textbarU'] = "#580"
latlig['textupsilon'] = "#965"
latlig['textschwa'] = '#601'
latlig['textgamma'] = '#611'
latlig['textesh'] = '#154'
latlig['texteta'] = '#951'
latlig['texttheta'] = '#952'
latlig['textbeta'] = '#946'
latlig['textdoublebarpipevar'] = "#x01c2"
latlig['texteng'] = '#x014a'
latlig['texteuro'] = '#x20ac'
latlig['textglotstop'] = "#660"
latlig['textvertline'] = "#124"
latlig['textdoublevertline'] = "#2016"
latlig['textraiseglotstop'] = "#x02c0"
latlig['DH'] = "ETH"
latlig['dh'] = "eth"
latlig['textturna'] = "#x250"
latlig['textscriptv'] = "#x28b"
latlig['textrtaild'] = "#x256"
latlig['textltailn'] = "#x272"
latlig['textsubrhalfring'] = "#x339"
latlig['textsci'] = "#x26a"
latlig['textphi'] = "#x278"
latlig['textscu'] = "#x28a" #textupsilon
latlig['L'] = "#321"
latlig['l'] = "#322"
latlig['textchi'] = "#967"
latlig['ldots'] = 'hellip'
latlig['textrevepsilon'] = "#604"
latlig['textrtails'] = "#537"
latlig['textrtailr'] = "#637"
latlig['Ohorn'] = "#416"
latlig['ohorn'] = "#417"
latlig['texthardsign'] = "#1098"
latlig['textquestiondown'] = "iquest"
latlig['textturnv'] = "#652"
latlig['textquotedblleft'] = "ldquo"
latlig['textquotedblright'] = "rdquo"
latlig['guillemotleft'] = "laquo"
latlig['guillemotright'] = "raquo"
latlig['textemdash'] = "mdash"
latlig['textemdash'] = "ndash"

"""


def unescape(string):
    """transform latex escape sequences of type \`\ae  into unicode
    """
    def _delatex(s):
        try:
            t = str(s)
            result = t.decode('latex+latin1')
        except UnicodeEncodeError:  # pragma: no cover
            result = string
        u_result = unicode(result)
        return u_result

    res = u_unescape(_delatex(stripctrlchars(unicode(string).strip())))
    for symbol in sorted(SYMBOLS.keys(), key=lambda s: len(s)):
        res = res.replace(symbol, SYMBOLS[symbol])
    if '\\' not in res:
        res = res.replace('{', '')
        res = res.replace('}', '')
    res = res.replace('\\\\&{} ', '& ')
    return res
