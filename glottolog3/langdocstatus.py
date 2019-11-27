"""
Language Description Status Browser
-----------------------------------

The description status of languages can be investigated in relation to the vitality (or
endangerment) of a language.
"""
from collections import defaultdict, OrderedDict
import json

import attr
from pyramid.view import view_config
from sqlalchemy import func
from sqlalchemy.orm import aliased, joinedload
from clld.web.adapters.geojson import GeoJson
from clld.web.maps import Map, Layer, Legend
from clld.web.util.helpers import JS
from clld.web.util.htmllib import HTML
from clld.web.util.multiselect import MultiSelect
from clld.db.meta import DBSession
from clld.db.models import common
from clldutils import svg

from glottolog3.models import Languoid, LanguoidLevel, get_parameter, get_source
from glottolog3.maps import Language

CATEGORIES = ['Spoken L1 Language', 'Sign Language']


def ldstatus(ppk):
    sql = """\
select
  l.id, v.domainelement_pk, vs.source, l.jsondata::json->>'meds'
from
  language as l, languoid as ll, valueset as vs, value as v, parameter as p
where
  l.jsondata::json->>'meds' is not null and l.pk = vs.language_pk and vs.parameter_pk = p.pk
  and v.valueset_pk = vs.pk and vs.parameter_pk = {0}
  and ll.pk = l.pk and ll.category in ('Spoken L1 Language', 'Sign Language')
""".format(ppk)
    res = {}
    for lid, aespk, aes_source, meds in DBSession.execute(sql):
        meds = json.loads(meds)
        res[lid] = (aespk, meds[0] if meds else None, meds, aes_source)
    return res


@view_config(route_name='langdocstatus', renderer='langdocstatus/intro.mako')
def intro(req):
    def count(ppk):
        return DBSession.query(common.DomainElement.pk, func.count(common.Value.pk))\
            .join(common.Value)\
            .join(common.ValueSet)\
            .join(common.Language)\
            .filter(Languoid.category.in_(CATEGORIES))\
            .filter(common.DomainElement.parameter_pk == ppk)\
            .group_by(common.DomainElement.pk)

    med = get_parameter('med')
    aes = get_parameter('aes')
    return {
        'aes': aes,
        'med': med,
        'ref': get_source(aes.jsondata['reference_id']),
        'macroareas': get_parameter('macroarea').domain,
        'families': family_query(),
        'med_type_count': {pk: c for pk, c in count(med.pk)},
        'aes_status_count': {pk: c for pk, c in count(aes.pk)},
    }


def src2dict(s, med_map):
    res = dict(zip(['id', 'med_type', 'year', 'pages', 'name'], s))
    res['med_rank'] = med_map[res['med_type']].number
    return res


@attr.s
class Icon(object):
    shape = attr.ib()
    color = attr.ib()

    @classmethod
    def from_spec(cls, s):
        return cls(s[0], s[1:])


def get_icon_map():
    res = defaultdict(dict)
    for pid in ['aes', 'med']:
        for de in get_parameter(pid).domain:
            res[pid][de.id.split('-')[1]] = Icon.from_spec(de.jsondata['icon'])
    return res


class DescStatsGeoJson(GeoJson):
    def __init__(self, obj):
        GeoJson.__init__(self, obj)
        aes = get_parameter('aes')
        med = get_parameter('med')
        self.ldstatus = ldstatus(aes.pk)
        self.med_map = {
            de.id.split('-')[1]: (Icon.from_spec(de.jsondata['icon']), de)
            for de in med.domain}
        self.med_map[None] = self.med_map['wordlist_or_less']
        self.aes_map = {
            de.pk: (Icon.from_spec(de.jsondata['icon']), de) for de in aes.domain}

    def feature_iterator(self, ctx, req):
        for l in ctx:
            if l.id in self.ldstatus:
                yield l

    def featurecollection_properties(self, ctx, req):
        return {'layer': 'desc'}

    def get_icon(self, req, type_, aes_icon):
        icon = self.med_map[type_][0].shape + aes_icon.color
        if self.obj[2] == 'sdt':
            icon = aes_icon.shape + self.med_map[type_][0].color
        return self.obj[0][icon]

    def feature_properties(self, ctx, req, feature):
        aespk, med, sources, edsrc = self.ldstatus[feature.id]
        # augment the source dicts
        sources = [src2dict(v, {k: v[1] for k, v in self.med_map.items()}) for v in sources]
        for s in sources:
            s['icon'] = self.get_icon(req, s['med_type'], self.aes_map[aespk][0])
            s['sdt'] = self.med_map[s['med_type']][1].number

        med = src2dict(med, {k: v[1] for k, v in self.med_map.items()}) if med else med
        aes_icon, aes = self.aes_map[aespk]
        return {
            'ed': aes.number,
            'edsrc': edsrc,
            'icon': self.get_icon(req, med['med_type'] if med else None, aes_icon),
            'med': med['id'] if med else None,
            'sdt': self.med_map[med['med_type'] if med else None][1].number,
            'info_query': {'source': med['id']} if med else {},
            'red_icon': self.get_icon(req, None, aes_icon),
            'sources': sources}

    def get_language(self, ctx, req, feature):
        return Language(
            0, feature.name, feature.longitude, feature.latitude, feature.id)


