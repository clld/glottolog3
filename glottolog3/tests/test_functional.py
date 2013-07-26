from path import path

from clld.tests.util import TestWithApp

import glottolog3


class Tests(TestWithApp):
    __cfg__ = path(glottolog3.__file__).dirname().joinpath('..', 'development.ini').abspath()
    __setup_db__ = False

    def test_home(self):
        res = self.app.get('/', status=200)
        res = self.app.get('/', accept='text/html', status=200)

    def test_languoids(self):
        res = self.app.get('/glottolog', status=200)
        res = self.app.get('/glottolog', accept='text/html', status=200)

    def test_languoidsmeta(self):
        res = self.app.get('/glottolog/glottologinformation', status=200)
        res = self.app.get('/glottolog/glottologinformation', accept='text/html', status=200)

    def test_langdoc(self):
        res = self.app.get('/langdoc', status=200)
        res = self.app.get('/langdoc', accept='text/html', status=200)

    def test_langdocmeta(self):
        res = self.app.get('/langdoc/langdocinformation', status=200)
        res = self.app.get('/langdoc/langdocinformation', accept='text/html', status=200)
