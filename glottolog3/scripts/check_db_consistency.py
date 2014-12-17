#!/usr/bin/env python
# check_db_consistency.py - test for some application-specific db invariants

import itertools

import sqlalchemy as sa
import six

from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from glottolog3.models import Languoid, LanguoidLevel, LanguoidStatus


class CheckMeta(type):

    __instances = []

    def __init__(self, name, bases, dct):
        super(CheckMeta, self).__init__(name, bases, dct)
        if 'invalid_query' in dct:
            self.__instances.append(self)

    def __iter__(self):
        return iter(self.__instances)


class Check(six.with_metaclass(CheckMeta, object)):

    def __init__(self):
        self.query = self.invalid_query(DBSession)
        self.invalid_count = self.query.count()
        self.invalid = self.query.all()
        print(self)
        
    def display(self, number=25):
        ids = (i.id for i in itertools.islice(self.invalid, number))
        cont = ', ...' if number < self.invalid_count else ''
        print('    %s%s' % (', '.join(ids), cont))

    def __str__(self):
        if self.invalid_count:
            msg = '%d invalid (%s)' % (self.invalid_count, self.__doc__)
        else:
            msg = 'OK'
        return '%s: %s' % (self.__class__.__name__, msg)


class DialectFather(Check):
    """Father of a dialect is a language or dialect."""

    def invalid_query(self, session):
        return session.query(Languoid)\
            .filter_by(active=True, level=LanguoidLevel.dialect)\
            .join(Languoid.father, aliased=True)\
            .filter(Languoid.level.notin_(
                [LanguoidLevel.language, LanguoidLevel.dialect]))\
            .order_by(Languoid.id)


class FamilyChildren(Check):
    """Family has at least one subfamily or language."""

    def invalid_query(self, session):
        return session.query(Languoid)\
            .filter_by(active=True, level=LanguoidLevel.family)\
            .filter(~Languoid.children.any(sa.and_(Languoid.active == True,
                Languoid.level.in_([LanguoidLevel.family, LanguoidLevel.language]))))\
            .order_by(Languoid.id)


class IsolateInactive(Check):
    """Inactive languoids lack parent and children."""

    def invalid_query(self, session):
        return session.query(Languoid)\
            .filter_by(active=False).filter(sa.or_(
                Languoid.father_pk != None,
                Languoid.family_pk != None,
                Languoid.child_family_count != 0,
                Languoid.child_language_count != 0,
                Languoid.child_dialect_count != 0,
                Languoid.children.any()))\
            .order_by(Languoid.id)


def main():
    parsed_args()
    for cls in Check:
        check = cls()
        if check.invalid:
            check.display()


if __name__ == '__main__':
    main()
