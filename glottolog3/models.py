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
    and_,
    cast,
    Text,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.hybrid import hybrid_property

from clld.interfaces import ISource, ILanguage
from clld.db.meta import DBSession, Base, CustomModelMixin
from clld.db.models.common import (
    Language, Source, HasSourceMixin, IdNameDescriptionMixin, IdentifierType, Identifier,
)
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


DOCTYPES = [
    'grammar',
    'grammarsketch',
    'dictionary',
    'specificfeature',
    'phonology',
    'text',
    'newtestament',
    'wordlist',
    'comparative',
    'minimal',
    'socling',
    'dialectology',
    'overview',
    'ethnographic',
    'bibliographical',
    'unknown']


class Doctype(Base, IdNameDescriptionMixin):
    """
    id -> pk
    id -> id
    abbr -> abbr
    name -> name
    """
    abbr = Column(Unicode)

    ord = Column(Integer)

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
class Languoid(CustomModelMixin, Language):
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

    descendants = relationship(
        'Languoid',
        order_by='Languoid.name, Languoid.id',
        foreign_keys=[family_pk],
        backref=backref('family', remote_side=[pk]))
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

    def get_identifier_objs(self, type_):
        if getattr(type_, 'value', type_) == IdentifierType.glottolog.value:
            return [
                Identifier(name=self.id, type=IdentifierType.glottolog.value)]
        #elif type_ == IdentifierType.iso and :
        #    return
        return Language.get_identifier_objs(self, type_)

    def get_replacements(self):
        return DBSession.query(Languoid, Superseded.relation)\
            .filter(Superseded.languoid_pk == self.pk)\
            .filter(Superseded.replacement_pk == Languoid.pk)

    def get_ancestors(self, session=None):
        """
        :return: Iterable of ancestors of self back to the top-level family.
        """
        session = session or DBSession
        # retrieve the ancestors ordered by distance, i.e. from direct parent
        # to top-level family:
        return session.query(Languoid)\
            .join(TreeClosureTable, and_(
                TreeClosureTable.parent_pk == Languoid.pk,
                TreeClosureTable.depth > 0))\
            .filter(TreeClosureTable.child_pk == self.pk)\
            .order_by(TreeClosureTable.depth)

    def __json__(self, req=None, core=False):
        def ancestor(l):
            r = {"name": l.name, "id": l.id}
            if req:
                r['url'] = req.resource_url(l)
            return r
        res = super(Languoid, self).__json__(req)
        if not core:
            res['classification'] = [ancestor(l) for l in reversed(list(self.get_ancestors()))]
            if self.iso_code:
                res[IdentifierType.iso.value] = self.iso_code
        return res

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
    def endangerment(self):
        for vs in self.valuesets:
            if vs.parameter.id == 'vitality':
                return vs.values[0].name

    @property
    def fc(self):
        c = self.classification('fc')
        if c and c.description:
            return c

    @property
    def sc(self):
        c = self.classification('sc')
        if c and c.description:
            return c

    def _crefs(self, t):
        c = self.classification(t)
        if c:
            return list(c.references)
        return []

    @property
    def crefs(self):
        return sorted(
            self._crefs('fc') + self.screfs, key=lambda r: -(r.source.year_int or 0))

    @property
    def screfs(self):
        """
        The subclassification justification have a hereditary semantics. I.e.,
        if there is a reference to, e.g., Indo-European it justifies every child
        such as Germanic, Northwest Germanic and so on unless the child has its
        own justification (in which case that ref supersedes and takes over everything
        below). Suppose one is looking at a subfamily without its own
        explicit justification, then one should get the parent justification.
        """
        res = self._crefs('sc')
        if not res:
            if self.father:
                res = self.father.screfs
        return res

    def __rdf__(self, request):
        gold_type = None
        if self.level == LanguoidLevel.family:
            gold_type = 'LanguageSubfamily' if self.father_pk else 'LanguageFamily'
        elif self.level == LanguoidLevel.language:
            gold_type = 'Language'
        elif self.level == LanguoidLevel.dialect:
            gold_type = 'Dialect'
        if gold_type:
            yield 'rdf:type', 'http://purl.org/linguistics/gold/' + gold_type
        if self.father:
            yield 'skos:broader', request.resource_url(self.father)
        for child in self.children:
            yield 'skos:narrower', request.resource_url(child)
        for l, why in self.get_replacements():
            yield 'dcterms:isReplacedBy', request.resource_url(l)
        if not self.active:
            yield 'skos:changeNote', 'obsolete'
        if self.status:
            yield 'skos:editorialNote', self.status.description
        for area in self.macroareas:
            yield 'dcterms:spatial', area.name
        for country in self.countries:
            yield 'dcterms:spatial', 'http://www.geonames.org/countries/%s/' % country.id

    def jqtree(self, icon_map=None):
        tree_ = []
        children_map = {}
        children_of_self = [c.pk for c in self.children]

        query = DBSession.query(
            Languoid.father_pk,
            Languoid.pk, Languoid.id, Languoid.name,
            Languoid.latitude, Languoid.hid,
            cast(Languoid.level, Text), cast(Languoid.status, Text),
            Languoid.child_language_count, TreeClosureTable.depth)\
        .select_from(Languoid).join(TreeClosureTable,
            Languoid.pk == TreeClosureTable.child_pk)\
        .filter(TreeClosureTable.parent_pk == (self.family_pk or self.pk))\
        .order_by(TreeClosureTable.depth, Languoid.name)

        for row in query:
            fpk, cpk, id_, name, lat, hid, level, status, clc, depth = row
            if hid and len(hid) != 3:
                hid = None

            label = name
            if clc:
                label += ' (%s)' % clc
            #label = '%s [%s]' % (name, id_)
            #if level == 'language' and hid and len(hid) == 3:
            #    label += '[%s]' % hid
            node = {'id': id_, 'pk': cpk, 'iso': hid, 'level': level, 'status': status, 'label': label, 'children': []}
            if icon_map and id_ == self.id and lat:
                node['map_marker'] = icon_map[cpk]
            if cpk in children_of_self:
                node['child'] = True
                if icon_map and (level == 'family' or lat):
                    node['map_marker'] = icon_map[cpk]
            children_map[cpk] = node['children']

            if not fpk:
                tree_.append(node)
            else:
                if fpk not in children_map:
                    # this can be the case for dialects attached to inactive nodes
                    continue
                children_map[fpk].append(node)
        return tree_


