from __future__ import unicode_literals

from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import aliased, joinedload
from clld.web.util.htmllib import HTML
from clld.db.meta import DBSession
from clld.db.util import get_distinct_values, icontains
from clld.db.models.common import Language, LanguageSource, Source
from clld.web.datatables.base import DataTable, Col, DetailsRowLinkCol, LinkCol
from clld.web.datatables.language import Languages
from clld.web.datatables.source import Sources
from clld.web.util.helpers import icon

from glottolog3.models import (
    Macroarea, Languoidmacroarea, Languoid, TreeClosureTable,
    LanguoidLevel, LanguoidStatus, Provider, Refprovider, Doctype, Ref,
)
from glottolog3.util import getRefs, get_params, languoid_link, format_ca_icon


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
    def __init__(self, dt, name, **kw):
        kw['sFilter'] = LanguoidStatus.established.value
        kw['choices'] = get_distinct_values(Languoid.status)
        super(StatusCol, self).__init__(dt, name, **kw)

    def search(self, qs):
        return Languoid.status == getattr(LanguoidStatus, qs, None)

    def order(self):
        return Languoid.status


class LevelCol(Col):
    __kw__ = dict(
        choices=['Top-level family', 'Isolate', 'Top-level unit', 'Subfamily'],
        sFilter='Top-level unit',
        bSortable=False)

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
        kw['sDescription'] = HTML.span(
            'see ',
            HTML.a('glossary',
                   href=dt.req.route_url('home.glossary', _anchor='macroarea')))
        super(MacroareaCol, self).__init__(dt, name, **kw)

    def format(self, item):
        return ', '.join(a.name for a in item.macroareas)

    def search(self, qs):
        return Languoidmacroarea.macroarea_pk == int(qs)

    @property
    def choices(self):
        return [(a.pk, a.name) for a in self.macroareas]


class IsoCol(Col):
    def format(self, item):
        if item.hid and len(item.hid) == 3:
            return item.hid

    def order(self):
        return Languoid.hid

    def search(self, qs):
        iso_like = Languoid.hid.op('~')('^[a-z]{3}$')
        return and_(Languoid.hid.contains(qs.lower()), iso_like)


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
        self.type = kw.pop('type', req.params.get('type', 'languages'))
        self.top_level_family = aliased(Language)
        super(Families, self).__init__(req, model, **kw)

    def default_order(self):
        return desc(Language.created)

    def base_query(self, query):
        query = query.filter(Language.active == True)\
            .filter(Languoid.status == LanguoidStatus.established)\
            .outerjoin(Languoidmacroarea)\
            .outerjoin(self.top_level_family, self.top_level_family.pk == Languoid.family_pk)\
            .distinct()\
            .options(joinedload(Languoid.macroareas), joinedload(Languoid.family))

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
                LevelCol(self, 'level'),
                MacroareaCol(self, 'macro-area'),
                Col(self, 'child_family_count', model_col=Languoid.child_family_count, sTitle='Sub-families'),
                Col(self, 'child_language_count', model_col=Languoid.child_language_count, sTitle='Child languages'),
                FamilyCol(self, 'top-level family'),
            ]
        return [
            Col(self, 'id', sTitle='Glottocode'),
            NameCol(self, 'name'),
            FamilyCol(self, 'top-level family'),
            IsoCol(self, 'iso', sTitle='ISO-639-3'),
            MacroareaCol(self, 'macro-area'),
            Col(self, 'child_dialect_count', sTitle='Child dialects', sClass='right'),
            Col(self, 'latitude'),
            Col(self, 'longitude'),
        ]

    def get_options(self):
        opts = super(Families, self).get_options()
        opts['sAjaxSource'] = self.req.route_url('languages', _query={'type': self.type})
        if self.type == 'families':
            opts['aaSorting'] = [[4, 'desc'], [0, 'asc']]
        return opts


#
# Refs
#
class _CollectionCol(Col):
    cls = None
    attr = None
    route = None

    def __init__(self, dt, name, **kw):
        self.collection = DBSession.query(self.cls).order_by(self.cls.id).all()
        self.collection_dict = {o.id: o for o in self.collection}
        kw['bSortable'] = False
        super(_CollectionCol, self).__init__(dt, name, **kw)

    def link(self, id_):
        if not id_:
            return ''
        return HTML.a(
            id_,
            title=self.collection_dict[id_].name,
            href=self.dt.req.route_url(
                self.route, _anchor='%s-%s' % (self.cls.mapper_name().lower(), id_)))

    def format(self, item):
        return ', '.join(filter(None, map(self.link, (getattr(item, self.attr) or '').split(', '))))

    def search(self, qs):
        return getattr(Ref, self.attr).contains(qs)

    @property
    def choices(self):
        return [o.id for o in self.collection]


class DoctypeCol(_CollectionCol):
    cls = Doctype
    attr = 'doctypes_str'
    route = 'home.glossary'


class ProviderCol(_CollectionCol):
    cls = Provider
    attr = 'providers_str'
    route = 'providers'


class CaCol(Col):
    def __init__(self, dt, name, **kw):
        kw['bSearchable'] = False
        kw['sTitle'] = 'ca'
        kw['sDescription'] = 'computerized assignment of ' + name[3:]
        self.attr = '%s_trigger' % name
        super(CaCol, self).__init__(dt, name, **kw)

    def order(self):
        return getattr(Ref, self.attr)

    def format(self, item):
        return format_ca_icon(self.dt.req, item, self.attr.split('_')[1])


class DirectAssignmentCol(Col):
    def format(self, item):
        if item.pk in self.dt.language_sources:
            return icon('tag')
        return ''


class Refs(Sources):
    def __init__(self, req, *args, **kw):
        if 'cq' in kw:
            self.complexquery = get_params(kw)
        elif 'cq' in req.params:
            self.complexquery = get_params(req.params)
        else:
            self.complexquery = None
        super(Refs, self).__init__(req, *args, **kw)
        if self.language:
            self.language_sources = [s.pk for s in self.language.sources]

    def default_order(self):
        return desc(Source.updated)

    def col_defs(self):
        cols = [
            DetailsRowLinkCol(self, 'd'),
            LinkCol(self, 'name'),
            Col(self, 'description', sTitle='Title'),
            CaCol(self, 'ca_language'),
        ]

        if not self.complexquery:
            cols.append(Col(self, 'year', model_col=Source.year_int))
            cols.append(Col(self, 'pages', model_col=Source.pages_int))

        cols.append(DoctypeCol(self, 'doctype'))
        cols.append(CaCol(self, 'ca_doctype'))
        cols.append(ProviderCol(self, 'provider'))
        if self.language:
            cols.append(DirectAssignmentCol(
                self, 'd',
                sTitle='da',
                sDescription="Signals whether the reference is directly assigned to this languoid or inherited from daughter languoids.",
                bSortable=False,
                bSearchable=False))
        return cols

    def base_query(self, query):
        if self.language:
            query = query.join(LanguageSource)\
                .join(TreeClosureTable,
                      TreeClosureTable.child_pk == LanguageSource.language_pk)\
                .filter(TreeClosureTable.parent_pk == self.language.pk)\
                .distinct()
        elif self.complexquery:
            query = getRefs(self.complexquery[0])
        return query

    def xhr_query(self):
        query = super(Refs, self).xhr_query() or {}
        if self.complexquery:
            query['cq'] = '1'
            query.update(self.complexquery[1])
        return query


def includeme(config):
    config.register_datatable('providers', Providers)
    config.register_datatable('languages', Families)
    config.register_datatable('sources', Refs)
