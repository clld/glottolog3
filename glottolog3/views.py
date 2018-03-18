from datetime import date
import re
import json
from collections import OrderedDict

from pyramid.httpexceptions import (
    HTTPNotAcceptable, HTTPNotFound, HTTPFound, HTTPMovedPermanently,
)
from pyramid.view import view_config
from sqlalchemy import and_, true, false, null, or_, exc
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import joinedload
from clld.db.meta import DBSession
from clld.db.models.common import (
    Language, Source, LanguageIdentifier, Identifier, IdentifierType,
)
from clld.db.util import icontains
from clld.web.util.helpers import JS
from clld.web.util.htmllib import HTML
from clld.web.util.multiselect import MultiSelect
from clld.lib import bibtex
from clld.interfaces import IRepresentation
from clldutils.misc import slug

from glottolog3.models import (
    Languoid, LanguoidStatus, LanguoidLevel, Macroarea, Doctype, Refprovider,
    TreeClosureTable, BOOKKEEPING,
)
from glottolog3.config import CFG
from glottolog3.util import getRefs, get_params
from glottolog3.datatables import Refs
from glottolog3.models import Country, SPECIAL_FAMILIES
from glottolog3.adapters import get_selected_languages_map


YEAR_PATTERN = re.compile('[0-9]{4}$')

GLOTTOCODE_PATTERN = re.compile('[a-z][a-z0-9]{3}[1-9]\d{3}$')


class LanguoidsMultiSelect(MultiSelect):
    def format_result(self, l):
        return dict(id=l.id, text=l.name, level=l.level.value)

    def get_options(self):
        opts = super(LanguoidsMultiSelect, self).get_options()
        opts['formatResult'] = JS('GLOTTOLOG3.formatLanguoid')
        opts['formatSelection'] = JS('GLOTTOLOG3.formatLanguoid')
        return opts


def iso(request):
    q = DBSession.query(Languoid).join(LanguageIdentifier).join(Identifier)\
        .filter(Identifier.type == IdentifierType.iso.value)\
        .filter(Identifier.name == request.matchdict['id']).first()
    if not q:
        return HTTPNotFound()
    params = {}
    if 'ext' in request.matchdict:
        params['ext'] = request.matchdict['ext']
    return HTTPFound(location=request.resource_url(q, **params))


def glottologmeta(request):
    q = DBSession.query(Languoid)
    qt = q.filter(Languoid.father_pk == null())
    res = {
        'last_update': DBSession.query(Language.updated)
        .order_by(Language.updated.desc()).first()[0],
        'number_of_families': qt.filter(Languoid.level == LanguoidLevel.family).count(),
        'number_of_isolates': qt.filter(Languoid.level == LanguoidLevel.language).count(),
    }
    bookkeeping = DBSession.query(Language).filter(Language.name == BOOKKEEPING).one()
    ql = q.filter(and_(
        Languoid.level == LanguoidLevel.language,
        Languoid.family_pk != bookkeeping.pk))
    res['number_of_languages'] = {'all': ql.count()}

    res['special_families'] = OrderedDict()
    res['number_of_languages']['l1'] = res['number_of_languages']['all']
    for name in SPECIAL_FAMILIES:
        l = qt.filter(Language.name == name).one()
        res['special_families'][name] = l
        res['number_of_languages'][name] = l.child_language_count
        res['number_of_languages']['l1'] -= l.child_language_count

    return res


def childnodes(request):
    if request.params.get('t') == 'select2':
        query = DBSession.query(Languoid.id, Languoid.name, Languoid.level)\
            .filter(icontains(Languoid.name, request.params.get('q')))
        total = query.count()
        ms = LanguoidsMultiSelect(request, None, None, url='x')
        return dict(
            results=[ms.format_result(l) for l in query.limit(100)],
            context={},
            more=total > 500)

    query = DBSession.query(
        Languoid.pk,
        Languoid.id,
        Languoid.name,
        Languoid.level,
        func.count(TreeClosureTable.child_pk).label('children'))\
        .filter(Language.pk == TreeClosureTable.parent_pk)\
        .filter(Language.active == true())

    if request.params.get('node'):
        query = query.filter(Languoid.father_pk == int(request.params['node']))
    else:
        # narrow down selection of top-level nodes in the tree:
        query = query.filter(Languoid.father_pk == null())
        if request.params.get('q'):
            query = query.filter(Language.name.contains(request.params.get('q')))

    query = query.group_by(
        Languoid.pk,
        Languoid.id,
        Languoid.name,
        Languoid.level).order_by(Language.name)
    return [{
        'label': ('%s (%s)' % (l.name, l.children - 1))
            if l.children > 1 else l.name,
        'glottocode': l.id,
        'lname': l.name,
        'id': l.pk,
        'level': l.level.value,
        #'children': l.children
        'load_on_demand': l.children > 1} for l in query]


