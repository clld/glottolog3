from json import dumps
import re
from itertools import cycle

from sqlalchemy import or_, not_
from sqlalchemy.orm import joinedload, joinedload_all
from sqlalchemy.sql.expression import func
from pyramid.httpexceptions import HTTPFound

from clld.db.meta import DBSession
from clld.db.models.common import (
    Identifier, LanguageIdentifier, IdentifierType, Language, Source,
)
from clld.web.util.helpers import link
from clld.web.util.htmllib import HTML
from clld.web.icon import SHAPES
from clld.interfaces import IIcon

from glottolog3.models import Country, Languoid, Languoidcountry, Refprovider, Provider
from glottolog3.maps import LanguoidsMap


REF_PATTERN = re.compile('\*\*(?P<id>[0-9]+)\*\*')


#def provider_detail_html(request=None, **kw):
#    raise HTTPFound(request.route_url('providers', _anchor='provider-' + request.matchdict['id']))

def provider_index_html(request=None, **kw):
    return {
        'providers': DBSession.query(Provider),
        'totalrefs': DBSession.query(Source).count(),
        'totalnodes': DBSession.query(Language).count(),
    }


def format_classificationcomment(req, comment):
    parts = []
    pos = 0
    for match in REF_PATTERN.finditer(comment):
        preceding = comment[pos:match.start()]
        parts.append(preceding)
        preceding_words = preceding.strip().split()
        if preceding_words and preceding_words[-1] not in ['in', 'of', 'per', 'by']:
            parts.append('(')
        parts.append(link(req, Source.get(match.group('id'))))
        if preceding_words and preceding_words[-1] not in ['in', 'of', 'per', 'by']:
            parts.append(')')
        pos = match.end()
    parts.append(comment[pos:])
    return HTML.p(*parts)


def format_justifications(req, refs):
    r = []
    for ref in refs:
        label = ref.source.name
        if ref.description:
            label += '[%s]' % ref.description
        r.append(HTML.li(link(req, ref.source, label=label)))
    return HTML.ul(*r)


def getLanguoids(name=False,
                 iso=False,
                 namequerytype='part',
                 country=False,
                 multilingual=False):
    """return an array of languoids responding to the specified criterion.
    """
    if not (name or iso or country):
        return []

    query = DBSession.query(Languoid)\
        .options(joinedload(Language.languagesource))\
        .order_by(Languoid.name)

    if name:
        namequeryfilter = {
            "regex": func.lower(Identifier.name).like(name.lower()),
            "part": func.lower(Identifier.name).contains(name.lower()),
            "whole": func.lower(Identifier.name) == name.lower(),
        }[namequerytype if namequerytype in ('regex', 'whole') else 'part']

        query = query.join(LanguageIdentifier, Identifier)\
            .filter(Identifier.type == 'name')\
            .filter(namequeryfilter)
        if not multilingual:
            query = query.filter(or_(
                Identifier.lang.in_((u'', u'eng', u'en')), Identifier.lang == None))
    elif country:
        alpha2 = country.split('(')[1].split(')')[0] if len(country) > 2 else country.upper()
        query = query.join(Languoidcountry).join(Country)\
            .filter(Country.id == alpha2)
    else:
        query = query.join(LanguageIdentifier, Identifier)\
            .filter(Identifier.name.contains(iso.lower()))\
            .filter(Identifier.type == IdentifierType.iso.value)

    return query


def language_index_html(request=None, **kw):
    res = dict(
        countries=dumps([
            '%s (%s)' % (c.name, c.id) for c in
            DBSession.query(Country).order_by(Country.description)]),
        params={
            'name': '',
            'iso': '',
            'namequerytype': 'part',
            'country': ''})

    for param, default in res['params'].items():
        res['params'][param] = request.params.get(param, default).strip()

    res['params']['multilingual'] = 'multilingual' in request.params

    if request.params.get('alnum'):
        raise HTTPFound(location=request.route_url(
            'language', id=request.params['alnum']))

    languoids = list(getLanguoids(**res['params']))
    map_ = LanguoidsMap(languoids, request)
    layer = list(map_.get_layers())[0]
    if not layer.data['features']:
        map_ = None
    res.update(map=map_, languoids=languoids)
    return res


COLORS = [
    #            red     yellow
    "00ff00", "ff0000", "ffff00", "0000ff", "ff00ff", "00ffff", "000000",
]


def language_detail_html(request=None, context=None, **kw):
    icon_map = dict(
        zip([context.pk] + [l.pk for l in context.children],
            cycle([s + c for s in SHAPES for c in COLORS])))
    for key in icon_map:
        icon_map[key] = request.registry.getUtility(IIcon, icon_map[key]).url(request)
    return dict(icon_map=icon_map)
