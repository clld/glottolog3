import datetime

from path import path

from clld.tests.util import TestWithApp

import glottolog3


class Tests(TestWithApp):
    __cfg__ = path(glottolog3.__file__).dirname().joinpath('..', 'development.ini').abspath()
    __setup_db__ = False

    def test_home(self):
        self.app.get('/')
        for name in 'glossary cite downloads contact'.split():
            self.app.get('/meta/' + name)
        for name in 'legal about news'.split():
            self.app.get('/' + name)

    def test_feeds(self):
        year = str(datetime.date.today().year)
        for feed in [
            '/langdoc.atom?cq=1&doctypes=grammar&year=' + year,
            '/glottolog/language.atom?type=languages',
            '/langdoc.atom?cq=1&doctypes=dictionary&year=' + year,
        ]:
            self.app.get_xml(feed)

    def test_languoids(self):
        self.app.get('/glottolog')
        self.app.get('/glottolog?alnum=stan1295', status=302)
        res = self.app.get('/glottolog?alnum=xxxx9999')
        assert 'No matching languoids' in res
        res = self.app.get('/glottolog?name=xxxx')
        assert 'No matching languoids' in res
        res = self.app.get('/glottolog?iso=x')
        assert 'at least two characters' in res
        res = self.app.get('/glottolog?name=U')
        assert 'at least two characters' in res
        res = self.app.get('/glottolog?name=U&namequerytype=whole')
        assert 'at least two characters' not in res
        self.app.get('/glottolog?search=deu', status=302)
        self.app.get_html('/glottolog?search=')
        self.app.get_html('/glottolog?search=en')
        self.app.get_html('/glottolog?search=Deu')
        self.app.get_html('/glottolog?search=%20')
        self.app.get_html('/glottolog?search=abcdefg')
        self.app.get('/glottolog?search=stan1295', status=302)
        self.app.get('/glottolog?country=DE', status=302)
        self.app.get('/glottolog?country=DEG')

    def test_languoidsfamily(self):
        self.app.get_dt('/glottolog/language?type=families')
        self.app.get('/glottolog/family')
        self.app.get('/glottolog/family.csv')

    def test_languoidslanguage(self):
        self.app.get_dt('/glottolog/language')
        self.app.get('/glottolog/language')
        self.app.get_json('/glottolog/language.geojson')
        self.app.get('/glottolog/language.csv')
        self.app.get_html(
            '/glottolog/language.map.html?type=languages&sEcho=1&sSearch_2=Atha')
        self.app.get_html(
            '/glottolog/language.map.html?country=PG')

    def test_languoidsmeta(self):
        self.app.get('/glottolog/glottologinformation')

    def test_langdoc(self):
        self.app.get_html('/langdoc')
        self.app.get('/langdoc.csv')
        self.app.get_dt('/langdoc')

    def test_langdocmeta(self):
        self.app.get('/langdoc/langdocinformation')

    def test_langdoccomplexquery(self):
        self.app.get('/langdoc/complexquery')
        self.app.get('/langdoc/complexquery?languoids=guac1239')
        self.app.get('/langdoc/complexquery?languoids=guac1239&format=xls', status=406)
        self.app.get('/langdoc/complexquery?languoids=guac1239&format=bib')
        self.app.get('/langdoc/complexquery?languoids=cher1273&macroareas=northamerica&doctypes=grammar&author=King')

    def test_childnodes(self):
        self.app.get('/db/getchildlects?q=ac')
        self.app.get('/db/getchildlects?node=1234')
        self.app.get('/db/getchildlects?t=select2&q=ac')

    def test_iso(self):
        self.app.get('/resource/languoid/iso/deu.rdf', status=302)
        self.app.get('/resource/languoid/iso/xxxx', status=404)

    def test_legacy(self):
        self.app.get('/resource/languoid/id/zulu1241.xhtml', status=301)
        self.app.get('/resource/languoid/id/zzzz9999', status=404)
        self.app.get('/resource/languoid/id/zulu1241', status=410)
        self.app.get('/resource/reference/id/11.xhtml', status=301)
        self.app.get('/resource/reference/id/0', status=404)
        self.app.get('/resource/reference/id/11', status=410)
        self.app.get('/credits', status=301)

    def test_language(self):
        self.app.get_xml('/resource/languoid/id/stan1295.rdf')
        self.assertEquals(
            len(self.app.parsed_body.findall(
                './/{http://www.w3.org/2004/02/skos/core#}broader')),
            2)
        res = self.app.get_json('/resource/languoid/id/stan1295.json')
        self.assertIn('classification', res)
        self.app.get('/resource/languoid/id/stan1295')
        self.app.get('/resource/languoid/id/alba1269')
        self.app.get('/resource/languoid/id/nilo1235')
        self.app.get('/resource/languoid/id/stan1295.bigmap.html')
        self.app.get('/resource/languoid/id/chil1280.newick.txt')
        self.app.get_xml('/resource/languoid/id/atha1245.phylo.xml')

    def test_ref(self):
        self.app.get('/resource/reference/id/2.rdf')
        self.app.get('/resource/reference/id/2')
        self.app.get_html('/resource/reference/id/40223')

    def test_desc_stats(self):
        self.app.get_html('/langdoc/status')
        self.app.get_html('/langdoc/status/browser?macroarea=Eurasia')
        self.app.get_html('/langdoc/status/languages-0-1?macroarea=Eurasia')
