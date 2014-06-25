# -*- coding: utf-8 -*-
import requests
from sqlalchemy import not_
from clld.db.meta import DBSession
from clld.db.util import icontains
from clld.lib.dsv import reader

from glottolog3.models import Languoid


DATA_URL = 'http://www.ethnologue.com/sites/default/files/LanguageCodes.tab'
DATA_FILE = 'LanguageCodes.tab'
BASE_URL = 'http://www.ethnologue.com/language/'


def download(args):
    with open(args.data_file(DATA_FILE), 'w') as fp:
        fp.write(requests.get(DATA_URL).content)


def update(args):
    codes = {}
    for lang in reader(args.data_file(DATA_FILE), namedtuples=True):
        codes[lang.LangID] = 1

    count = 0
    for lang in DBSession.query(Languoid)\
            .filter(Languoid.hid != None)\
            .filter(not_(icontains(Languoid.hid, 'nocode'))):
        if lang.hid in codes:
            lang.update_jsondata(ethnologue=BASE_URL + lang.hid)
        else:
            lang.update_jsondata(ethnologue=None)
            count += 1

    print count, 'iso codes have no ethnologue code'
