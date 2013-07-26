# -*- coding: utf-8 -*-
"""
Project related model.
"""
from string import capwords
from datetime import datetime
from copy import copy

from zope.interface import implementer

from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
    Float,
    DateTime,
    desc,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.hybrid import hybrid_property

from clld.interfaces import ISource, ILanguage
from clld.db.meta import DBSession, Base, CustomModelMixin
from clld.db.models.common import Language, Source, HasSourceMixin, IdNameDescriptionMixin
from clld.web.util.htmllib import literal
from clld.lib import bibtex
from clld.util import UnicodeMixin
from clld.util import DeclEnum

from glottolog3.interfaces import IProvider


@implementer(IProvider)
class Provider(Base, IdNameDescriptionMixin):
    """A provider of bibliographical data, i.e. entries in Ref.

    name -> id
    description -> name
    comment -> description
    """
    abbr = Column(Unicode)
    url = Column(Unicode)

    # if refurl is given, we can construct direct links to the provider's catalog ...
    refurl = Column(Unicode)
    # ... using the content of the bibfield attribute of a Ref instance.
    bibfield = Column(Unicode)


class Macroarea(Base, IdNameDescriptionMixin):
    pass


class Country(Base, IdNameDescriptionMixin):
    """
    alpha2 -> id
    name -> name
    """


class Languoidmacroarea(Base):
    __table_args__ = (UniqueConstraint('macroarea_pk', 'languoid_pk'),)
    macroarea_pk = Column(Integer, ForeignKey('macroarea.pk'))
    languoid_pk = Column(Integer, ForeignKey('languoid.pk'))


class Languoidcountry(Base):
    __table_args__ = (UniqueConstraint('country_pk', 'languoid_pk'),)
    country_pk = Column(Integer, ForeignKey('country.pk'))
    languoid_pk = Column(Integer, ForeignKey('languoid.pk'))


class Superseded(Base):
    languoid_pk = Column(Integer, ForeignKey('languoid.pk'))
    replacement_pk = Column(Integer, ForeignKey('languoid.pk'))
    # relation is one of: duplicate, father of spurious dialect, child of megalolanguoid
    relation = Column(Unicode)


class Doctype(Base, IdNameDescriptionMixin):
    """
    id -> pk
    id -> id
    abbr -> abbr
    name -> name
    """
    abbr = Column(Unicode)

    def __unicode__(self):
        return capwords(self.name.replace('_', ' '))


class Refdoctype(Base):
    __table_args__ = (UniqueConstraint('doctype_pk', 'ref_pk'),)
    doctype_pk = Column(Integer, ForeignKey('doctype.pk'))
    ref_pk = Column(Integer, ForeignKey('ref.pk'))


class Refmacroarea(Base):
    __table_args__ = (UniqueConstraint('macroarea_pk', 'ref_pk'),)
    macroarea_pk = Column(Integer, ForeignKey('macroarea.pk'))
    ref_pk = Column(Integer, ForeignKey('ref.pk'))


class Refcountry(Base):
    __table_args__ = (UniqueConstraint('country_pk', 'ref_pk'),)
    country_pk = Column(Integer, ForeignKey('country.pk'))
    ref_pk = Column(Integer, ForeignKey('ref.pk'))


class Refprovider(Base):
    __table_args__ = (UniqueConstraint('provider_pk', 'ref_pk'),)
    provider_pk = Column(Integer, ForeignKey('provider.pk'))
    ref_pk = Column(Integer, ForeignKey('ref.pk'))

    @classmethod
    def get_stats(cls):
        return dict(
            DBSession.query(Provider.pk, func.count(cls.ref_pk).label('c'))
            .filter(Provider.pk == cls.provider_pk)
            .group_by(Provider.pk)
            .order_by(desc('c'))
            .all())


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------
class LanguoidLevel(DeclEnum):
    family = 'family', 'family'
    language = 'language', 'language'
    dialect = 'dialect', 'dialect'


class LanguoidStatus(DeclEnum):
    established = 'established', 'established'
    spurious = 'spurious', 'spurious'
    spurious_retired = 'spurious retired', 'spurious retired'
    unattested = 'unattested', 'unattested'
    provisional = 'provisional', 'provisional'
    retired = 'retired', 'retired'


