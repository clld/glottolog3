# -*- coding: utf-8 -*-
import transaction

from sqlalchemy import desc
from sqlalchemy.orm import joinedload_all
from clld.scripts.util import parsed_args
from clld.db.models.common import Identifier, LanguageIdentifier, Language
from clld.db.meta import DBSession

from glottolog3.models import Languoid


MAX_IDENTIFIER_PK = None


def create_name(names, l):
    global MAX_IDENTIFIER_PK
    if l.name not in names:
        MAX_IDENTIFIER_PK += 1
        id_ = Identifier(
            pk=MAX_IDENTIFIER_PK,
            id=str(MAX_IDENTIFIER_PK),
            name=l.name,
            description='Glottolog',
            type='name')
        DBSession.add(id_)
        pk = MAX_IDENTIFIER_PK
        names[l.name] = id_
    else:
        pk = names[l.name].pk
    DBSession.add(LanguageIdentifier(language_pk=l.pk, identifier_pk=pk))


def main(args):  # pragma: no cover
    global MAX_IDENTIFIER_PK

    with transaction.manager:
        MAX_IDENTIFIER_PK = DBSession.query(
            Identifier.pk).order_by(desc(Identifier.pk)).first()[0]

        gc_names = {i.name: i for i in DBSession.query(Identifier).filter(
            Identifier.type == 'name').filter(Identifier.description == 'Glottolog')}

        for l in DBSession.query(Languoid).options(joinedload_all(
            Language.languageidentifier, LanguageIdentifier.identifier
        )):
            for lid in l.languageidentifier:
                if lid.identifier.description == 'Glottolog 2012' or lid.identifier.description == 'Glottolog':
                    l.languageidentifier.remove(lid)
            create_name(gc_names, l)


if __name__ == '__main__':
    main(parsed_args())
