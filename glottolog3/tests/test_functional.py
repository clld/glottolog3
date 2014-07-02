import datetime

from path import path

from clld.tests.util import TestWithApp

import glottolog3


class Tests(TestWithApp):
    __cfg__ = path(glottolog3.__file__).dirname().joinpath('..', 'development.ini').abspath()
    __setup_db__ = False

    def test_home(self):
        res = self.app.get('/')
        for name in 'glossary cite downloads errata contact'.split():
            res = self.app.get('/meta/' + name)
        for name in 'legal credits'.split():
            res = self.app.get('/' + name)

    def test_feeds(self):
        year = str(datetime.date.today().year)
        for feed in [
            '/langdoc.atom?cq=1&doctypes=grammar&year=' + year,
            '/glottolog/language.atom?type=languages',
            '/langdoc.atom?cq=1&doctypes=dictionary&year=' + year,
        ]:
            self.app.get_xml(feed)

    def test_languoids(self):
        res = self.app.get('/glottolog')
        res = self.app.get('/glottolog?alnum=stan1295', status=302)
        res = self.app.get('/glottolog?alnum=xxxx9999')
        assert 'No matching languoids' in res
        res = self.app.get('/glottolog?name=xxxx')
        assert 'No matching languoids' in res

    def test_languoidsfamily(self):
        res = self.app.get_dt('/glottolog/language?type=families')
        res = self.app.get('/glottolog/family')
        res = self.app.get('/glottolog/family.csv')

    def test_languoidslanguage(self):
        res = self.app.get_dt('/glottolog/language')
        res = self.app.get('/glottolog/language')
        res = self.app.get_json('/glottolog/language.geojson')
        res = self.app.get('/glottolog/language.csv')
        self.app.get_html(
            '/glottolog/language.map.html?type=languages&sEcho=1&sSearch_2=Atha')
        self.app.get_html(
            '/glottolog/language.map.html?country=PG')

    def test_languoidsmeta(self):
        res = self.app.get('/glottolog/glottologinformation')

    def test_langdoc(self):
        res = self.app.get_html('/langdoc')
        res = self.app.get('/langdoc.csv')
        res = self.app.get_dt('/langdoc')

    def test_langdocmeta(self):
        res = self.app.get('/langdoc/langdocinformation')

    def test_langdoccomplexquery(self):
        res = self.app.get('/langdoc/complexquery')
        res = self.app.get('/langdoc/complexquery?languoids=guac1239')
        res = self.app.get('/langdoc/complexquery?languoids=guac1239&format=xls', status=406)
        res = self.app.get('/langdoc/complexquery?languoids=guac1239&format=bib')
        res = self.app.get('/langdoc/complexquery?languoids=cher1273&macroareas=northamerica&doctypes=grammar&author=King')

    def test_childnodes(self):
        res = self.app.get('/db/getchildlects?q=ac')
        res = self.app.get('/db/getchildlects?node=1234')
        res = self.app.get('/db/getchildlects?t=select2&q=ac')

    def test_iso(self):
        res = self.app.get('/resource/languoid/iso/deu.rdf', status=302)
        res = self.app.get('/resource/languoid/iso/xxxx', status=404)

    def test_legacy(self):
        res = self.app.get('/resource/languoid/id/zulu1241', status=410)
        res = self.app.get('/resource/languoid/id/zzzz9999', status=404)

    def test_language(self):
        res = self.app.get('/resource/languoid/id/stan1295.rdf')
        res = self.app.get('/resource/languoid/id/stan1295')
        res = self.app.get('/resource/languoid/id/nilo1235')
        res = self.app.get('/resource/languoid/id/stan1295.bigmap.html')
        res = self.app.get('/resource/languoid/id/chil1280.newick.txt')
        res = self.app.get_xml('/resource/languoid/id/atha1245.phylo.xml')

    def test_ref(self):
        res = self.app.get('/resource/reference/id/2.rdf')
        res = self.app.get('/resource/reference/id/2')
        self.app.get_html('/resource/reference/id/40223')

    def test_desc_stats(self):
        self.app.get_html('/langdoc/status')
        self.app.get_html('/langdoc/status/browser?macroarea=Eurasia')
        self.app.get_html('/langdoc/status/languages-0-1?macroarea=Eurasia')
