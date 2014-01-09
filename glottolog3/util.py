from json import dumps
import re
from itertools import cycle

from path import path
import colander
from sqlalchemy import or_, not_, desc
from sqlalchemy.orm import joinedload, joinedload_all
from sqlalchemy.sql.expression import func
from pyramid.httpexceptions import HTTPFound

from clld.db.meta import DBSession
from clld.db.models.common import (
    Identifier, LanguageIdentifier, IdentifierType, Language, Source, LanguageSource,
)
from clld.db.util import icontains
from clld.web.adapters.download import download_dir, download_asset_spec
from clld.web.util.helpers import link, icon
from clld.web.util.htmllib import HTML
from clld.web.icon import SHAPES
from clld.interfaces import IIcon

import glottolog3
from glottolog3.models import (
    Country, Languoid, Languoidcountry, Refprovider, Provider, Ref,
    Macroarea, Refmacroarea, TreeClosureTable, Doctype, Refdoctype,
    LanguoidStatus,
)
from glottolog3.maps import LanguoidsMap


REF_PATTERN = re.compile('\*\*(?P<id>[0-9]+)\*\*')


def languoid_link(req, languoid, active=True, classification=False):
    link_attrs = {}
    if languoid.status and languoid.status.value:
        link_attrs['class'] = 'Language ' + languoid.status.value
    if languoid.status and languoid.status != LanguoidStatus.established:
        link_attrs['title'] = '%s - %s' % (languoid.name, languoid.status.description)
    content = [link(req, languoid, **link_attrs) if active else languoid.name]
    if classification:
        if languoid.fc or languoid.sc:
            content.append(
                icon("icon-info-sign", title="classification comment available"))
    return HTML.span(*content, **dict(class_="level-" + languoid.level.value))


def old_downloads(req):
    for version in sorted(download_dir('glottolog3').dirs()):
        number = version.basename()
        dls = []
        for f in version.files():
            dls.append((
                f.basename(),
                req.static_url(download_asset_spec('glottolog3', number, f.basename()))))
        yield number, dls


class ModelInstance(object):
    def __init__(self, cls, attr='id', collection=None, alias=None):
        self.cls = cls
        self.attr = attr
        self.alias = alias
        self.collection = collection

    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        if not isinstance(appstruct, self.cls):
            raise colander.Invalid(node, '%r is not a boolean' % appstruct)
        return getattr(appstruct, self.attr)

    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null
        value = None
        if self.collection:
            for obj in self.collection:
                if getattr(obj, self.attr) == cstruct \
                        or (self.alias and getattr(obj, self.alias) == cstruct):
                    value = obj
        else:
            value = self.cls.get(cstruct, key=self.attr, default=None)
            if self.alias and value is None:
                value = self.cls.get(cstruct, key=self.alias, default=None)
        if value is None:
            raise colander.Invalid(node, 'no single result found')
        return value

    def cstruct_children(self, node, cstruct):
        return []


def get_params(params, **kw):
    """
    :return: pair (appstruct, request params dict)
    """
    def default_params():
        d = dict(biblio={})
        for name in 'author year title editor journal address publisher'.split():
            d['biblio'][name] = ''
        return d

    reqparams = {}
    cstruct = default_params()

    biblio = colander.SchemaNode(colander.Mapping(), name='biblio', missing={})
    for name in cstruct['biblio']:
        biblio.add(
            colander.SchemaNode(colander.String(), name=name, missing='', title=name.capitalize()))
        cstruct['biblio'][name] = params.get(name, '')
        if cstruct['biblio'][name]:
            reqparams[name] = cstruct['biblio'][name]

    schema = colander.SchemaNode(colander.Mapping())
    for name, cls in dict(languoid=Languoid, doctype=Doctype, macroarea=Macroarea).items():
        plural = name + 's'
        _kw = dict(collection=kw.get(plural))
        if name == 'languoid':
            _kw['alias'] = 'hid'
        schema.add(
            colander.SchemaNode(
                colander.Sequence(),
                colander.SchemaNode(ModelInstance(cls, **_kw), name=name),
                missing=[],
                name=plural))
        if plural != 'languoids':
            cstruct[plural] = params.getall(plural) if hasattr(params, 'getall') else params.get(plural, [])
            if cstruct[plural]:
                reqparams[plural] = cstruct[plural]
        else:
            cstruct[plural] = filter(None, params.get(plural, '').split(','))
            if cstruct[plural]:
                reqparams[plural] = params[plural]
    schema.add(biblio)
    try:
        return schema.deserialize(cstruct), reqparams
    except colander.Invalid:
        return default_params(), {}


def getRefs(params):
    query = DBSession.query(Ref)
    filtered = False

    for param, value in params['biblio'].items():
        if value:
            filtered = True
            query = query.filter(icontains(getattr(Ref, param), value))

    if params.get('languoids'):
        filtered = True
        lids = DBSession.query(TreeClosureTable.child_pk)\
            .filter(TreeClosureTable.parent_pk.in_([l.pk for l in params['languoids']]))\
            .subquery()
        query = query.join(LanguageSource, LanguageSource.source_pk == Ref.pk)\
            .filter(LanguageSource.language_pk.in_(lids))

    if params.get('doctypes'):
        filtered = True
        query = query.join(Refdoctype)\
            .filter(Refdoctype.doctype_pk.in_([l.pk for l in params['doctypes']]))

    if params.get('macroareas'):
        filtered = True
        query = query.join(Refmacroarea)\
            .filter(Refmacroarea.macroarea_pk.in_([l.pk for l in params['macroareas']]))

    if not filtered:
        return []

    return query.distinct()


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
                 multilingual=False,
                 inactive=False):
    """return an array of languoids responding to the specified criterion.
    """
    if not (name or iso or country):
        return []

    query = DBSession.query(Languoid)\
        .options(joinedload(Language.sources), joinedload(Languoid.family))\
        .order_by(Languoid.name)

    if not inactive:
        query = query.filter(Language.active == True)

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
        try:
            alpha2 = country.split('(')[1].split(')')[0] \
                if len(country) > 2 else country.upper()
        except IndexError:
            return []
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
            'country': ''},
        message=None)

    for param, default in res['params'].items():
        res['params'][param] = request.params.get(param, default).strip()

    res['params']['multilingual'] = 'multilingual' in request.params

    if request.params.get('alnum'):
        l = Languoid.get(request.params.get('alnum'), default=None)
        if l:
            raise HTTPFound(location=request.resource_url(l))
        res['message'] = 'No matching languoids found'

    languoids = list(getLanguoids(**res['params']))
    if not languoids and \
            (res['params']['name'] or res['params']['iso'] or res['params']['country']):
        res['message'] = 'No matching languoids found'
    #if len(languoids) == 1:
    #    raise HTTPFound(request.resource_url(languoids[0]))
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


def get_icon_map(request, context):
    icon_map = dict(
        zip([context.pk] + [l.pk for l in context.children],
            cycle([s + c for s in SHAPES for c in COLORS])))
    for key in icon_map:
        icon_map[key] = request.registry.getUtility(IIcon, icon_map[key]).url(request)
    return icon_map


def language_detail_html(request=None, context=None, **kw):
    return dict(icon_map=get_icon_map(request, context))


def language_bigmap_html(request=None, context=None, **kw):
    return dict(icon_map=get_icon_map(request, context))


def language_snippet_html(request=None, context=None, **kw):
    source = None
    if request.params.get('source'):
        source = Source.get(request.params['source'])
    return dict(source=source)
