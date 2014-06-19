# -*- coding: utf-8 -*-
import json

from sqlalchemy import not_
import requests
import transaction
from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.util import icontains
from glottolog3.models import Languoid


DATA_FILE = 'endangeredlanguages.json'
BASE_URL = 'http://www.endangeredlanguages.com/lang/'


def main(args):
    path = args.data_file(DATA_FILE)
    if path.exists():
        with open(path) as fp:
            data = json.load(fp)
    else:
        data = {}

    count = 0
    with transaction.manager:
        for lang in DBSession.query(Languoid)\
                .filter(Languoid.hid != None)\
                .filter(not_(icontains(Languoid.hid, 'nocode'))):
            if len(lang.hid) != 3:
                print lang.hid
                continue

            if lang.hid not in data:
                data[lang.hid] = requests.get(BASE_URL + lang.hid).status_code != 500

            if data[lang.hid]:
                count += 1
                lang.update_jsondata(endangeredlanguages=BASE_URL + lang.hid)

    print 'assigned', count, 'urls'

    with open(args.data_file(DATA_FILE), 'w') as fp:
        json.dump(data, fp)


if __name__ == '__main__':  # pragma: no cover
    main(parsed_args((("--version",), dict(default=""))))