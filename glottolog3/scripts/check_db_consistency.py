#!/usr/bin/env python
# check_db_consistency.py - test for some application-specific db invariants

import itertools

import sqlalchemy as sa
import six

from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.models import Config, ValueSet

from glottolog3.models import Languoid, LanguoidLevel, LanguoidStatus,\
    TreeClosureTable, Language, BOOKKEEPING, Ref


class CheckMeta(type):

    __instances = []

    def __init__(self, name, bases, dct):
        super(CheckMeta, self).__init__(name, bases, dct)
        if 'invalid_query' in dct:
            self.__instances.append(self)

    def __iter__(self):
        return iter(self.__instances)


class Check(six.with_metaclass(CheckMeta, object)):

    detail = True

    def __init__(self):
        self.query = self.invalid_query(DBSession)

    def validate(self):
        self.invalid_count = self.query.count()
        print(self)
        if self.invalid_count:
            if self.detail:
                self.invalid = self.query.all()
                self.display()
            return False
        else:
            self.invalid_count = ()
            return True

    def display(self, number=25):
        ids = (i.id for i in itertools.islice(self.invalid, number))
        cont = ', ...' if number < self.invalid_count else ''
        print('    %s%s' % (', '.join(ids), cont))

    def __str__(self):
        if self.invalid_count:
            msg = '%d invalid\n    (violating %s)' % (self.invalid_count, self.__doc__)
        else:
            msg = 'OK'
        return '%s: %s' % (self.__class__.__name__, msg)


class DialectFather(Check):
    """Father of a dialect is a language or dialect."""

    def invalid_query(self, session):
        return session.query(Languoid)\
            .filter_by(active=True, level=LanguoidLevel.dialect)\
            .order_by(Languoid.id)\
            .join(Languoid.father, aliased=True)\
            .filter(Languoid.level.notin_(
                [LanguoidLevel.language, LanguoidLevel.dialect]))


class FamilyChildren(Check):
    """Family has at least one subfamily or language."""

    def invalid_query(self, session):
        return session.query(Languoid)\
            .filter_by(active=True, level=LanguoidLevel.family)\
            .filter(~Languoid.children.any(sa.and_(Languoid.active == True,
                Languoid.level.in_([LanguoidLevel.family, LanguoidLevel.language]))))\
            .order_by(Languoid.id)


class FatherFamily(Check):
    """Languoids have correct top-level family."""

    def invalid_query(self, session):
        cte = session.query(Languoid.pk, Languoid.father_pk)\
            .cte(recursive=True)
        parent = sa.orm.aliased(Languoid)
        cte = cte.union_all(session.query(cte.c.pk, parent.father_pk)\
            .join(parent, cte.c.father_pk == parent.pk)\
            .filter(parent.father_pk != None))
        family = sa.orm.aliased(Languoid)
        return session.query(Languoid).join(cte, Languoid.pk == cte.c.pk)\
            .outerjoin(family, sa.and_(cte.c.father_pk == family.pk, family.father_pk == None))\
            .filter(Languoid.family_pk != family.pk)\
            .order_by(Languoid.id)


class TreeClosure(Check):
    """Treeclosuretable is correct."""

    detail = False

    def invalid_query(self, session):
        cte = session.query(Languoid.pk,
                Languoid.pk.label('father_pk'), sa.literal(0).label('depth'))\
            .cte(recursive=True)
        parent = sa.orm.aliased(Languoid)
        cte = cte.union_all(session.query(cte.c.pk, parent.father_pk, cte.c.depth + 1)\
            .join(parent, cte.c.father_pk == parent.pk)\
            .filter(parent.father_pk != None))
        tree1 = session.query(TreeClosureTable.child_pk, TreeClosureTable.parent_pk, TreeClosureTable.depth)
        tree2 = session.query(cte.c.pk, cte.c.father_pk, cte.c.depth)
        diff = sa.union_all(tree1.except_all(tree2), tree2.except_all(tree1))
        return session.query(diff.alias())


