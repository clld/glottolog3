from json import dumps

from sqlalchemy import or_, not_
from sqlalchemy.orm import joinedload, joinedload_all
from sqlalchemy.sql.expression import func
from pyramid.httpexceptions import HTTPFound

from clld.db.meta import DBSession
from clld.db.models.common import (
    Identifier, LanguageIdentifier, IdentifierType, Language,
)

from glottolog3.models import Country, Languoid, Languoidcountry
from glottolog3.maps import LanguoidsMap


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
