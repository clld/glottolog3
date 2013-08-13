from __future__ import unicode_literals
import re

from purl import URL
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import joinedload, joinedload_all, aliased
from clld.web.datatables.base import DataTable, Col, LinkCol, DetailsRowLinkCol
from clld.web.util.helpers import button, JSModal, icon, link
from clld.web.util.htmllib import HTML
from clld.db.meta import DBSession
from clld.db.util import get_distinct_values, icontains
from clld.db.models.common import Language, LanguageSource
from clld.web.datatables.language import Languages
from clld.web.datatables.source import Sources

from glottolog3.models import (
    Macroarea, Languoidmacroarea, Languoid, TreeClosureTable,
    LanguoidLevel, LanguoidStatus, Provider, Refprovider, Refdoctype, Doctype, Ref,
)
from glottolog3.util import getRefs, get_params, languoid_link


class RefCountCol(Col):
    def format(self, item):
        return self.dt.ref_count[item.pk]


class Providers(DataTable):
    def __init__(self, req, model, **kw):
        self.ref_count = Refprovider.get_stats()
        super(Providers, self).__init__(req, Provider, **kw)

    def col_defs(self):
        return [
            Col(self, 'id'),
            Col(self, 'name'),
            RefCountCol(self, 'refs', bSortable=False, bSearchable=False),
            Col(self, 'description'),
        ]


class NameCol(Col):
    def format(self, item):
        return languoid_link(self.dt.req, item)


class StatusCol(Col):
    def __init__(self, dt, name='status', **kw):
        kw['sFilter'] = LanguoidStatus.established.value
        kw['choices'] = get_distinct_values(Languoid.status)
        super(StatusCol, self).__init__(dt, name, **kw)

    def search(self, qs):
        return Languoid.status == getattr(LanguoidStatus, qs, None)

    def order(self):
        return Languoid.status


class LevelCol(Col):
    def __init__(self, dt, name='level', **kw):
        kw['choices'] = ['Top-level family', 'Isolate', 'Top-level unit', 'Subfamily']
        kw['sFilter'] = 'Top-level unit'
        kw['bSortable'] = False
        super(LevelCol, self).__init__(dt, name, **kw)

    def format(self, item):
        if item.father_pk is None:
            if item.level == LanguoidLevel.family:
                return 'Top-level family'
            else:
                return 'Isolate'
        return 'Subfamily'

    def search(self, qs):
        if qs == 'Top-level family':
            return and_(Languoid.father_pk.__eq__(None),
                        Languoid.level == LanguoidLevel.family)
        if qs == 'Isolate':
            return and_(Languoid.father_pk.__eq__(None),
                        Languoid.level == LanguoidLevel.language)
        if qs == 'Top-level unit':
            return Languoid.father_pk.__eq__(None)
        if qs == 'Subfamily':
            return and_(Languoid.father_pk.__ne__(None),
                        Languoid.level == LanguoidLevel.family)


class MacroareaCol(Col):
    def __init__(self, dt, name, **kw):
        self.macroareas = DBSession.query(Macroarea).order_by(Macroarea.id).all()
        kw['bSortable'] = False
        desc = []
        for area in self.macroareas:
            desc.append(HTML.dt(u'%s' % area))
            desc.append(HTML.dd(area.description))
        kw['sDescription'] = HTML.span('see ', HTML.a('glossary', href=dt.req.route_url('home.glossary', _anchor='macroarea')))#HTML.dl(*desc)
        super(MacroareaCol, self).__init__(dt, name, **kw)

    def format(self, item):
        return ', '.join(a.name for a in item.macroareas)

    def search(self, qs):
        return Languoidmacroarea.macroarea_pk == int(qs)

    @property
    def choices(self):
        return [(a.pk, a.name) for a in self.macroareas]


class RefCol(Col):
    def format(self, item):
        return format_justifications(self.dt.req, item)


class IsoCol(Col):
    def format(self, item):
        if item.hid and len(item.hid) == 3:
            return item.hid

    def order(self):
        return Languoid.hid

    def search(self, qs):
        return Languoid.hid.contains(qs.lower())