def credits(request):
    return HTTPMovedPermanently(location=request.route_url('about'))


def glossary(request):
    return {
        'macroareas': DBSession.query(Macroarea).order_by(Macroarea.id),
        'doctypes': DBSession.query(Doctype).order_by(Doctype.name)}


def cite(request):
    return {'date': date.today(), 'refs': CFG['PUBLICATIONS']}


def downloads(request):
    return {}


def news(request):
    return {}


def contact(request):
    return {}


def about(request):
    return {}


def families(request):
    return {'dt': request.get_datatable('languages', Language, type='families')}


def getLanguoids(name=False,
                 iso=False,
                 namequerytype='part',
                 country=False,
                 multilingual=False,
                 inactive=False):
    """return an array of languoids responding to the specified criterion.
    """
    if not (name or iso or country):
        return []

    query = DBSession.query(Languoid)\
        .options(joinedload(Languoid.family))\
        .order_by(Languoid.name)

    if not inactive:
        query = query.filter(Language.active == True)

    if name:
        crit = [Identifier.type == 'name']
        ul_iname = func.unaccent(func.lower(Identifier.name))
        ul_name = func.unaccent(name.lower())
        if namequerytype == 'whole':
            crit.append(ul_iname == ul_name)
        else:
            crit.append(ul_iname.contains(ul_name))
        if not multilingual:
            crit.append(func.coalesce(Identifier.lang, '').in_((u'', u'eng', u'en')))
        crit = Language.identifiers.any(and_(*crit))
        query = query.filter(or_(icontains(Languoid.name, name), crit))
    elif country:
        return []  # pragma: no cover
    else:
        query = query.join(LanguageIdentifier, Identifier)\
            .filter(Identifier.type == IdentifierType.iso.value)\
            .filter(Identifier.name.contains(iso.lower()))
    return query


def quicksearch(request):
    message = None
    query = DBSession.query(Languoid)
    term = request.params['search'].strip()
    titlecase = term.istitle()
    term = term.lower()
    params = {'iso': '', 'country': '',
        'name': '', 'namequerytype': 'part', 'multilingual': ''}

    if not term:
        query = None
    elif len(term) < 3:
        query = None
        message = ('Please enter at least four characters for a name search '
            'or three characters for an iso code')
    elif len(term) == 3 and not titlecase:
        query = query.filter(Languoid.identifiers.any(
            type=IdentifierType.iso.value, name=term))
        kind = 'ISO 639-3'
    elif len(term) == 8 and GLOTTOCODE_PATTERN.match(term):
        query = query.filter(Languoid.id == term)
        kind = 'Glottocode'
    else:
        _query = query.filter(func.lower(Languoid.name) == term)
        if DBSession.query(_query.exists()).scalar():
            query = _query
        else:
            query = query.filter(or_(
                func.lower(Languoid.name).contains(term),
                Languoid.identifiers.any(and_(
                    Identifier.type == u'name',
                    Identifier.description == Languoid.GLOTTOLOG_NAME,
                    func.lower(Identifier.name).contains(term)))))

        kind = 'name part'
        params['name'] = term

    if query is None:
        languoids = []
    else:
        languoids = query.order_by(Languoid.name)\
            .options(joinedload(Languoid.family)).all()
        if not languoids:
            term_pre = HTML.kbd(term, style='white-space: pre')
            message = 'No matching languoids found for %s "' % kind + term_pre + '"'
        elif len(languoids) == 1:
            raise HTTPFound(request.resource_url(languoids[0]))

    map_, icon_map, family_map = get_selected_languages_map(request, languoids)
    layer = list(map_.get_layers())[0]
    if not layer.data['features']:
        map_ = None

    countries = json.dumps(['%s (%s)' % (c.name, c.id) for c in
        DBSession.query(Country).order_by(Country.description)])

    return {'message': message, 'params': params, 'languoids': languoids,
        'map': map_, 'countries': countries}


