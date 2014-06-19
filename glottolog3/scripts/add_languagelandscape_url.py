# -*- coding: utf-8 -*-
import json
from urllib import quote

import requests
import transaction
from bs4 import BeautifulSoup as bs
from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.models.common import Language

from glottolog3.scripts.util import match_obsolete_refs, get_obsolete_refs
from glottolog3.models import Ref

DATA_FILE = 'languagelandscape.json'
BASE_URL = 'http://languagelandscape.org'


def ll_get(path):
    print 'requesting', path
    return bs(requests.get(BASE_URL + path.encode('utf8')).content)


def ll_read(args):
    path = args.data_file(DATA_FILE)
    if path.exists():
        with open(path) as fp:
            data = json.load(fp)
    else:
        data = {}
    return data

    for a in ll_get('/languages/').find_all('a', href=True):
        if a['href'].startswith('/language/'):
            try:
                url = BASE_URL + quote(a['href'].encode('utf8'))
                if url not in data:
                    for aa in ll_get(a['href']).find_all('a', href=True):
                        if aa['href'].startswith('http://glottolog.org/resource/languoid/id'):
                            data[url] = aa['href'].split('/')[-1]
                            break
            except:
                print a['href']
                raise
    with open(args.data_file(DATA_FILE), 'w') as fp:
        json.dump(data, fp)

    return data


def main(args):
    ll = ll_read(args)

    count = 0
    with transaction.manager:
        for url, glottocode in ll.items():
            lang = Language.get(glottocode, default=None)
            if lang:
                count += 1
                lang.update_jsondata(languagelandscape=url)
    print 'assigned', count, 'languagelandscape urls'


if __name__ == '__main__':  # pragma: no cover
    main(parsed_args((("--version",), dict(default=""))))
