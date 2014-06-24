# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
import json
from collections import defaultdict

import requests
import transaction
from clld.scripts.util import parsed_args, Data
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.dsv import reader
from glottolog3.models import Languoid


DATA_FILE = 'wikipedia/missing_links.tab'
JSON_FILE = 'wikipedia/missing_links.json'
GC_PATTERN = re.compile('[a-z]{4}[0-9]{4}$')
LL_PATTERN = re.compile('(?P<code>[\w]{3}(\-[\w]{3})?)')


def ll_codes(item):
    if item.LinguistList:
        s = item.LinguistList.replace('(link does not work)', '')
        for m in LL_PATTERN.finditer(s):
            code = m.group('code')
            if requests.get('http://multitree.org/codes/' + code).status_code == 200:
                yield code


def main(args):
    count = 0
    data = args.data_file(JSON_FILE)
    if data.exists():
        with open(data) as fp:
            data = json.load(fp)
    else:
        data = dict(wikipedia={}, multitree=defaultdict(list))
        for item in reader(args.data_file(DATA_FILE), namedtuples=True):
            if item.Glottolog and GC_PATTERN.match(item.Glottolog.strip()):
                data['wikipedia'][item.Glottolog.strip()] = item.Wiki.strip()
                for code in ll_codes(item):
                    data['multitree'][item.Glottolog.strip()].append(code)
        with open(args.data_file(JSON_FILE), 'w') as fp:
            json.dump(data, fp)

    with transaction.manager:
        iid = int(DBSession.execute(
            "select max(cast(id as integer)) from identifier").fetchone()[0]) + 1
        langs = {}
        for gid, name in data['wikipedia'].items():
            if gid not in langs:
                langs[gid] = Languoid.get(gid)
            langs[gid].update_jsondata(wikipedia=name.split('/')[-1])

        for gid, codes in data['multitree'].items():
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


if __name__ == '__main__':  # pragma: no cover
    main(parsed_args())