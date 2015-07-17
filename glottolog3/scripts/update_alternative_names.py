# -*- coding: utf-8 -*-
from collections import Counter

import transaction

from sqlalchemy import desc
from sqlalchemy.orm import joinedload_all
from clld.scripts.util import parsed_args
from clld.db.models.common import Identifier, LanguageIdentifier, Language, IdentifierType
from clld.db.meta import DBSession

from glottolog3.models import Languoid
from glottolog3.scripts.util import glottolog_names, glottolog_name


MAX_IDENTIFIER_PK = None


def create_name(names, l):
    res = []
    global MAX_IDENTIFIER_PK
    if l.name not in names:
        res.append('newname')
        MAX_IDENTIFIER_PK += 1
        id_ = glottolog_name(pk=MAX_IDENTIFIER_PK, id=str(MAX_IDENTIFIER_PK), name=l.name)
        DBSession.add(id_)
        pk = MAX_IDENTIFIER_PK
        names[l.name] = id_
    else:
        pk = names[l.name].pk
    if pk not in [li.identifier_pk for li in l.languageidentifier]:
        res.append('newrelation')
        DBSession.add(LanguageIdentifier(language_pk=l.pk, identifier_pk=pk))
    return res


def main(args):  # pragma: no cover
    global MAX_IDENTIFIER_PK
    stats = Counter()

    with transaction.manager:
        MAX_IDENTIFIER_PK = DBSession.query(
            Identifier.pk).order_by(desc(Identifier.pk)).first()[0]

        gl_names = glottolog_names()

        for l in DBSession.query(Languoid).options(joinedload_all(
            Language.languageidentifier, LanguageIdentifier.identifier
        )):
            stats.update(create_name(gl_names, l))
    args.log.info('%s' % stats)


if __name__ == '__main__':
    main(parsed_args())