class FamilyCol(Col):
    def format(self, item):
        if item.family_pk:
            return languoid_link(self.dt.req, item.family)

    def order(self):
        return self.dt.top_level_family.name

    def search(self, qs):
        return icontains(self.dt.top_level_family.name, qs)


class Families(Languages):
    def __init__(self, req, model, **kw):
        self.type = kw.pop('type', req.params.get('type', 'families'))
        self.top_level_family = aliased(Language)
        super(Families, self).__init__(req, model, **kw)

    def base_query(self, query):
        query = query.filter(Language.active == True)\
            .filter(Languoid.status == LanguoidStatus.established)\
            .outerjoin(Languoidmacroarea)\
            .outerjoin(self.top_level_family, self.top_level_family.pk == Languoid.family_pk)\
            .distinct()\
            .options(joinedload(Languoid.macroareas))

        if self.type == 'families':
            return query.filter(
                or_(Languoid.level == LanguoidLevel.family,
                    and_(Languoid.level == LanguoidLevel.language,
                         Languoid.father_pk == None)))
        else:
            return query.filter(Languoid.level == LanguoidLevel.language)

    def col_defs(self):
        if self.type == 'families':
            return [
                NameCol(self, 'name'),
                #StatusCol(self),
                LevelCol(self),
                MacroareaCol(self, 'macro-area'),
                Col(self, 'child_family_count', model_col=Languoid.child_family_count, sTitle='Sub-families'),
                Col(self, 'child_language_count', model_col=Languoid.child_language_count, sTitle='Child languages'),
                #Col(self, 'child_dialect_count', sTitle='Child dialects'),
                FamilyCol(self, 'top-level family'),
            ]
        else:
            return [
                Col(self, 'id', sTitle='Glottocode'),
                NameCol(self, 'name'),
                FamilyCol(self, 'top-level family'),
                IsoCol(self, 'iso', sTitle='ISO-639-3'),
                #StatusCol(self),
                MacroareaCol(self, 'macro-area'),
                Col(self, 'child_dialect_count', sTitle='Child dialects'),
            ]

    def get_options(self):
        opts = super(Families, self).get_options()
        opts['sAjaxSource'] = self.req.route_url('languages', _query={'type': self.type})
        if self.type == 'families':
            opts['aaSorting'] = [[4, 'desc'], [0, 'asc']]
        return opts


class DoctypeCol(Col):
    def __init__(self, dt, name, **kw):
        self.doctypes = DBSession.query(Doctype).order_by(Doctype.id).all()
        kw['bSortable'] = False
        super(DoctypeCol, self).__init__(dt, name, **kw)

    def format(self, item):
        return ', '.join(a.name for a in item.doctypes)

    def search(self, qs):
        return Refdoctype.doctype_pk == int(qs)

    @property
    def choices(self):
        return [(a.pk, a.name) for a in self.doctypes]


class Refs(Sources):
    def __init__(self, req, *args, **kw):
        if 'cq' in kw:
            self.complexquery = get_params(kw)
        elif 'cq' in req.params:
            self.complexquery = get_params(req.params)
        else:
            self.complexquery = None
        super(Refs, self).__init__(req, *args, **kw)

    def col_defs(self):
        cols = super(Refs, self).col_defs()
        if self.complexquery:
            cols = cols[:3]
        if self.language:
            cols.append(DoctypeCol(self, 'doctype'))
        return cols

    def base_query(self, query):
        if self.language:
            query = query.join(LanguageSource)\
                .join(TreeClosureTable, TreeClosureTable.child_pk == LanguageSource.language_pk)\
                .filter(TreeClosureTable.parent_pk == self.language.pk)
            query = query.outerjoin(Refdoctype, Ref.pk == Refdoctype.ref_pk)\
                .distinct()
        elif self.complexquery:
            query = getRefs(self.complexquery[0])
        return query

    def get_options(self):
        opts = super(Refs, self).get_options()
        if self.complexquery:
            query = {'cq': '1'}
            query.update(self.complexquery[1])
            opts['sAjaxSource'] = self.req.route_url('sources', _query=query)
        return opts