@implementer(ISource)
class Ref(CustomModelMixin, Source):
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
    language_note = Column(Unicode)

    #: store the trigger for computerized assignment of languages
    ca_language_trigger = Column(Unicode)

    #: store the trigger for computerized assignment of doctype
    ca_doctype_trigger = Column(Unicode)

    doctypes_str = Column(Unicode)
    providers_str = Column(Unicode)

    providers = relationship(
        Provider,
        secondary=Refprovider.__table__,
        order_by='Provider.name',
        backref=backref(
            'refs', order_by='Source.author, Source.year, Source.description'))

    doctypes = relationship(
        Doctype,
        secondary=Refdoctype.__table__,
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

    def __rdf__(self, request):
        """
        % for provider in ctx.providers:
        <dcterms:provenance rdf:parseType="Resource">
            <dcterms:description rdf:resource="${request.route_url('langdoc.meta', _anchor='provider-' + str(provider.id))}"/>
            <rdfs:label>${provider.description}</rdfs:label>
        </dcterms:provenance>
        % endfor

        % for ma in ctx.macroareas:
        <dcterms:spatial rdf:parseType="Resource">
            <dcterms:description rdf:resource="${request.route_url('home.glossary', _anchor='macroarea-'+str(ma.id))}"/>
            <rdfs:label>${ma.name}</rdfs:label>
        </dcterms:spatial>
        % endfor
        % for dt in ctx.doctypes:
        <dc:type rdf:parseType="Resource">
            <dcterms:description rdf:resource="${request.route_url('home.glossary', _anchor='doctype-'+str(dt.id))}"/>
            <rdfs:label>${dt.name}</rdfs:label>
        </dc:type>
        % endfor
        """

    def __bibtex__(self):
        res = {}
        for attr in 'inlg inlg_code subject subject_headings keywords ozbib_id'.split():
            v = getattr(self, attr, None)
            if v:
                res[attr] = '%s' % v
        return res


class TreeClosureTable(Base):
    __table_args__ = (UniqueConstraint('parent_pk', 'child_pk'),)
    parent_pk = Column(Integer, ForeignKey('languoid.pk'))
    child_pk = Column(Integer, ForeignKey('languoid.pk'))
    depth = Column(Integer)


class LegacyCode(Base):
    id = Column(String, unique=True)


class LegacyRef(Base):
    id = Column(String, unique=True)
