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
from __future__ import unicode_literals
from collections import defaultdict

import transaction
import requests
from bs4 import BeautifulSoup as bs
from sqlalchemy import desc

from clld.db.meta import DBSession
from clld.db.models.common import Language, Identifier, IdentifierType, LanguageIdentifier
from clld.lib.bibtex import EntryType
from clld.lib.iso import get_tab

from glottolog3.models import (
    Languoid, Doctype, Ref, Provider, LanguoidLevel, TreeClosureTable, LanguoidStatus,
)


HTML = 'http://www-01.sil.org/iso639-3/chg_requests.asp?order=CR_Number&chg_status=past'
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
    codes = {row[0] for row in DBSession.query(Languoid.hid).filter(Languoid.hid != None)
             if len(row[0]) == 3}
    macrolangs = defaultdict(list)
    for code in get_tab('macrolanguages'):
        if code.I_Id in codes:
            macrolangs[code.M_Id].append(code.I_Id)

    return macrolangs


def download(args):
    return dict(changerequests=changerequests(args), macrolanguages=macrolanguages(args))


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
    pk = int(DBSession.execute("select max(pk) from source").fetchone()[0])
    for crno, affected in args.json['changerequests'].items():
        year, serial = crno.split('-')
        title = 'Change Request Number %s' % crno
        ref = Ref.get(title, key='title', default=None)

        if not ref:
            iid += 1
            pk += 1
            ref = Ref(
                pk=pk,
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
                language_note=', '.join('%(Language Name)s [%(Affected Identifier)s]' % spec for spec in affected),
                jsondata=dict(hhtype=dtid, src=pid))
            ref.doctypes.append(dt)
            ref.providers.append(provider)

        for spec in affected:
            lang = Languoid.get(spec['Affected Identifier'], key='hid', default=None)
            if lang and lang not in ref.languages:
                ref.languages.append(lang)
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
                    identifier = Identifier(
                        pk=max_identifier_pk + 1,
                        id=str(max_identifier_pk + 1),
                        name=mid,
                        type=IdentifierType.iso.value)
                    DBSession.add(identifier)
                    DBSession.flush()
                    DBSession.add(LanguageIdentifier(
                        identifier_pk=identifier.pk, language_pk=family.pk))
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
