# -*- coding: utf-8 -*-
"""
Add ISO 639-3 change requests as refs

ISO 639-3 Registration Authority. 2006. Change Request Number 2006-001.
Dallas: SIL International. (http://www.sil.org/iso639-3/cr_files/2006-001.pdf)

download
--------

Download the index of change requests, convert it to JSON.


update
------

Create the refs
"""
import json
from collections import defaultdict

import transaction
import requests
from bs4 import BeautifulSoup as bs
from sqlalchemy import desc

from clld.db.meta import DBSession
from clld.db.models.common import Language, Identifier, IdentifierType
from clld.lib.bibtex import EntryType
from clld.lib.iso import get_tab

from glottolog3.models import (
    Languoid, Doctype, Ref, Provider, LanguoidLevel, TreeClosureTable, LanguoidStatus,
)


HTML = 'http://www.sil.org/iso639-3/chg_requests.asp?order=CR_Number&chg_status=past'
JSON = 'sil-cr.json'


def text(n):
    return ' '.join(list(n.stripped_strings)).strip()


def changerequests(args):
    html = bs(requests.get(HTML).text)

    res = defaultdict(list)
    for i, tr in enumerate(html.find('table', **{'class': 'stripeMe'}).find_all('tr')):
        if i == 0:
            cols = [text(n) for n in tr.find_all('th')]
        else:
            r = dict(zip(cols, [text(n) for n in tr.find_all('td')]))
            res[r['CR Number']].append(r)
    return res


def macrolanguages(args):
    codes = dict(
        (row[0], 1)
        for row in DBSession.query(Languoid.hid).filter(Languoid.hid != None)
        if len(row[0]) == 3)

    macrolangs = defaultdict(list)
    for code in get_tab('macrolanguages'):
        if code.I_Id in codes:
            macrolangs[code.M_Id].append(code.I_Id)

    return macrolangs


def download(args):
    res = dict(changerequests=changerequests(args), macrolanguages=macrolanguages(args))
    with open(args.data_file(JSON), 'w') as fp:
        json.dump(res, fp)


def update(args):
    author = 'ISO 639-3 Registration Authority'
    pid = 'iso6393'
    dtid = 'overview'
    dt = Doctype.get(dtid)
    provider = Provider.get(pid, default=None)
    if provider is None:
        provider = Provider(
            id=pid,
            abbr=pid,
            name=author,
            description="Change requests submitted to the ISO 639-3 registration authority.")
    iid = max(int(DBSession.execute(
        "select max(cast(id as integer)) from source").fetchone()[0]), 500000)
    for crno, affected in args.json['changerequests'].items():
        year, serial = crno.split('-')
        title = 'Change Request Number %s' % crno
        ref = Ref.get(title, key='title', default=None)
        if ref:
            continue
        iid += 1
        ref = Ref(
            id=str(iid),
            name='%s %s' % (author, year),
            bibtex_type=EntryType.misc,
            number=crno,
            description=title,
            year=year,
            year_int=int(year),
            title=title,
            author=author,
            address='Dallas',
            publisher='SIL International',
            url='http://www.sil.org/iso639-3/cr_files/%s.pdf' % crno,
            doctypes_str=dtid,
            providers_str=pid,
            jsondata=dict(lgcode='', hhtype=dtid, src=pid))
        ref.doctypes.append(dt)
        ref.providers.append(provider)
        for spec in affected:
            lang = Languoid.get(spec['Affected Identifier'], key='hid', default=None)
            if lang:
                ref.languages.append(Language.get(lang.pk))
        DBSession.add(ref)

    transaction.commit()
    transaction.begin()

    matched = 0
    near = 0
    max_identifier_pk = DBSession.query(
        Identifier.pk).order_by(desc(Identifier.pk)).first()[0]
    families = []
    for family in DBSession.query(Languoid)\
            .filter(Languoid.level == LanguoidLevel.family)\
            .filter(Language.active == True)\
            .all():
        isoleafs = set()
        for row in DBSession.query(TreeClosureTable.child_pk, Languoid.hid)\
            .filter(family.pk == TreeClosureTable.parent_pk)\
            .filter(Languoid.pk == TreeClosureTable.child_pk)\
            .filter(Languoid.hid != None)\
            .filter(Languoid.level == LanguoidLevel.language)\
            .filter(Languoid.status == LanguoidStatus.established)\
            .all():
            if len(row[1]) == 3:
                isoleafs.add(row[1])
        families.append((family, isoleafs))

    families = sorted(families, key=lambda p: len(p[1]))

    for mid, leafs in args.json['macrolanguages'].items():
        leafs = set(leafs)
        found = False
        for family, isoleafs in families:
            if leafs == isoleafs:
                if mid not in [c.name for c in family.identifiers
                               if c.type == IdentifierType.iso.value]:
                    family.codes.append(Identifier(
                        id=str(max_identifier_pk + 1),
                        name=mid,
                        type=IdentifierType.iso.value))
                    max_identifier_pk += 1
                matched += 1
                found = True
                break
            elif leafs.issubset(isoleafs):
                print '~~~', family.name, '-->', mid, 'distance:', len(leafs), len(isoleafs)
                near += 1
                found = True
                break
        if not found:
            print '---', mid, leafs

    print 'matched', matched, 'of', len(args.json['macrolanguages']), 'macrolangs'
    print near
