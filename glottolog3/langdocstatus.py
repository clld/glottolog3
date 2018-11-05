"""
Language Description Status Browser
-----------------------------------

The description status of languages can be investigated in relation to the vitality (or
endangerment) of a language.
"""
from collections import defaultdict, namedtuple, Counter
from math import ceil
from functools import total_ordering

from pyramid.view import view_config
from sqlalchemy.orm import aliased, joinedload
from clld.web.adapters.geojson import GeoJson
from clld.web.maps import Map, Layer, Legend
from clld.web.util.helpers import JS
from clld.web.util.htmllib import HTML
from clld.web.util.multiselect import MultiSelect
from clld.db.meta import DBSession
from clld.db.models import common
from clldutils.jsonlib import load
from clldutils.path import Path

import glottolog3
from glottolog3.models import (
    DOCTYPES, Languoid, Macroarea, Languoidmacroarea, LanguoidLevel, Ref, Doctype,
)
from glottolog3.maps import Language


def ldstatus():
    return load(Path(glottolog3.__file__).parent.joinpath('static', 'ldstatus.json'))


@view_config(route_name='langdocstatus', renderer='langdocstatus/intro.mako')
def intro(req):
    lds = ldstatus()
    count, i = Counter(), 0
    for i, (lid, spec) in enumerate(lds.items()):
        count.update([SIMPLIFIED_DOCTYPE_MAP[spec[0][1] if spec[0] else None].ord])
    return {
        'macroareas': DBSession.query(Macroarea).order_by(Macroarea.name),
        'families': family_query().options(joinedload(Languoid.macroareas)),
        'sdts': [(sdt, count[sdt.ord], i + 1) for sdt in SIMPLIFIED_DOCTYPES],
        'doctypes': [(dt, SIMPLIFIED_DOCTYPE_MAP[dt.id].ord)
                     for dt in DBSession.query(Doctype).order_by(Doctype.ord)],
    }


SimplifiedDoctype = namedtuple('SimplifiedDoctype', 'ord name shape color')
SIMPLIFIED_DOCTYPES = [
    SimplifiedDoctype(i, *args) for i, args in enumerate([
        ('long grammar', 'c', '00ff00'),  # long grammar & extensive description of most elements of the grammar $\approx 300+$ pages
        ('grammar', 's', 'a0fb75'),  # grammar & a description of most elements of the grammar ($\approx 150$ pages) &
        ('grammar sketch', 'd', 'ff6600'),  # grammar sketch & a less extensive description of many elements of the grammar ($\approx 50$ pages)
        ('phonology/text', 't', 'ff4400'),  #
        ('wordlist or less', 'f', 'ff0000'),
    ])
]
SIMPLIFIED_DOCTYPE_MAP = defaultdict(lambda: SIMPLIFIED_DOCTYPES[4])
SIMPLIFIED_DOCTYPE_MAP[-1] = SIMPLIFIED_DOCTYPES[0]
SIMPLIFIED_DOCTYPE_MAP['long_grammar'] = SIMPLIFIED_DOCTYPES[0]
for i, dt in enumerate(DOCTYPES):
    if i <= 1:
        SIMPLIFIED_DOCTYPE_MAP[i] = SIMPLIFIED_DOCTYPES[i + 1]  # i.e. grammar or grammarsketch
        SIMPLIFIED_DOCTYPE_MAP[dt] = SIMPLIFIED_DOCTYPES[i + 1]
    elif 1 < i < DOCTYPES.index('wordlist'):
        SIMPLIFIED_DOCTYPE_MAP[i] = SIMPLIFIED_DOCTYPES[3]
        SIMPLIFIED_DOCTYPE_MAP[dt] = SIMPLIFIED_DOCTYPES[3]

Endangerment = namedtuple('Endangerment', 'ord name color shape')
ENDANGERMENTS = [
    Endangerment(i, *args) for i, args in enumerate([
        ('not endangered', '00ff00', 'c'),
        ('threatened', 'a0fb75', 'c'),
        ('shifting', 'ff6600', 's'),
        ('moribund', 'ff4400', 'd'),
        ('nearly extinct', 'ff0000', 't'),
        ('extinct', '000000', 'f'),
    ])
]

ENDANGERMENT_MAP = defaultdict(
    lambda: ENDANGERMENTS[0], [(ed.name, ed) for ed in ENDANGERMENTS])


def src2dict(s):
    return dict(zip(['id', 'doctype', 'year', 'pages', 'name'], s))


