# -*- coding: utf-8 -*-
import sys
import transaction
import json

from sqlalchemy import desc
from clld.scripts.util import parsed_args
from clld.db.models.common import Identifier, LanguageIdentifier, IdentifierType
from clld.db.meta import DBSession
from clld.util import EnumSymbol

from glottolog3.models import Languoid, Macroarea, Superseded
from glottolog3.lib.util import get_map


def main(args):  # pragma: no cover
    with transaction.manager:
        max_identifier_pk = DBSession.query(
            Identifier.pk).order_by(desc(Identifier.pk)).first()[0]
        ma_map = get_map(Macroarea)
        languoids = dict((l.pk, l) for l in DBSession.query(Languoid))
        with open(args.data_file('languoids.json')) as fp:
            for attrs in json.load(fp):
                ma = attrs.pop('macroarea', None)
                replacement = attrs.pop('replacement', None)
                hname = attrs.pop('hname', None)

                l = languoids.get(attrs['pk'])
                if l:
                    for k, v in attrs.items():
                        if k == 'globalclassificationcomment':
                            continue
                        cv = getattr(l, k)
                        if isinstance(cv, EnumSymbol):
                            cv = cv.value
                        assert v == cv
                        #setattr(l, k, v)
                    if len(l.hid or '') == 3:
                        assert l.iso_code
                        #if not l.iso_code:
                        #    l.identifiers.append(
                        #        Identifier(
                        #            id=str(max_identifier_pk + 1),
                        #            name=l.hid,
                        #            type=IdentifierType.iso.value))
                        #    max_identifier_pk += 1
                else:
                    raise ValueError()
                    try:
                        l = Languoid(**attrs)
                    except Exception:
                        print attrs
                        raise
                    DBSession.add(l)
                    languoids[l.pk] = l

                    if len(attrs.get('hid', '')) == 3:
                        l.identifiers.append(
                            Identifier(
                                id=str(max_identifier_pk + 1),
                                name=attrs['hid'],
                                type=IdentifierType.iso.value))
                        max_identifier_pk += 1
                    if ma:
                        l.macroareas.append(ma_map[ma])

                    l.identifiers.append(
                        Identifier(
                            id=str(max_identifier_pk + 1),
                            name=l.name,
                            description='Glottolog',
                            type='name'))
                    max_identifier_pk += 1

                if hname:
                    assert l.jsondata['hname'] == hname
                    #l.hname = hname

                if replacement:
                    raise ValueError()
                    DBSession.add(Superseded(
                        languoid_pk=l.pk,
                        replacement_pk=replacement,
                        relation='classification update'))

                #DBSession.flush()


if __name__ == '__main__':
    main(parsed_args())
