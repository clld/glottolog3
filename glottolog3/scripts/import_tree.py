# -*- coding: utf-8 -*-
"""
apply changes to the classification in the db.

input:
- glottolog-data/languoids/changes.json
"""
from __future__ import unicode_literals
import transaction

from sqlalchemy import desc

from clld.util import jsonload
from clld.db.models.common import Identifier, LanguageIdentifier, IdentifierType
from clld.db.meta import DBSession

from glottolog3.models import Languoid, Superseded, LanguoidLevel, LanguoidStatus
from glottolog3.scripts.util import (
    recreate_treeclosure, get_args, glottolog_name, glottolog_names,
)


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

        gl_name = glottolog_name()
        gl_names = glottolog_names()

        languoids = {l.pk: l for l in DBSession.query(Languoid)}
        for attrs in jsonload(args.data_dir.joinpath('languoids', 'changes.json')):
            replacement = attrs.pop('replacement', None)
            hname = attrs.pop('hname', None)

            for name, enum in [('level', LanguoidLevel), ('status', LanguoidStatus)]:
                if name in attrs:
                    attrs[name] = enum.from_string(attrs[name])

            l = languoids.get(attrs['pk'])
            if l:
                for k, v in attrs.items():
                    setattr(l, k, v)
                #
                # We do not assign ISO codes for existing languages, because it could be
                # that the ISO code is now assigned to a family node, due to a change
                # request, e.g. see https://github.com/clld/glottolog-data/issues/40
                #
                if len(l.hid or '') == 3 and not l.iso_code:
                    args.log.warn('Language with hid %s but no iso code!' % l.hid)
            else:
                l = Languoid(**attrs)
                DBSession.add(l)
                languoids[l.pk] = l

                if len(attrs.get('hid', '')) == 3:
                    create_identifier(
                        None, l, name=attrs['hid'], type=IdentifierType.iso.value)

                create_identifier(
                    gl_names.get(l.name),
                    l,
                    name=l.name,
                    description=gl_name.description,
                    type=gl_name.type)

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
    main(get_args())