class DescStatsGeoJson(GeoJson):
    def feature_iterator(self, ctx, req):
        return ctx

    def featurecollection_properties(self, ctx, req):
        return {'layer': 'desc'}

    def get_icon(self, req, type_, endangerment):
        icon = SIMPLIFIED_DOCTYPE_MAP[type_].shape + endangerment.color
        if self.obj[2] == 'sdt':
            icon = endangerment.shape + SIMPLIFIED_DOCTYPE_MAP[type_].color
        return self.obj[0][icon]

    def feature_properties(self, ctx, req, feature):
        endangerment = ENDANGERMENT_MAP[feature.status.description]
        med, sources, edsrc = self.obj[1].get(feature.id, (None, [], None))
        # augment the source dicts
        sources = [src2dict(v) for v in sources]
        for s in sources:
            s['icon'] = self.get_icon(req, s['doctype'], endangerment)
            s['sdt'] = SIMPLIFIED_DOCTYPE_MAP[s['doctype']].ord

        med = src2dict(med) if med else med
        return {
            'ed': endangerment.ord,
            'edsrc': edsrc,
            'icon': self.get_icon(req, med['doctype'] if med else None, endangerment),
            'med': med['id'] if med else None,
            'sdt': SIMPLIFIED_DOCTYPE_MAP[med['doctype'] if med else None].ord,
            'info_query': {'source': med['id']} if med else {},
            'red_icon': self.get_icon(req, None, endangerment),
            'sources': sources}

    def get_language(self, ctx, req, feature):
        return Language(
            0, feature.name, feature.longitude, feature.latitude, feature.id)


class DescStatsMap(Map):
    def __init__(self, ctx, req, icon_map, focus):
        self.ldstatus = ldstatus()
        self.icon_map = icon_map
        self.focus = focus
        Map.__init__(self, ctx, req)

    def get_layers(self):
        yield Layer(
            'languoids',
            'Languoids',
            DescStatsGeoJson((self.icon_map, self.ldstatus, self.focus)).render(
                self.ctx, self.req, dump=False))

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
                src=self.icon_map[spec], height='20', width='20', style='margin-left: 0.5em;')

        def desc(text):
            return HTML.span(text, style='margin-left: 0.5em; margin-right: 0.5em;')

        values = [desc('Most extensive description is a ...')]
        for sdt in SIMPLIFIED_DOCTYPES:
            values.append(
                HTML.label(
                    HTML.input(
                        type='checkbox',
                        checked='checked',
                        id='marker-toggle-sdt-' + str(sdt.ord),
                        onclick='GLOTTOLOG3.LangdocStatus.toggleMarkers()'),
                    img(sdt.shape + 'ffffff' if self.focus == 'ed' else 'c' + sdt.color),
                    desc(sdt.name)))
        values.append(desc('Language is ...'))
        for ed in ENDANGERMENTS:
            values.append((
                HTML.label(
                    HTML.input(
                        type='checkbox',
                        checked='checked',
                        id='marker-toggle-ed-' + str(ed.ord),
                        onclick='GLOTTOLOG3.LangdocStatus.toggleMarkers()'),
                    img('c' + ed.color if self.focus == 'ed' else ed.shape + 'ffffff'),
                    desc(ed.name.lower()))))
        yield Legend(self, 'values', values, label='Legend')


def language_query(req=None):
    query = DBSession.query(common.Language) \
        .filter(common.Language.active == True) \
        .filter(common.Language.latitude != None) \
        .filter(Languoid.level == LanguoidLevel.language)
    if req:
        macroarea = req.params.get('macroarea')
        if macroarea:
            query = query.join(Languoidmacroarea).join(Macroarea)\
                .filter(Macroarea.name == macroarea)
        families = [f for f in req.params.get('family', '').split(',') if f]
        if families:
            family = aliased(Languoid)
            query = query.join(family, Languoid.family_pk == family.pk)\
                .filter(family.id.in_(families))

    return query


def family_query(req=None):
    query = DBSession.query(Languoid)\
        .filter(Languoid.father_pk == None)\
        .filter(common.Language.active == True)\
        .order_by(common.Language.name)
    if req:
        macroarea = req.params.get('macroarea')
        if macroarea:
            query = query.join(Languoidmacroarea).join(Macroarea)\
                .filter(Macroarea.name == macroarea)
    return query


def _get_families(req):
    families = [f for f in req.params.get('family', '').split(',') if f]
    if families:
        return DBSession.query(Languoid).filter(Languoid.id.in_(families)).all()
    return []


@view_config(route_name='langdocstatus.browser', renderer='langdocstatus/browser.mako')
def browser(req):
    ms = MultiSelect(
        req, 'families', 'msfamily', collection=family_query(req), selected=_get_families(req))

    focus = req.params.get('focus', 'ed')
    if focus == 'sdt':
        colors, shapes = SIMPLIFIED_DOCTYPES, ENDANGERMENTS
    else:
        shapes, colors = SIMPLIFIED_DOCTYPES, ENDANGERMENTS
    icon_map = {}
    for shape in [o.shape for o in shapes]:
        for color in [o.color for o in colors] + ['ffffff']:
            spec = shape + color
            icon_map[spec] = req.static_url('clld:web/static/icons/%s.png' % spec)

    return {
        'families': ms,
        'macroareas': DBSession.query(Macroarea).all(),
        'map': DescStatsMap(language_query(req), req, icon_map, focus),
        'icon_map': icon_map,
        'focus': focus,
        'doctypes': SIMPLIFIED_DOCTYPES,
        'endangerments': ENDANGERMENTS}


@view_config(
    route_name='langdocstatus.languages', renderer='langdocstatus/language_table.mako')
