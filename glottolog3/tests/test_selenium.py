# coding: utf8
import time

from six.moves.configparser import ConfigParser
from path import path

from clld.lib.bibtex import Database
from clld.tests.util import TestWithSelenium, PageObject

import glottolog3


PROJECT = path(glottolog3.__file__).dirname().joinpath('..').abspath()


def get_app(config='development.ini'):
    cfg = PROJECT.joinpath(config)
    parser = ConfigParser()
    parser.read(cfg)
    return glottolog3.main({'__file__': str(cfg), 'here': str(PROJECT)},
        **{'sqlalchemy.url': parser.get('app:main', 'sqlalchemy.url')})


class Tests(TestWithSelenium):
    app = get_app()

    def test_site_search(self):
        input_ = PageObject(self.browser, 'site-search-input', self.url('/'))
        input_.e.send_keys('deu')
        button = PageObject(self.browser, 'site-search-button')
        button.e.click()
        time.sleep(0.5)
        self.assertIn('stan1295', self.browser.current_url)

    def test_map(self):
        map_ = self.get_map('/resource/languoid/id/berb1260.bigmap.html')
        #map_.test_show_marker()
        #map_.test_show_legend()
        #map_.test_show_legend('languoids')

    def test_datatable_family(self):
        dt = self.get_datatable('/glottolog/family')
        dt.filter('level', '--any--')
        self.assertTrue(dt.get_info().filtered > 3500)

    def test_datatable_language(self):
        dt = self.get_datatable('/glottolog/language')
        dt.filter('name', u'ü')
        self.assertEqual(dt.get_info().filtered, 14)

    def test_languoid_map_and_table(self):
        map_ = self.get_map('/resource/languoid/id/ghad1239')
        map_.test_show_marker()
        dt = self.get_datatable('/resource/languoid/id/berb1260')
        dt.filter('doctype', 'grammar')
        dt.sort('Year')
        dt.sort('Title')
        recs = dt.get_info().filtered
        assert not self.downloads.listdir()
        dt.download('bib')
        time.sleep(1.5)
        bib = Database.from_file(self.downloads.joinpath('glottolog-refs.bib'))
        self.assertEqual(recs, len(bib))