# ENDPOINTS ADDED BY BLUEPRINT
def bpsearch(request):
    message = None
    query = DBSession.query(Languoid)
    term = request.params['bpsearch'].strip().lower()
    params = {
            'name': term,
            'namequerytype': request.params['namequerytype'],
            'multilingual': 'multilingual' in request.params
            }

    if not term:
        query = None
    elif len(term) < 3:
        query = None
        message = ('Please enter at least three characters for a search.')
    elif len(term) == 8 and GLOTTOCODE_PATTERN.match(term):
        query = query.filter(Languoid.id == term)
        kind = 'Glottocode'
    else:
        # list of criteria to search languoids by
        crit = [Identifier.type == 'name']
        ul_iname = func.unaccent(func.lower(Identifier.name))
        ul_name = func.unaccent(term)
        if params['namequerytype'] == 'whole':
            crit.append(ul_iname == ul_name)
        else:
            crit.append(ul_iname.contains(ul_name))
        if not params['multilingual']:
            # restrict to English identifiers
            crit.append(func.coalesce(Identifier.lang, '').in_((u'', u'eng', u'en')))
        crit = Language.identifiers.any(and_(*crit))
        # add ISOs to query if length == 3
        iso = Languoid.identifiers.any(type=IdentifierType.iso.value, name=term) if len(term) == 3 else None
        query = query.filter(or_(
            icontains(Languoid.name, term), 
            crit,
            iso))
        kind = 'name part'

    if query is None:
        languoids = []
    else:
        languoids = query.order_by(Languoid.name)\
            .options(joinedload(Languoid.family)).all()
        if not languoids:
            term_pre = HTML.kbd(term, style='white-space: pre')
            message = 'No matching languoids found for %s "' % kind + term_pre + '"'

    map_ = None

    countries = json.dumps(['%s (%s)' % (c.name, c.id) for c in
        DBSession.query(Country).order_by(Country.description)])

    return {'message': message, 'params': params, 'languoids': languoids,
            'map': map_, 'countries': countries}

@view_config(
        route_name='glottolog.bp_api_search',
        request_method='GET',
        renderer='json')
def bp_api_search(request):
    query = DBSession.query(Languoid)
    term = request.params['bpsearch'].strip().lower()
    namequerytype = request.params.get('namequerytype', 'part').strip().lower()
    multilingual = request.params.get('multilingual', None)

    if not term:
        query = None
    elif len(term) < 3:
        return [{'message': 'Please enter at least three characters for a search.'}]
    elif len(term) == 8 and GLOTTOCODE_PATTERN.match(term):
        query = query.filter(Languoid.id == term)
        kind = 'Glottocode'
    else:
        # list of criteria to search languoids by
        crit = [Identifier.type == 'name']
        ul_iname = func.unaccent(func.lower(Identifier.name))
        ul_name = func.unaccent(term)
        if namequerytype == 'whole':
            crit.append(ul_iname == ul_name)
        else:
            crit.append(ul_iname.contains(ul_name))
        if not multilingual:
            # restrict to English identifiers
            crit.append(func.coalesce(Identifier.lang, '').in_((u'', u'eng', u'en')))
        crit = Language.identifiers.any(and_(*crit))
        # add ISOs to query if length == 3
        iso = Languoid.identifiers.any(type=IdentifierType.iso.value, name=term) if len(term) == 3 else None
        query = query.filter(or_(
            icontains(Languoid.name, term), 
            crit,
            iso))
        kind = 'name part'

    if query is None:
        return []
    else:
        languoids = query.order_by(Languoid.name)\
                .options(joinedload(Languoid.family)).all()
        if not languoids:
            message = 'No matching languoids found for \'' + term + '\''
            return [{'message': message}]

    return [{
        'name': languoid.name,
        'glottocode': languoid.id,
        'iso': languoid.hid if languoid.hid else '',
        'level': languoid.level.name
        } for languoid in languoids]

@view_config(
        route_name='glottolog.add_identifier',
        request_method='POST', 
        renderer='json')
