# -*- coding: utf-8 -*-
import sys
import transaction
import json

from sqlalchemy import desc
from clld.scripts.util import parsed_args
from clld.db.models.common import Identifier, LanguageIdentifier, IdentifierType
from clld.db.meta import DBSession

from glottolog3.models import (
    Languoid, Macroarea, Superseded, LanguoidLevel, LanguoidStatus,
)
from glottolog3.scripts.util import recreate_treeclosure
from glottolog3.lib.util import get_map


MAX_IDENTIFIER_PK = None


def create_identifier(identifier, l, **kw):
    global MAX_IDENTIFIER_PK
    if identifier is None:
        MAX_IDENTIFIER_PK += 1
        DBSession.add(Identifier(pk=MAX_IDENTIFIER_PK, id=str(MAX_IDENTIFIER_PK), **kw))
        pk = MAX_IDENTIFIER_PK
    else:
        pk = identifier.pk
    DBSession.add(LanguageIdentifier(language_pk=l.pk, identifier_pk=pk))


def main(args):  # pragma: no cover
    global MAX_IDENTIFIER_PK

    with transaction.manager:
        MAX_IDENTIFIER_PK = DBSession.query(
            Identifier.pk).order_by(desc(Identifier.pk)).first()[0]

        gc_names = {i.name: i for i in DBSession.query(Identifier).filter(
            Identifier.type == 'name').filter(Identifier.description == 'Glottolog')}

        ma_map = get_map(Macroarea)
        languoids = dict((l.pk, l) for l in DBSession.query(Languoid))
        with open(args.data_file(args.version, 'languoids.json')) as fp:
            for attrs in json.load(fp):
                ma = attrs.pop('macroarea', None)
                replacement = attrs.pop('replacement', None)
                hname = attrs.pop('hname', None)

                for name, enum in [('level', LanguoidLevel), ('status', LanguoidStatus)]:
                    if name in attrs:
                        attrs[name] = enum.from_string(attrs[name])

                l = languoids.get(attrs['pk'])
                if l:
                    for k, v in attrs.items():
                        if k == 'globalclassificationcomment':
                            continue
                        setattr(l, k, v)
                    if len(l.hid or '') == 3:
                        if not l.iso_code:
                            create_identifier(
                                None, l, name=l.hid, type=IdentifierType.iso.value)
                else:
                    l = Languoid(**attrs)
                    DBSession.add(l)
                    languoids[l.pk] = l

                    if len(attrs.get('hid', '')) == 3:
                        create_identifier(
                            None, l, name=attrs['hid'], type=IdentifierType.iso.value)
                    if ma:
                        l.macroareas.append(ma_map[ma])

                    create_identifier(
                        gc_names.get(l.name),
                        l,
                        name=l.name,
                        description='Glottolog',
                        type='name')

                if hname:
                    l.update_jsondata(hname=hname)

                if replacement:
                    DBSession.add(Superseded(
                        languoid_pk=l.pk,
                        replacement_pk=replacement,
                        relation='classification update'))

                DBSession.flush()

        recreate_treeclosure()


if __name__ == '__main__':
    main(parsed_args((("--version",), dict(default=""))))