def languages(req):
    """
    :param req:
    :return: list of (language, med) pairs with matching endangerment and doctype.
    """
    langs = []
    macroarea = req.params.get('macroarea')
    family = _get_families(req)
    year = req.params.get('year')

    label = 'Languages'
    try:
        ed = ENDANGERMENTS[int(req.matchdict['ed'])]
        label = HTML.em(ed.name) + ' languages'
    except IndexError:
        ed = None

    if family:
        label = label + ' of the %s families' % ', '.join(f.name for f in family)

    if macroarea:
        label = label + ' from ' + macroarea

    try:
        sdt = SIMPLIFIED_DOCTYPES[int(req.matchdict['sdt'])]
    except IndexError:
        sdt = None

    if sdt:
        label = label + ' whose most extensive description'

        if year:
            year = int(year)
            label = label + ' in %s' % year

        label = label + ' is a ' + sdt.name

    stats = ldstatus()
    for lang in language_query(req):
        if ed:
            _ed = lang.status.description
            if ed.name != _ed:
                continue

        med_, sources, _ = stats.get(lang.id, (None, [], None))
        med = None
        if year:
            for s in sources:
                s = src2dict(s)
                if s['year'] <= int(year):
                    med = s
                    break
        else:
            med = med_

        if sdt:
            _sdt = SIMPLIFIED_DOCTYPE_MAP[med['doctype'] if med else None]
            if _sdt.ord != sdt.ord:
                continue

        langs.append((lang, med))

    return {'languages': sorted(langs, key=lambda l: l[0].name), 'label': label}


@total_ordering
class Source(object):
    """Representation of a source amenable to computation of MEDs
    (Most Extensive Description)
    """
    def __init__(self, source, lcount):
        assert lcount
        self.index = len(DOCTYPES)
        self.doctype = None

        for doctype in source.doctypes:
            doctype = doctype.id
            if doctype and DOCTYPES.index(doctype) < self.index:
                self.index = DOCTYPES.index(doctype)
                self.doctype = doctype

        # the number of pages is divided by number of doctypes times number of
        # described languages
        self.pages = int(ceil(
            float(source.pages_int or 0) / ((len(source.doctypes) or 1) * lcount)))

        if self.doctype == 'grammar' and self.pages >= 300:
            self.doctype = 'long_grammar'
            self.index = -1

        self.year = source.year_int
        self.id = source.id
        self.name = source.name

    def __json__(self):
        return [getattr(self, k) for k in 'id doctype year pages name'.split()]

    def __hash__(self):
        return int(self.id)

    @property
    def weight(self):
        """This is the algorithm:
        "more extensive" means: better doctype (i.e. lower index) or more pages or newer.

        Thus, a sorted list of Sources will have the MED as first element.
        """
        return self.index, -self.pages, -(self.year or 0), int(self.id)

    def __eq__(self, other):
        return self.weight == other.weight

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self.weight < other.weight


def extract_data(endangerment):  # pragma: no cover
    status = {}
    lpks = DBSession.query(common.Language.pk) \
        .filter(common.Language.active == True) \
        .filter(common.Language.latitude != None) \
        .filter(Languoid.level == LanguoidLevel.language) \
        .order_by(common.Language.pk).all()
    print(len(lpks))

    sql = """\
select ls.source_pk, count(ls.language_pk) from languagesource as ls, ref as r 
where ls.source_pk = r.pk and r.ca_doctype_trigger is null and r.ca_language_trigger is null 
group by source_pk 
    """
    lcounts = {r[0]: r[1] for r in DBSession.execute(sql)}

    # loop over active, established languages with geo-coords
    for i, lpk in enumerate(lpks):
        l = DBSession.query(common.Language).filter(common.Language.pk == lpk).one()
        # let's collect the relevant sources in a way that allows computation of med.
        # Note: we limit refs to the ones without computerized assignments.
        sources = list(DBSession.query(Ref).join(common.LanguageSource) \
                       .filter(common.LanguageSource.language_pk == lpk) \
                       .filter(Ref.ca_doctype_trigger == None) \
                       .filter(Ref.ca_language_trigger == None) \
                       .options(joinedload(Ref.doctypes)))
        sources = sorted([Source(s, lcounts.get(s.pk, 0)) for s in sources])

        # keep the overall med
        # note: this source may not be included in the potential meds computed
        # below,
        # e.g. because it may not have a year.
        med = sources[0].__json__() if sources else None

        # now we have to compute meds respecting a cut-off year.
        # to do so, we collect eligible sources per year and then
        # take the med of this collection.
        potential_meds = []

        # we only have to loop over publication years within all sources, because
        # only in these years something better might have come along.
        for year in set(s.year for s in sources if s.year):
            # let's see if something better was published!
            eligible = [s for s in sources if s.year and s.year <= year]
            if eligible:
                potential_meds.append(sorted(eligible)[0])

        # we store the precomputed sources information as jsondata:
        status[l.id] = [
            med,
            [s.__json__() for s in
             sorted(set(potential_meds), key=lambda s: -s.year)],
            endangerment.get(l.id, {}).get('source')
        ]
        if i and i % 1000 == 0:
            print(i)
            DBSession.close()

    return status
