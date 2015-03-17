# -*- coding: utf-8 -*-
from collections import defaultdict

import requests
from sqlalchemy import not_
from clld.db.meta import DBSession
from clld.db.util import icontains
from clld.db.models.common import Language
from clld.lib.dsv import reader
from clld.lib.ethnologue import get_classification

from glottolog3.models import Languoid, TreeClosureTable, LanguoidLevel


JSON = 'ethnologue_subgroups.json'
BASE_URL = 'http://www.ethnologue.com/'
DATA_URL = BASE_URL + 'sites/default/files/LanguageCodes.tab'
DATA_FILE = 'LanguageCodes.tab'
LANGUAGE_URL = BASE_URL + 'language/'
SUBGROUP_URL = BASE_URL + 'subgroups/'


def download(args):
    with open(args.data_file(DATA_FILE), 'w') as fp:
        fp.write(requests.get(DATA_URL).content)
    # TODO: copy or downlad JSON!!!!


def update(args):
    codes = {}
    for lang in reader(args.data_file(DATA_FILE), namedtuples=True):
        codes[lang.LangID] = 1

    count = 0
    for lang in DBSession.query(Languoid)\
            .filter(Languoid.hid != None)\
            .filter(not_(icontains(Languoid.hid, 'nocode'))):
        if lang.hid in codes:
            lang.update_jsondata(ethnologue=LANGUAGE_URL + lang.hid)
        else:
            lang.update_jsondata(ethnologue=None)
            count += 1

    print count, 'iso codes have no ethnologue code'

    ethnologue = args.json

    leafsets = defaultdict(list)
    for id_, doc in ethnologue['docs'].items():
        for sid, spec in get_classification(id_, doc).items():
            leafs = sorted(set([p[0] for p in spec[2]]))
            if leafs:
                leafsets[tuple(leafs)].append(sid)

    all = 0
    matched = 0
    for family in DBSession.query(Languoid)\
            .filter(Languoid.level == LanguoidLevel.family)\
            .filter(Language.active == True):
        leafs = []
        all += 1
        for row in DBSession.query(TreeClosureTable.child_pk, Languoid.hid)\
                .filter(TreeClosureTable.parent_pk == family.pk)\
                .filter(TreeClosureTable.child_pk == Languoid.pk)\
                .filter(Languoid.hid != None):
            if len(row[1]) == 3:
                leafs.append(row[1])
        leafs = tuple(sorted(set(leafs)))
        for i, subgroup in enumerate(leafsets.get(leafs, [])):
            if i == 0:
                matched += 1
                family.update_jsondata(ethnologue=SUBGROUP_URL + subgroup)
                break
    print matched, 'of', all, 'families have an exact counterpart in ethnologue!'
