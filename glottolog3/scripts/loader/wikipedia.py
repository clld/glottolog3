# -*- coding: utf-8 -*-
"""
To be able to add links to wikipedia (and multitree), we import data scraped from
wikipedia.

This data is stored in tab-separated values as follows:

Name	Glottolog	LinguistList	Wiki
Late British; Common Brittonic	bryt1239	1bd	Common_Brittonic


download
--------

Converts the tab-separated data into JSON data, additionally checking the validity of
multitree identifiers.


update
------

For each matching languoid we add
- the name of the wikipedia page as jsondata['wikipedia'],
- multitree identifiers.
"""
from __future__ import unicode_literals
import re
from collections import defaultdict

import requests
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.dsv import reader
from glottolog3.models import Languoid


DATA_FILE = 'missing_links.tab'
JSON = 'missing_links.json'
GC_PATTERN = re.compile('[a-z]{4}[0-9]{4}$')
LL_PATTERN = re.compile('(?P<code>[\w]{3}(\-[\w]{3})?)')


def ll_codes(item):
    if item.LinguistList:
        s = item.LinguistList.replace('(link does not work)', '')
        for m in LL_PATTERN.finditer(s):
            code = m.group('code')
            if requests.get('http://multitree.org/codes/' + code).status_code == 200:
                # Note: Invalid identifiers result in HTTP 500.
                yield code


def download(args):
    data = dict(wikipedia={}, multitree=defaultdict(list))
    for item in reader(args.data_file(DATA_FILE), namedtuples=True):
        if item.Glottolog and GC_PATTERN.match(item.Glottolog.strip()):
            data['wikipedia'][item.Glottolog.strip()] = item.Wiki.strip()
            for code in ll_codes(item):
                data['multitree'][item.Glottolog.strip()].append(code)
    return data


def update(args):
    count = 0
    assert args.json

    iid = int(DBSession.execute(
        "select max(cast(id as integer)) from identifier").fetchone()[0]) + 1

    langs = {}
    for gid, name in args.json['wikipedia'].items():
        if gid not in langs:
            langs[gid] = Languoid.get(gid)
        langs[gid].update_jsondata(wikipedia=name.split('/')[-1])

    for gid, codes in args.json['multitree'].items():
        l = langs[gid]
        lcodes = [i.name for i in l.identifiers if i.type == 'multitree']

        for code in set(codes):
            if code not in lcodes:
                identifier = DBSession.query(common.Identifier)\
                    .filter(common.Identifier.type == 'multitree')\
                    .filter(common.Identifier.name == code)\
                    .first()
                if not identifier:
                    identifier = common.Identifier(
                        id=str(iid), name=code, type='multitree')
                    iid += 1
                count += 1
                DBSession.add(
                    common.LanguageIdentifier(language=l, identifier=identifier))

    print count, 'new multitree identifiers'
