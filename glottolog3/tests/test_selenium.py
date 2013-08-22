import time

from path import path

from clld.lib.bibtex import Database
from clld.tests.util import TestWithSelenium

import glottolog3


PROJECT = path(glottolog3.__file__).dirname().joinpath('..').abspath()


class Tests(TestWithSelenium):
    app = glottolog3.main(
        {'__file__': str(PROJECT.joinpath('development.ini')), 'here': str(PROJECT)},
        **{'sqlalchemy.url': 'postgres://robert@/glottolog3'})

    def test_map(self):
        map_ = self.get_map('/resource/languoid/id/berb1260.bigmap.html')
        map_.test_show_marker()
        map_.test_show_legend()
        map_.test_show_legend('languoids')

    def test_datatable_family(self):
        dt = self.get_datatable('/glottolog/family')
        dt.filter('level', '--any--')
        self.assertEqual(dt.get_info().filtered, 3961)

    def test_datatable_language(self):
        dt = self.get_datatable('/glottolog/language')
        dt.filter('name', u'\xfc')
        self.assertEqual(dt.get_info().filtered, 1)

    def test_languoid_map_and_table(self):
        map_ = self.get_map('/resource/languoid/id/berb1260')
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
