# -*- coding: utf-8 -*-
import sys
import transaction
import json
from itertools import groupby

from sqlalchemy import desc, or_

from clld.scripts.util import parsed_args
from clld.lib import iso
from clld.db.meta import DBSession
from clld.db.models.common import Language, LanguageIdentifier, Identifier, IdentifierType

from glottolog3.models import Languoid, TreeClosureTable, LanguoidLevel


def get_macrolangs(codes):
    for code in iso.get_tab('macrolanguages'):
        if code.i_id in codes:
            yield code.m_id, code.i_id


def main(args):  # pragma: no cover
    i = 0
    matched = 0
    near = 0
    with transaction.manager:
        max_identifier_pk = DBSession.query(
            Identifier.pk).order_by(desc(Identifier.pk)).first()[0]
        codes = dict(
            (row[0], 1)
            for row in DBSession.query(Languoid.hid).filter(Languoid.hid != None)
            if len(row[0]) == 3)
        macrolangs = dict(
            (k, set(gg[1] for gg in g))
            for k, g in groupby(get_macrolangs(codes), lambda p: p[0]))

        families = []
        for family in DBSession.query(Languoid)\
                .filter(Languoid.level == LanguoidLevel.family)\
                .filter(Language.active == True)\
                .all():
            isoleafs = set()
            i += 1

            if i % 100 == 0:
                print i

            for row in DBSession.query(TreeClosureTable.child, Languoid.hid)\
                .filter(family.pk == TreeClosureTable.parent_pk)\
                .filter(Languoid.pk == TreeClosureTable.child_pk)\
                .filter(Languoid.hid != None)\
                .filter(Languoid.level == LanguoidLevel.language)\
                .filter(Languoid.status == 'established')\
                .all():
                if len(row[1]) == 3:
                    isoleafs.add(row[1])

            families.append((family, isoleafs))

        families = sorted(families, key=lambda p: len(p[1]))

        for mid, leafs in macrolangs.items():
            found = False
            for family, isoleafs in families:
                if leafs == isoleafs:
                    if mid not in [c.name for c in family.identifiers if c.type == IdentifierType.iso.value]:
                        family.codes.append(Identifier(
                            id=str(max_identifier_pk + 1),
                            name=mid,
                            type=IdentifierType.iso.value))
                        max_identifier_pk += 1
                    matched += 1
                    found = True
                    break
                elif leafs.issubset(isoleafs):
                    print '~~~', family.primaryname, '-->', mid, 'distance:', len(leafs), len(isoleafs)
                    near += 1
                    found = True
                    break
            if not found:
                print '---', mid, leafs

    print 'matched', matched, 'of', len(macrolangs), 'macrolangs'
    print near


if __name__ == '__main__':
    main(parsed_args())
