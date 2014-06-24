# -*- coding: utf-8 -*-
import json

from sqlalchemy import not_
import requests
import transaction
from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.util import icontains
from glottolog3.models import Languoid


DATA_FILE = 'ethnologue.json'
BASE_URL = 'http://www.ethnologue.com/language/'
TRIGGER = lambda code: 'Ethnologue has no page for ' + code


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
                continue

            if lang.hid not in data:
                r = requests.get(BASE_URL + lang.hid)
                data[lang.hid] = r.status_code == 200 and TRIGGER(lang.hid) not in r.text

            if data[lang.hid]:
                lang.update_jsondata(ethnologue=BASE_URL + lang.hid)
            else:
                count += 1

    print count, 'iso codes have no ethnologue code'

    with open(args.data_file(DATA_FILE), 'w') as fp:
        json.dump(data, fp)


if __name__ == '__main__':  # pragma: no cover
    main(parsed_args())