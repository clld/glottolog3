# -*- coding: utf-8 -*-
from urllib import quote

import requests
from bs4 import BeautifulSoup as bs
from clld.db.models.common import Language


JSON = 'languagelandscape.json'
BASE_URL = 'http://languagelandscape.org'


def ll_get(path):
    return bs(requests.get(BASE_URL + path.encode('utf8')).content)


def download(args):
    data = {}
    for a in ll_get('/languages/').find_all('a', href=True):
        if a['href'].startswith('/language/'):
            url = BASE_URL + quote(a['href'].encode('utf8'))
            if url not in data:
                for aa in ll_get(a['href']).find_all('a', href=True):
                    if aa['href'].startswith('http://glottolog.org/resource/languoid/id'):
                        data[url] = aa['href'].split('/')[-1]
                        break
    return data


def main(args):
    count = 0
    for url, glottocode in args.json.items():
        lang = Language.get(glottocode, default=None)
        if lang:
            count += 1
            lang.update_jsondata(languagelandscape=url)
    print 'assigned', count, 'languagelandscape urls'