@implementer(ILanguage)
class Languoid(Language, CustomModelMixin):
    """
    id -> pk
    alnumcode -> id
    primaryname -> name
    names, codes -> languageidentifier
    refs -> languagesource
    """
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)

    # hid is the id of a language in Harald's classification. I.e. if hid is None, the
    # languoid is not a H-Language.
    hid = Column(Unicode, unique=True)

    father_pk = Column(Integer, ForeignKey('languoid.pk'))
    family_pk = Column(Integer, ForeignKey('languoid.pk'))

    level = Column(LanguoidLevel.db_type())
    status = Column(LanguoidStatus.db_type())

    classificationcomment = Column(Unicode)  # the justification from Harald
    globalclassificationcomment = Column(Unicode)

    child_family_count = Column(Integer)
    child_language_count = Column(Integer)
    child_dialect_count = Column(Integer)

    children = relationship(
        'Languoid',
        order_by='Languoid.name, Languoid.id',
        foreign_keys=[father_pk],
        backref=backref('father', remote_side=[pk]))
    macroareas = relationship(
        Macroarea,
        secondary=Languoidmacroarea.__table__,
        order_by='Macroarea.id',
        backref=backref('languoids', order_by='Languoid.name, Languoid.id'))
    countries = relationship(
        Country,
        secondary=Languoidcountry.__table__,
        order_by='Country.name',
        backref=backref('languoids', order_by='Languoid.name, Languoid.id'))

    def get_replacements(self):
        return DBSession.query(Languoid, SpuriousReplacements.relation)\
            .filter(SpuriousReplacements.languoidbase_pk == self.pk)\
            .filter(SpuriousReplacements.replacement_pk == Languoid.pk)

    @hybrid_property
    def glottocode(self):
        return self.id

    @hybrid_property
    def child_count(self):
        return (self.child_dialect_count or 0) \
            + (self.child_family_count or 0) \
            + (self.child_language_count or 0)

    def get_ancestors(self):
        """
        :return: Generator yielding the line of ancestors of self back to the top-level\
        family.
        """
        languoid = self
        while languoid.father:
            languoid = languoid.father
            yield languoid

    def get_geocoords(self):
        """
        :return: sqlalchemy Query selecting quadrupels \
        (lid, primaryname, longitude, latitude) where lid is the Languoidbase.id of one\
        of the children of self.

        .. note::

            This method does not return the geo coordinates of the Languoid self, but of
            its descendants.
        """
        child_pks = DBSession.query(Languoid.pk)\
            .filter(Languoid.father_pk == self.pk).subquery()
        return DBSession.query(
            TreeClosureTable.parent_pk,
            Language.name,
            Language.longitude,
            Language.latitude,
            Language.id)\
            .filter(Language.pk == TreeClosureTable.child_pk)\
            .filter(TreeClosureTable.parent_pk.in_(child_pks))\
            .filter(Language.latitude != None)

    def classification(self, type_):
        assert type_ in ['fc', 'sc']
        for vs in self.valuesets:
            if vs.parameter.id == type_:
                return vs

    @property
    def fc(self):
        c = self.classification('fc')
        if c.description:
            return c

    @property
    def sc(self):
        c = self.classification('sc')
        if c.description:
            return c

    @property
    def crefs(self):
        def refs(t):
            c = self.classification(t)
            if c:
                return list(c.references)
            return []
        return refs('fc') + refs('sc')

    def __rdf__(self, request):
        if self.father:
            yield 'skos:broader', request.resource_url(self.father)
        for child in self.children:
            yield 'skos:narrower', request.resource_url(child)


@implementer(ISource)
class Ref(Source, CustomModelMixin):
    """
    id -> pk
    bibtexkey -> id
    author + year -> name
    title -> description
    """
    pk = Column(Integer, ForeignKey('source.pk'), primary_key=True)

    field_labels = [
        ('author', 'author'),
        ('editor', 'editor'),
        ('year', 'year'),
        ('title', 'title'),
        ('address', 'city'),
        ('publisher', 'publisher'),
        ('pages', 'pages'),
        ('startpage', 'start page'),
        ('endpage', 'end page'),
        ('numberofpages', 'number of pages'),
        ('type', 'bibliographic type'),
        ('ozbib_id', 'OZBIB ID'),
    ]
    endpage_int = Column(Integer)
    inlg = Column(Unicode, index=True)
    inlg_code = Column(Unicode, index=True)
    subject = Column(Unicode)
    subject_headings = Column(Unicode)
    keywords = Column(Unicode)
    normalizedauthorstring = Column(Unicode)
    normalizededitorstring = Column(Unicode)
    ozbib_id = Column(Integer)

    providers = relationship(
        Provider,
        secondary=Refprovider.__table__,
        order_by='Provider.name',
        backref=backref(
            'refs', order_by='Source.author, Source.year, Source.description'))

    doctypes = relationship(
        Doctype,
        secondary=Refdoctype.__table__,
        lazy=False,
        order_by='Doctype.name',
        backref=backref(
            'refs', order_by='Source.author, Source.year, Source.description'))

    macroareas = relationship(
        Macroarea,
        secondary=Refmacroarea.__table__,
        order_by='Macroarea.id',
        backref=backref(
            'refs', order_by='Source.author, Source.year, Source.description'))

    countries = relationship(
        Country,
        secondary=Refcountry.__table__,
        order_by='Country.name',
        backref=backref(
            'refs', order_by='Source.author, Source.year, Source.description'))


class TreeClosureTable(Base):
    __table_args__ = (UniqueConstraint('parent_pk', 'child_pk'),)
    parent_pk = Column(Integer, ForeignKey('languoid.pk'))
    child_pk = Column(Integer, ForeignKey('languoid.pk'))
    depth = Column(Integer)