class DescStatsMap(Map):
    def __init__(self, ctx, req, icon_map, focus, de_to_icon):
        self.icon_map = icon_map
        self.focus = focus
        self.de_to_icon = de_to_icon
        Map.__init__(self, ctx, req)

    def get_layers(self):
        yield Layer(
            'languoids',
            'Languoids',
            DescStatsGeoJson((self.icon_map, None, self.focus)).render(
                self.ctx, self.req, dump=False)
        )

    def get_options(self):
        return {
            'icon_size': 20,
            'hash': True,
            'max_zoom': 12,
            'on_init': JS('GLOTTOLOG3.LangdocStatus.update'),
            'no_showlabels': True}

    def get_legends(self):
        def img(spec):
            return HTML.img(
                src=svg.data_url(svg.icon(spec)), height='20', width='20', style='margin-left: 0.5em;')

        def desc(text):
            return HTML.span(text, style='margin-left: 0.5em; margin-right: 0.5em;')

        values = [desc('Most extensive description is a ...')]
        for sdt in get_parameter('med').domain:
            icon = self.de_to_icon['med'][sdt.id.split('-')[1]]
            values.append(
                HTML.label(
                    HTML.input(
                        type='checkbox',
                        checked='checked',
                        id='marker-toggle-sdt-' + str(sdt.number),
                        onclick='GLOTTOLOG3.LangdocStatus.toggleMarkers()'),
                    img(icon.shape + 'ffffff' if self.focus == 'ed' else 'c' + icon.color),
                    desc(sdt.name)))
        values.append(desc('Language is ...'))
        for ed in get_parameter('aes').domain:
            icon = self.de_to_icon['aes'][ed.id.split('-')[1]]
            values.append((
                HTML.label(
                    HTML.input(
                        type='checkbox',
                        checked='checked',
                        id='marker-toggle-ed-' + str(ed.number),
                        onclick='GLOTTOLOG3.LangdocStatus.toggleMarkers()'),
                    img('c' + icon.color if self.focus == 'ed' else icon.shape + 'ffffff'),
                    desc(ed.name.lower()))))
        yield Legend(self, 'values', values, label='Legend')


def language_query(req=None):
    query = DBSession.query(common.Language) \
        .filter(common.Language.active == True) \
        .filter(common.Language.latitude != None) \
        .filter(Languoid.level == LanguoidLevel.language) \
        .filter(Languoid.category.in_(CATEGORIES))
    if req:
        macroarea = req.params.get('macroarea')
        if macroarea:
            query = query.filter(Languoid.macroareas.contains(macroarea))
        families = [f for f in req.params.get('family', '').split(',') if f]
        if families:
            family = aliased(Languoid)
            query = query.join(family, Languoid.family_pk == family.pk)\
                .filter(family.id.in_(families))
        countries = []
        for c in req.params.getall('country'):
            countries.extend(c.split())
        if countries:
            query = query\
                .join(common.ValueSet)\
                .join(common.Parameter)\
                .join(common.Value)\
                .join(common.DomainElement)\
                .filter(common.Parameter.id == 'country')\
                .filter(common.DomainElement.name.in_(countries))

    return query


def family_query(req=None):
    query = DBSession.query(Languoid)\
        .filter(Languoid.father_pk == None)\
        .filter(common.Language.active == True)\
        .order_by(common.Language.name)
    if req:
        macroarea = req.params.get('macroarea')
        if macroarea:
            query = query.filter(Languoid.macroareas.contains(macroarea))
    return query


