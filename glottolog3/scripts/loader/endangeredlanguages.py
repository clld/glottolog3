# -*- coding: utf-8 -*-
from sqlalchemy import not_
import requests
from clld.db.meta import DBSession
from clld.db.util import icontains
from glottolog3.models import Languoid


JSON = 'endangeredlanguages.json'
BASE_URL = 'http://www.endangeredlanguages.com/lang/'


def lquery():
    for lang in DBSession.query(Languoid)\
            .filter(Languoid.hid != None)\
            .filter(not_(icontains(Languoid.hid, 'nocode'))):
        if len(lang.hid) == 3:
            yield lang


def download(args):
    data = {}
    for lang in lquery():
        data[lang.hid] = requests.get(BASE_URL + lang.hid).status_code != 500
    return data


def update(args):
    for count, lang in enumerate(l for l in lquery() if args.json.get(l.hid)):
        lang.update_jsondata(endangeredlanguages=BASE_URL + lang.hid)

    print 'assigned', count, 'urls'