def add_identifier(request):
    # TODO: Add validity checks for parameters and unit tests

    gcode = request.json_body['glottocode']
    lang = request.json_body['language']
    name = request.json_body['name']
    type = request.json_body['type']
    desc = request.json_body['description']

    languoid = DBSession.query(Language) \
                        .filter_by(id='{0}'.format(gcode)) \
                        .first()

    identifier = Identifier(
        (name, type, desc, lang),
        id='{0}-{1}-{2}-{3}'.format(
        slug(name), slug(type), slug(desc or ''), lang),
        name=name,
        type=type,
        description=desc,
        lang=lang)

    try:
        DBSession.add(identifier)
        DBSession.add(
            LanguageIdentifier(language=languoid, identifier=identifier))
        DBSession.flush()
    except exc.SQLAlchemyError as e:
        DBSession.rollback()
        return { 'error': '{}'.format(e) }

    return {'message': 'Identifier successfully added.',
            'identifier': '%s' % identifier} 

# BLUEPRINT CODE END


def languages(request):
    if request.params.get('search'):
        return quicksearch(request)

    elif request.params.get('bpsearch'):
        return bpsearch(request)

    res = dict(
        countries=json.dumps([
            '%s (%s)' % (c.name, c.id) for c in
            DBSession.query(Country).order_by(Country.description)]),
        params={
            'name': '',
            'iso': '',
            'namequerytype': 'part',
            'country': ''},
        message=None)

    for param, default in res['params'].items():
        res['params'][param] = request.params.get(param, default).strip()

    if res['params']['country']:
        country = res['params']['country']
        try:
            alpha2 = country.split('(')[1].split(')')[0] \
                if len(country) > 2 else country.upper()
            raise HTTPFound(location=request.route_url(
                'languages_alt', ext='map.html', _query=dict(country=alpha2)))
        except IndexError:
            pass

    res['params']['multilingual'] = 'multilingual' in request.params

    if request.params.get('alnum'):
        l = Languoid.get(request.params.get('alnum'), default=None)
        if l:
            raise HTTPFound(location=request.resource_url(l))
        res['message'] = 'No matching languoids found'

    if (res['params']['iso'] and len(res['params']['iso']) < 2) or (
            res['params']['name']
            and len(res['params']['name']) < 2
            and res['params']['namequerytype'] == 'part'):
        res.update(
            message='Please enter at least two characters to search',
            map=None,
            languoids=[])
        return res

    languoids = list(getLanguoids(**res['params']))
    if not languoids and \
            (res['params']['name'] or res['params']['iso'] or res['params']['country']):
        res['message'] = 'No matching languoids found'
    #if len(languoids) == 1:
    #    raise HTTPFound(request.resource_url(languoids[0]))

    map_, icon_map, family_map = get_selected_languages_map(request, languoids)

    layer = list(map_.get_layers())[0]
    if not layer.data['features']:
        map_ = None
    res.update(map=map_, languoids=languoids)
    return res


def langdoccomplexquery(request):
    res = {
        'dt': None,
        'doctypes': DBSession.query(Doctype).order_by(Doctype.id),
        'macroareas': DBSession.query(Macroarea).order_by(Macroarea.id),
        'ms': {}
    }

    for name, cls, kw in [
        ('languoids', LanguoidsMultiSelect, dict(
            url=request.route_url('glottolog.childnodes'))),
        ('macroareas', MultiSelect, dict(collection=res['macroareas'])),
        ('doctypes', MultiSelect, dict(collection=res['doctypes'])),
    ]:
        res['ms'][name] = cls(request, name, 'ms' + name, **kw)

    res['params'], reqparams = get_params(request.params, **res)
    res['refs'] = getRefs(res['params'])

    if res['refs']:
        res['dt'] = Refs(request, Source, cq=1, **reqparams)

    fmt = request.params.get('format')
    if fmt:
        db = bibtex.Database([ref.bibtex() for ref in res['refs']])
        for name, adapter in request.registry.getAdapters([db], IRepresentation):
            if name == fmt:
                return adapter.render_to_response(db, request)
        return HTTPNotAcceptable()

    return res


def redirect_languoid_xhtml(req):
    return HTTPMovedPermanently(location=req.route_url('language', id=req.matchdict['id']))


def redirect_reference_xhtml(req):
    return HTTPMovedPermanently(location=req.route_url('source', id=req.matchdict['id']))