def _get_families(req):
    families = [f for f in req.params.get('family', '').split(',') if f]
    if families:
        return DBSession.query(Languoid).filter(Languoid.id.in_(families)).all()
    return []


@view_config(route_name='langdocstatus.browser', renderer='langdocstatus/browser.mako')
def browser(req):
    """
    The main GlottoScope view, with selection controls, map and tally table.
    """
    ms = MultiSelect(
        req, 'families', 'msfamily', collection=family_query(req), selected=_get_families(req))

    focus = req.params.get('focus', 'ed')

    im = get_icon_map()
    if focus == 'sdt':
        colors, shapes = im['med'], im['aes']
    else:
        shapes, colors = im['med'], im['aes']

    icon_map = {}
    for shape in [o.shape for o in shapes.values()]:
        for color in [o.color for o in colors.values()] + ['ffffff']:
            spec = shape + color
            icon_map[spec] = req.static_url('clld:web/static/icons/%s.png' % spec)

    countries = OrderedDict()
    for c in req.params.getall('country'):
        countries[c] = DBSession.query(common.DomainElement).join(common.Parameter)\
            .filter(common.Parameter.id == 'country')\
            .filter(common.DomainElement.name == c)\
            .one().description

    return {
        'families': ms,
        'macroareas': get_parameter('macroarea'),
        'countries': countries,
        'map': DescStatsMap(language_query(req), req, icon_map, focus, im),
        'icon_map': icon_map,
        'focus': focus,
        'doctypes': [
            (de, Icon.from_spec(de.jsondata['icon'])) for de in get_parameter('med').domain],
        'endangerments': [
            (de, Icon.from_spec(de.jsondata['icon'])) for de in get_parameter('aes').domain],
    }


@view_config(
    route_name='langdocstatus.languages', renderer='langdocstatus/language_table.mako')
def languages(req):
    """
    Called when cells in the tally table are clicked to load the corresponding languages.

    :param req:
    :return: list of (language, med) pairs with matching endangerment and doctype.
    """
    macroarea = req.params.get('macroarea')
    family = _get_families(req)
    year = req.params.get('year')

    demap = defaultdict(dict)
    for pid in ['aes', 'med']:
        for de in get_parameter(pid).domain:
            demap[pid][de.number] = de

    aes, aeslpks, med, medlpks = None, [], None, []

    label = 'Languages'
    if int(req.matchdict['ed']) in demap['aes']:
        aes = demap['aes'][int(req.matchdict['ed'])]
        label = HTML.em(aes.name) + ' languages'
        aeslpks = {
            v.valueset.language_pk for v in DBSession.query(common.Value)\
                .filter(common.Value.domainelement_pk == aes.pk)\
                .options(joinedload(common.Value.valueset))}

    if family:
        label = label + ' of the %s families' % ', '.join(f.name for f in family)

    if macroarea:
        label = label + ' from ' + macroarea

    if int(req.matchdict['sdt']) in demap['med']:
        med = demap['med'][int(req.matchdict['sdt'])]
        medlpks = {
            v.valueset.language_pk for v in DBSession.query(common.Value) \
                .filter(common.Value.domainelement_pk == med.pk) \
                .options(joinedload(common.Value.valueset))}

        label = label + ' whose most extensive description'

        if year:
            year = int(year)
            label = label + ' in %s' % year

        label = label + ' is a ' + med.name

    stats = ldstatus(get_parameter('aes').pk)
    langs = []
    for lang in language_query(req):
        if aes and lang.pk not in aeslpks:
            continue
        if not year and (med and lang.pk not in medlpks):
            continue

        aespk, med_, sources, _ = stats.get(lang.id, (None, None, [], None))
        gmed = None
        if year:
            drop = True
            for s in sources:
                s = src2dict(s, {v.id.split('-')[1]: v for v in demap['med'].values()})
                if s['year'] <= int(year):
                    gmed = s
                    if med and gmed['med_type'] == med.id.split('-')[1]:
                        drop = False
                    break
            if drop and med:
                continue
        else:
            gmed = med_
        langs.append((lang, gmed))

    return {'languages': sorted(langs, key=lambda l: l[0].name), 'label': label}
