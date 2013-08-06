from path import path

from clld.tests.util import TestWithApp

import glottolog3


class Tests(TestWithApp):
    __cfg__ = path(glottolog3.__file__).dirname().joinpath('..', 'development.ini').abspath()
    __setup_db__ = False

    def test_home(self):
        res = self.app.get('/', status=200)
        res = self.app.get('/', accept='text/html', status=200)
        for name in 'glossary cite downloads errata contact'.split():
            res = self.app.get('/meta/' + name, accept='text/html', status=200)
        for name in 'legal credits'.split():
            res = self.app.get('/' + name, accept='text/html', status=200)

    def test_languoids(self):
        res = self.app.get('/glottolog', status=200)
        res = self.app.get('/glottolog', accept='text/html', status=200)

    def test_languoidsfamily(self):
        res = self.app.get('/glottolog/family?sEcho=1', xhr=True, status=200)
        res = self.app.get('/glottolog/family', accept='text/html', status=200)

    def test_languoidslanguage(self):
        res = self.app.get('/glottolog/language?sEcho=1', xhr=True, status=200)
        res = self.app.get('/glottolog/language', accept='text/html', status=200)

    def test_languoidsmeta(self):
        res = self.app.get('/glottolog/glottologinformation', status=200)
        res = self.app.get('/glottolog/glottologinformation', accept='text/html', status=200)

    def test_langdoc(self):
        res = self.app.get('/langdoc', status=200)
        res = self.app.get('/langdoc', accept='text/html', status=200)

    def test_langdocmeta(self):
        res = self.app.get('/langdoc/langdocinformation', status=200)
        res = self.app.get('/langdoc/langdocinformation', accept='text/html', status=200)

    def test_langdoccomplexquery(self):
        res = self.app.get('/langdoc/complexquery', status=200)
        res = self.app.get('/langdoc/complexquery?languoids=guac1239', status=200)
        res = self.app.get('/langdoc/complexquery?languoids=guac1239&format=xls', status=406)
        res = self.app.get('/langdoc/complexquery?languoids=guac1239&format=bib', status=200)

    def test_childnodes(self):
        res = self.app.get('/db/getchildlects?q=ac', status=200)
        res = self.app.get('/db/getchildlects?node=1234', status=200)
        res = self.app.get('/db/getchildlects?t=select2&q=ac', status=200)

    def test_iso(self):
        res = self.app.get('/resource/languoid/iso/deu.rdf', status=302)
        res = self.app.get('/resource/languoid/iso/xxxx', status=404)

    def test_language(self):
        res = self.app.get('/resource/languoid/id/stan1295', accept='text/html', status=200)
        res = self.app.get('/resource/languoid/id/stan1295.bigmap.html', accept='text/html', status=200)
