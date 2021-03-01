import os
import time

import pytest

from clld.lib.bibtex import Database


@pytest.mark.selenium
def test_site_search(selenium):
    input_ = selenium.get_page('site-search-input', url='/')
    input_.e.send_keys('deu')
    button = selenium.get_page('site-search-button')
    button.e.click()
    time.sleep(0.5)
    assert selenium.browser.find_element_by_link_text('stan1295') is not None


@pytest.mark.selenium
@pytest.mark.xfail(reason='flaky')
def test_map(selenium):
    map_ = selenium.get_map('/resource/languoid/id/berb1260.bigmap.html')
    map_.test_show_marker()
    map_.test_show_legend()
    map_.test_show_legend('languoids')


@pytest.mark.selenium
def test_datatable_family(selenium):
    dt = selenium.get_datatable('/glottolog/family')
    time.sleep(1)
    dt.filter('level', '--any--')
    time.sleep(1)
    assert dt.get_info().filtered > 350


@pytest.mark.selenium
def test_datatable_language(selenium):
    dt = selenium.get_datatable('/glottolog/language')
    dt.filter('name', u'\u00fc')
    assert dt.get_info().filtered == 16


@pytest.mark.selenium
def test_languoid_map_and_table(selenium):
    map_ = selenium.get_map('/resource/languoid/id/ghad1239')
    map_.test_show_marker()
    dt = selenium.get_datatable('/resource/languoid/id/berb1260')
    dt.filter('doctype', 'grammar')
    dt.sort('Year')
    dt.sort('Title')
    recs = dt.get_info().filtered
    assert not os.listdir(str(selenium.downloads))
    dt.download('bib')
    time.sleep(1.5)
    bib = Database.from_file(os.path.join(str(selenium.downloads), 'glottolog-refs.bib'))
    assert recs == len(bib)
