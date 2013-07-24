from __future__ import unicode_literals

from sqlalchemy import func, or_, and_
from sqlalchemy.orm import joinedload, joinedload_all
from clld.web.datatables.base import DataTable, Col, LinkCol
from clld.web.util.helpers import button, JSModal, icon, link
from clld.web.util.htmllib import HTML
from clld.db.meta import DBSession
from clld.db.util import get_distinct_values, icontains
from clld.db.models.common import Language
from clld.web.datatables.language import Languages as BaseTable

from glottolog3.models import (
    Macroarea, Languoidmacroarea, Languoid, TreeClosureTable, Justification,
    LanguoidLevel, LanguoidStatus,
)
#from glottolog2.lib.util import top_node_query, link, format_justifications


class NameCol(Col):
    def format(self, item):
        return link(self.dt.req, item)


class LevelCol(Col):
    def __init__(self, dt, name, **kw):
        kw['choices'] = ['Top-level family', 'Isolate', 'Top-level unit', 'Subfamily']
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


class RefsLinkCol(Col):
    def format(self, item):
        return button(
            #
            # TODO
            #
            #icon('icon-list'), href=self.dt.req.route_url(
            #    'langdoc.complexquery', _query=dict(languoids='(%s)' % item.id)),
            title='show all references for any languoid in %s' % item.name)


class IsoCol(Col):
    def format(self, item):
        if item.hid and len(item.hid) == 3:
            return item.hid

    def order(self):
        return Languoid.hid

    def search(self, qs):
        return Languoid.hid.contains(qs.lower())


class Families(BaseTable):
    def __init__(self, req, model, **kw):
        self.type = kw.pop('type', req.params.get('type', 'families'))
        super(Families, self).__init__(req, model, **kw)

    def base_query(self, query):
        query = query.filter(Language.active == True)\
            .outerjoin(Languoidmacroarea)\
            .distinct()\
            .options(
                joinedload(Languoid.macroareas),
                joinedload_all(Languoid.justifications, Justification.source))

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
                Col(self, 'status', sFilter=LanguoidStatus.established.value,
                    choices=get_distinct_values(Languoid.status)),
                #Col(self, 'level', sFilter='family',
                #    choices=get_distinct_values(Languoid.level)),
                #Col(self, 'active', sFilter='True'),
                LevelCol(self, 'level', bSortable=False),
                MacroareaCol(self, 'macro-area'),
                RefsLinkCol(self, 'refs', bSearchable=False, bSortable=False),
                Col(self, 'child_family_count', sTitle='Sub-families'),
                Col(self, 'child_language_count', sTitle='Child languages'),
                #Col(self, 'child_dialect_count', sTitle='Child dialects'),
            ]
        else:
            return [
                Col(self, 'id', sTitle='Glottocode'),
                NameCol(self, 'name'),
                IsoCol(self, 'iso', sTitle='ISO-639-3'),
                Col(self, 'status', sFilter='established',
                    choices=get_distinct_values(Languoid.status)),
                #Col(self, 'level', sFilter='language',
                #    choices=get_distinct_values(Languoid.level)),
                MacroareaCol(self, 'macro-area'),
                Col(self, 'child_dialect_count', sTitle='Child dialects'),
            ]

    def get_options(self):
        opts = super(Families, self).get_options()
        opts['sAjaxSource'] = self.req.route_url('languages', _query={'type': self.type})
        return opts
