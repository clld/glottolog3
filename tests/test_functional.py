from __future__ import unicode_literals
import datetime

from six import text_type

import pytest


@pytest.mark.parametrize('method, path, status, match', [
    ('get', '/', None, None),
    ('get', '/meta/glossary', None, None),
    ('get', '/meta/cite', None, None),
    ('get', '/meta/downloads', None, None),
    ('get', '/meta/contact', None, None),
    ('get', '/legal', None, None),
    ('get', '/about', None, None),
    ('get', '/news', None, None),
    ('get_html', '/parameters/aes', None, None),
    ('get_json', '/parameters/aes.geojson', None, None),
    ('get', '/langdoc/langdocinformation', None, None),
    ('get', '/glottolog', None, None),
    ('get', '/glottolog?alnum=stan1295', 302, None),
    ('get', '/glottolog?alnum=xxxx9999', None, 'No matching languoids'),
    ('get', '/glottolog?name=xxxx', None, 'No matching languoids'),
    ('get', '/glottolog?iso=x', None, 'at least two characters'),
    ('get', '/glottolog?name=U', None, 'at least two characters'),
    ('get', '/glottolog?search=deu', 302, None),
    ('get_html', '/glottolog?search=', None, None),
    ('get_html', '/glottolog?search=en', None, None),
    ('get_html', '/glottolog?search=Deu', None, None),
    ('get_html', '/glottolog?search=%20', None, None),
    ('get_html', '/glottolog?search=abcdefg', None, None),
    ('get', '/glottolog?search=stan1295', 302, None),
    ('get', '/glottolog?country=DE', 302, None),
    ('get', '/glottolog?country=DEG', None, None),
    ('get_dt', '/glottolog/language?type=families', None, None),
    ('get', '/glottolog/family', None, None),
    ('get', '/glottolog/family.csv', None, None),
    ('get_dt', '/glottolog/language', None, None),
    ('get', '/glottolog/language', None, None),
    ('get_json', '/glottolog/language.geojson', None, None),
    ('get', '/glottolog/language.csv', None, None),
    ('get_html', '/glottolog/language.map.html?type=languages&sEcho=1&sSearch_2=Atha', None, None),
    ('get_html', '/glottolog/language.map.html?country=PG', None, None),
    ('get', '/glottolog/glottologinformation', None, None),
    ('get_html', '/langdoc', None, None),
    ('get', '/langdoc.csv', None, None),
    ('get_dt', '/langdoc', None, None),
    ('get', '/langdoc/langdocinformation', None, None),
    ('get', '/langdoc/complexquery', None, None),
    ('get', '/langdoc/complexquery?languoids=guac1239', None, None),
    ('get', '/langdoc/complexquery?languoids=guac1239&format=xls', 406, None),
    ('get', '/langdoc/complexquery?languoids=guac1239&format=bib', None, None),
    ('get', '/langdoc/complexquery?languoids=cher1273&macroareas=northamerica&doctypes=grammar&author=King', None, None),
    ('get', '/db/getchildlects?q=ac', None, None),
    ('get', '/db/getchildlects?node=1234', None, None),
    ('get', '/db/getchildlects?t=select2&q=ac', None, None),
    ('get', '/resource/languoid/iso/deu.rdf', 302, None),
    ('get', '/resource/languoid/iso/xxxx', 404, None),
    ('get', '/resource/languoid/id/zulu1241.xhtml', 301, None),
    ('get', '/resource/languoid/id/zzzz9999', 404, None),
    ('get', '/resource/languoid/id/zulu1241', 410, None),
    ('get', '/resource/languoid/id/11.xhtml', 301, None),
    ('get', '/resource/languoid/id/0', 404, None),
    ('get', '/resource/languoid/id/174997', 404, None),
    ('get', '/credits', 301, None),
    ('get_xml', '/resource/languoid/id/stan1295.rdf', None, None),
    ('get_json', '/resource/languoid/id/stan1295.json', None, 'classification'),
    ('get', '/resource/languoid/id/afud1235', None, None),
    ('get', '/resource/languoid/id/stan1295', None, None),
    ('get', '/resource/languoid/id/alba1269', None, None),
    ('get', '/resource/languoid/id/nilo1235', 301, None),
    ('get', '/resource/languoid/id/stan1295.bigmap.html', None, None),
    ('get_xml', '/resource/languoid/id/atha1245.phylo.xml', None, None),
    ('get', '/resource/reference/id/2.rdf', None, None),
    ('get', '/resource/reference/id/2', None, None),
    ('get_html', '/resource/reference/id/40223', None, None),
    ('get', '/resource/reference/id/hh:h:Ethnologue:22', 301, None),
    ('get_html', '/langdoc/status', None, None),
    ('get_html', '/langdoc/status/browser?macroarea=Eurasia', None, None),
    ('get_html', '/langdoc/status/languages-1-3?macroarea=Eurasia&year=2018&family=', None, None),
])
def test_pages(app, method, path, status, match):
    kwargs = {'status': status} if status is not None else {'status': 200}
    res = getattr(app, method)(path, **kwargs)
    if match is not None:
        assert match in res


def test_body(app):
    assert '[atha1245]' in text_type(app.get('/resource/languoid/id/chil1280.newick.txt').body)


def test_name_characters(app):
    assert 'at least two characters' not in app.get_xml('/resource/languoid/id/stan1295.rdf')


@pytest.mark.parametrize('xpath', [
    './/{http://www.w3.org/2004/02/skos/core#}broaderTransitive',
    './/{http://www.w3.org/2004/02/skos/core#}broader',
])
def test_parsed_body(app, xpath):
    app.get_xml('/resource/languoid/id/stan1295.rdf')
    assert len(app.parsed_body.findall(xpath)) == 1


@pytest.mark.parametrize('feed', [
    '/langdoc.atom?cq=1&doctypes=grammar&year=',
    '/glottolog/language.atom?type=languages',
     '/langdoc.atom?cq=1&doctypes=dictionary&year=',
])
def test_feeds(app, feed):
    if feed.endswith('&year='):
        feed += str(datetime.date.today().year)
    app.get_xml(feed)
