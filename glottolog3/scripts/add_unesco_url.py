# -*- coding: utf-8 -*-

import requests
import transaction
from bs4 import BeautifulSoup as bs
from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.models.common import Language
from clld.lib.dsv import reader
from glottolog3.models import Languoid


DATA_FILE = 'unesco_atlas_languages_limited_dataset.csv'
BASE_URL = 'http://languagelandscape.org'
"""
ID
Name in English
Name in French
Name in Spanish	Countries
Country codes alpha 3
ISO639-3 codes
Degree of endangerment
"""




def main(args):
    count = 0
    notfound = {}
    with transaction.manager:
        for item in reader(args.data_file(DATA_FILE), dicts=True):
            if item['ISO639-3 codes']:
                for code in item['ISO639-3 codes'].split(','):
                    code = code.strip()
                    lang = Languoid.get(code, key='hid', default=None)
                    if lang:
                        count += 1
                        item['url'] = 'http://www.unesco.org/culture/languages-atlas/en/atlasmap/language-iso-%s.html' % code
                        lang.update_jsondata(unesco=item)
                    else:
                        notfound[code] = 1
    print 'assigned', count, 'unesco urls'
    print 'missing iso codes:', notfound


if __name__ == '__main__':  # pragma: no cover
    main(parsed_args((("--version",), dict(default=""))))