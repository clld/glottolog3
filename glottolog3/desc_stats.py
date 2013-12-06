"""
Language Description Status Browser
-----------------------------------
"""
from collections import defaultdict
import json

from path import path
from clld.web.adapters.geojson import GeoJson, pacific_centered_coordinates
from clld.web.maps import Map, Layer, Legend
from clld.web.util.helpers import JS
from clld.web.util.htmllib import HTML
from clld.db.meta import DBSession

import glottolog3
from glottolog3.models import DOCTYPES, Languoid, Macroarea
from glottolog3.maps import Language


class SimplifiedDoctype(object):
    def __init__(self, ord_, name, color, color_extinct):
        self.ord = ord_
        self.name = name
        self.color = color
        self.color_extinct = color_extinct


SIMPLIFIED_DOCTYPES = [
    SimplifiedDoctype(i, *args) for i, args in enumerate([
        ('grammar', '00ff00', '006400'),
        ('grammar sketch', 'ff8040', 'd3d3d3'),
        ('phonology/text', 'ff4500', '708a90'),
        ('wordlist or less', 'ff0000', '000000'),
    ])
]

SIMPLIFIED_DOCTYPE_MAP = defaultdict(lambda: SIMPLIFIED_DOCTYPES[3])
for i, dt in enumerate(DOCTYPES):
    if i <= 1:
        SIMPLIFIED_DOCTYPE_MAP[i] = SIMPLIFIED_DOCTYPES[i]  # i.e. grammar or grammarsketch
        SIMPLIFIED_DOCTYPE_MAP[dt] = SIMPLIFIED_DOCTYPES[i]
    elif 1 < i < DOCTYPES.index('wordlist'):
        SIMPLIFIED_DOCTYPE_MAP[i] = SIMPLIFIED_DOCTYPES[2]
        SIMPLIFIED_DOCTYPE_MAP[dt] = SIMPLIFIED_DOCTYPES[2]


class DescStatsGeoJson(GeoJson):
    def feature_iterator(self, ctx, req):
        return ctx.values()

    def featurecollection_properties(self, ctx, req):
        return {'layer': 'desc'}

    def get_icon(self, type_, extinct=False):
        sdt = SIMPLIFIED_DOCTYPE_MAP[type_]
        return sdt.color_extinct if extinct else sdt.color

    def feature_properties(self, ctx, req, feature):
        # augment the source dicts
        for s in feature['sources']:
            s['icon'] = self.get_icon(s['doctype'])
            s['eicon'] = self.get_icon(s['doctype'], feature['extinct'])
            s['sdt'] = SIMPLIFIED_DOCTYPE_MAP[s['doctype']].ord

        med = feature['med']
        return {
            'extinct': feature['extinct'],
            'icon': self.get_icon(med['doctype'] if med else None),
            'eicon': self.get_icon(
                med['doctype'] if med else None, extinct=feature['extinct']),
            'med': med['id'] if med else None,
            'sdt': SIMPLIFIED_DOCTYPE_MAP[med['doctype'] if med else None].ord,
            'info_query': {'source': med['id']} if med else {},
            'red_icon': self.get_icon(None),
            'red_eicon': self.get_icon(None, extinct=feature['extinct']),
            'sources': feature['sources']}

    def get_language(self, ctx, req, feature):
        return Language(
            0, feature['name'], feature['longitude'], feature['latitude'], feature['id'])

    def get_coordinates(self, language):
        return pacific_centered_coordinates(language)


class DescStatsMap(Map):
    def get_layers(self):
        yield Layer(
            'languoids',
            'Languoids',
            DescStatsGeoJson(self.ctx).render(self.ctx, self.req, dump=False))

    def get_options(self):
        return {
            'icon_size': 20,
            'hash': True,
            'on_init': JS('GLOTTOLOG3.descStatsUpdate'),
            'no_showlabels': True}

    def get_legends(self):
        def img(color):
            return HTML.img(
                src=self.req.static_url('glottolog3:static/icons/c%s.png' % color),
                height='20',
                width='20',
                style='margin-left: 0.5em;')

        def desc(text):
            return HTML.span(text, style='margin-left: 0.5em; margin-right: 0.5em;')

        values = [desc('Most extensive description is a ...')]
        for sdt in SIMPLIFIED_DOCTYPES:
            values.append((img(sdt.color), img(sdt.color_extinct), desc(sdt.name)))
        yield Legend(self, 'values', values, label='Legend')


def _desc_stats_data(req):
    macroarea = req.params.get('macroarea')
    family = req.params.get('family')
    res = {}
    with open(path(glottolog3.__file__).dirname().joinpath('static', 'meds.json')) as fp:
        data = json.load(fp)
    for k, v in data.items():
        if (not macroarea or macroarea in v['macroareas'])\
                and (not family or v['family'] == family):
            res[k] = v
    return res


def desc_stats(req):
    family = req.params.get('family')
    if family:
        family = Languoid.get(family)
    return {
        'macroareas': DBSession.query(Macroarea).all(),
        'family': family,
        'map': DescStatsMap(_desc_stats_data(req), req), 'doctypes': SIMPLIFIED_DOCTYPES}


def desc_stats_languages(req):
    langs = []
    macroarea = req.params.get('macroarea')
    family = req.params.get('family')
    year = req.params.get('year')

    if req.matchdict['type'] in ['extinct', 'living']:
        label = req.matchdict['type'].capitalize() + ' languages'
    else:
        label = 'Languages'

    if family:
        family = Languoid.get(family)
        label = label + ' of the %s family' % family.name

    if macroarea:
        label = label + ' from ' + macroarea

    label = label + ' whose most extensive description'

    if year:
        year = int(year)
        label = label + ' in %s' % year

    label = label + ' is a ' + SIMPLIFIED_DOCTYPES[int(req.matchdict['index'])].name

    for lang in _desc_stats_data(req).values():
        if req.matchdict['type'] == 'living' and lang['extinct']:
            continue
        if req.matchdict['type'] == 'extinct' and not lang['extinct']:
            continue

        med = None
        if year:
            for s in lang['sources']:
                if s['year'] <= year:
                    med = s
                    break
        else:
            med = lang['med']

        sdt = SIMPLIFIED_DOCTYPE_MAP[med['doctype'] if med else None]
        if sdt.ord == int(req.matchdict['index']):
            langs.append((lang, med))

    return {'languages': sorted(langs, key=lambda l: l[0]['name']), 'label': label}