class ChildCounts(Check):
    """Languoids have correct child family/language/dialect counts."""

    def invalid_query(self, session):
        cte = session.query(Languoid.pk, Languoid.father_pk, Languoid.level)\
            .filter(Languoid.father_pk != None).cte(recursive=True)
        parent = sa.orm.aliased(Languoid)
        cte = cte.union_all(session.query(cte.c.pk, parent.father_pk, cte.c.level)\
            .join(parent, cte.c.father_pk == parent.pk)\
            .filter(parent.father_pk != None))
        return session.query(Languoid)\
            .outerjoin(cte, Languoid.pk == cte.c.father_pk)\
            .group_by(Languoid)\
            .having(sa.or_(
                Languoid.child_family_count !=
                    sa.func.count(sa.func.nullif(cte.c.level != LanguoidLevel.family, True)),
                Languoid.child_language_count !=
                    sa.func.count(sa.func.nullif(cte.c.level != LanguoidLevel.language, True)),
                Languoid.child_dialect_count !=
                    sa.func.count(sa.func.nullif(cte.c.level != LanguoidLevel.dialect, True))))\
            .order_by((Languoid.id))


class FamilyLanguages(Check):
    """Family has at least two languages."""

    def invalid_query(self, session):
        child = sa.orm.aliased(Languoid, flat=True)
        return session.query(Languoid)\
            .filter_by(active=True, level=LanguoidLevel.family)\
            .join(TreeClosureTable, TreeClosureTable.parent_pk == Languoid.pk)\
            .outerjoin(child, sa.and_(
                TreeClosureTable.child_pk == child.pk,
                TreeClosureTable.depth > 0,
                child.level == LanguoidLevel.language))\
            .group_by(Language.pk, Languoid.pk)\
            .having(sa.func.count(child.pk) < 2)\
            .order_by(Languoid.id)


class SpuriousRetiredBookkeeping(Check):
    """Spurious retired languoids are under Bookkeeping."""

    def invalid_query(self, session):
        return session.query(Languoid)\
            .filter_by(status=LanguoidStatus.spurious_retired)\
            .filter(~Languoid.father.has(name=BOOKKEEPING))\
            .order_by(Languoid.id)


class BookkeepingNoChildren(Check):
    """Bookkeeping languoids lack children."""

    def invalid_query(self, session):
        return session.query(Languoid)\
            .filter(Languoid.father.has(name=BOOKKEEPING))\
            .filter(Languoid.children.any())\
            .order_by(Languoid.id)


class IsolateInactive(Check):
    """Inactive languoids lack parent and children."""

    def invalid_query(self, session):
        return session.query(Languoid)\
            .filter_by(active=False).filter(sa.or_(
                Languoid.father_pk != None,
                Languoid.children.any()))\
            .order_by(Languoid.id)


class GlottologName(Check):
    """Languoid has its name as Glottolog identifier."""

    def invalid_query(self, session):
        return session.query(Languoid)\
            .filter(~Languoid.identifiers.any(name=Languoid.name,
                type=u'name', description=u'Glottolog'))\
            .order_by(Languoid.id)


class UniqueName(Check):
    """Among active languages main Glottolog names are unique."""

    def invalid_query(self, session):
        other = sa.orm.aliased(Languoid)
        return session.query(Languoid)\
            .filter_by(active=True,
                status=LanguoidStatus.established,
                level=LanguoidLevel.language)\
            .filter(session.query(other).filter(other.pk != Languoid.pk)\
                .filter_by(active=True,
                    status=LanguoidStatus.established,
                    level=LanguoidLevel.language,
                    name=Languoid.name).exists())\
            .order_by(Languoid.id)


class RefRedirects(Check):
    """Redirects of reference ids target an unredirected id."""

    def invalid_query(self, session):
        return session.query(
                sa.func.regexp_replace(Config.key, u'\D', '', u'g').label('id'),
                sa.func.nullif(Config.value, u'__gone__').label('target'))\
            .filter(Config.key.like(u'__Source_%%__'))\
            .filter(session.query(sa.orm.aliased(Config))\
                .filter_by(key=sa.func.format(u'__Source_%s__', Config.value)).exists())\
            .order_by('id', 'target')


class MarkupRefLinks(Check):
    """Classification description source links are valid."""

    def invalid_query(self, session):
        vs_rid = sa.select([ValueSet.pk,
            sa.func.unnest(sa.func.regexp_matches(
                ValueSet.description, '\*\*(\d+)\*\*', 'g')).label('ref_id')]).alias()
        return session.query(ValueSet)\
            .filter(ValueSet.pk.in_(session.query(vs_rid.c.pk)\
                .filter(~session.query(Ref).filter_by(id=vs_rid.c.ref_id).exists())))\
            .order_by(ValueSet.id)


def main(args):
    for cls in Check:
        check = cls()
        check.validate()


if __name__ == '__main__':
    main(parsed_args())
