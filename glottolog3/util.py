from json import dumps
import re
from itertools import cycle

import colander

from clld.db.meta import DBSession
from clld.db.models.common import Language, Source, LanguageSource
from clld.db.util import icontains
from clld.web.adapters.download import download_dir, download_asset_spec
from clld.web.util.helpers import link, icon
from clld.web.util.htmllib import HTML, literal
from clld.web.icon import SHAPES
from clld.interfaces import IIcon

from glottolog3.models import (
    Languoid, Provider, Ref,
    Macroarea, Refmacroarea, TreeClosureTable, Doctype, Refdoctype,
    LanguoidStatus,
)
from glottolog3.maps import LanguoidMap


REF_PATTERN = re.compile('\*\*(?P<id>[0-9]+)\*\*')
LANG_PATTERN = re.compile('\[(?P<id>[^\]]+)\]')
ISO_PATTERN = re.compile(r'\[(?P<iso>[a-z]{3})\]')


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


def change_request_link(cr_id, iso_code=None, label=None):
    if iso_code:
        url = 'http://www.sil.org/iso639-3/chg_detail.asp?id={0}&lang={1}'
        args = (cr_id, iso_code)
    else:
        url = 'http://www.sil.org/iso639-3/chg_detail.asp?id={0}'
        args = (cr_id,)
    return HTML.a(label or cr_id, href=url.format(*args))


def linkify_iso_codes(text, class_=None, url='/resource/languoid/iso/{0}'):
    def chunks():
        start = 0
        for match in ISO_PATTERN.finditer(text):
            yield text[start:match.start(0)]
            yield HTML.a(match.group(0), href=url.format(match.group('iso')),
                class_=class_)
            start = match.end(0)
        yield text[start:]
    return literal('').join(chunks())


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
            colander.SchemaNode(
                colander.String(), name=name, missing='', title=name.capitalize()))
        cstruct['biblio'][name] = params.get(name, '')
        if cstruct['biblio'][name]:
            reqparams[name] = cstruct['biblio'][name]

    schema = colander.SchemaNode(colander.Mapping())
    for name, cls in dict(
            languoid=Languoid, doctype=Doctype, macroarea=Macroarea).items():
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
            cstruct[plural] = params.getall(plural) if hasattr(params, 'getall') \
                else params.get(plural, [])
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
        subquery = DBSession.query(LanguageSource).filter_by(source_pk=Ref.pk)\
            .join(TreeClosureTable,
                TreeClosureTable.child_pk == LanguageSource.language_pk)\
            .filter(TreeClosureTable.parent_pk.in_(
                [l.pk for l in params['languoids']]))
        query = query.filter(subquery.exists())
                
    if params.get('doctypes'):
        filtered = True
        subquery = DBSession.query(Refdoctype).filter_by(ref_pk=Ref.pk)\
            .filter(Refdoctype.doctype_pk.in_(
                [d.pk for d in params['doctypes']]))
        query = query.filter(subquery.exists())

    if params.get('macroareas'):
        filtered = True
        subquery = DBSession.query(Refmacroarea).filter_by(ref_pk=Ref.pk)\
            .filter(Refmacroarea.macroarea_pk.in_(
                [m.pk for m in params['macroareas']]))
        query = query.filter(subquery.exists())

    if not filtered:
        return []

    return query


def provider_index_html(request=None, **kw):
    return {
        'providers': DBSession.query(Provider),
        'totalrefs': DBSession.query(Source).count(),
        'totalnodes': DBSession.query(Language).count(),
    }


def format_comment(req, comment):
    """
    We collect source ids found in comment, retrieve the corresponding source objects from
    the database in a single query and then replace the ids with formatted source links.
    """
    parts = []
    sources = {}
    pos = 0
    comment = comment.replace('~', ' ')
    for match in REF_PATTERN.finditer(comment):
        preceding = comment[pos:match.start()]
        parts.append(preceding)
        add_braces = \
            (preceding.strip().split() or ['aaa'])[-1] not in ['in', 'of', 'per', 'by']
        if add_braces:
            parts.append('(')
        parts.append(match.group('id'))
        sources[match.group('id')] = None
        if add_braces:
            parts.append(')')
        pos = match.end()
    parts.append(comment[pos:])

    for source in DBSession.query(Source).filter(Source.id.in_(sources.keys())):
        sources[source.id] = source

    return HTML.p(*[link(req, sources[p]) if p in sources else p for p in parts] )


def format_classificationcomment(req, comment):
    return format_comment(req, comment)


def format_justifications(req, refs):
    seen = {}
    r = []
    for ref in refs:
        key = (ref.source.pk, ref.description)
        if key in seen:
            continue
        seen[key] = 1
        label = ref.source.name
        if ref.description:
            label += '[%s]' % ref.description
        r.append(HTML.li(link(req, ref.source, label=label)))
    return HTML.ul(*r)


COLORS = [
    #            red     yellow
    "00ff00", "ff0000", "ffff00", "0000ff", "ff00ff", "00ffff", "000000",
]


def normalize_language_explanation(chunk):
    """
    i) X [aaa]
    ii) L [aaa] = "X"
    iii) X = L [aaa]

    :return: X [aaa]
    """
    chunk = chunk.strip()
    if '=' not in chunk:
        return chunk
    chunks = chunk.split('=')
    left = '='.join(chunks[:-1]).strip()
    right = chunks[-1].strip()
    if right.startswith('"') and right.endswith('=') and '[' not in right and '[' in left:
        # case ii)
        return right[1:-1].strip() + ' [' + left.split('[', 1)[1]
    if '[' in right and '[' not in left:
        # case iii)
        return left + ' [' + right.split('[', 1)[1]
    return chunk


def format_languages(req, ref):
    ldict = {l.hid: l for l in ref.languages}
    in_note = {}
    lnotes = map(normalize_language_explanation, (ref.language_note or '').split(','))

    for lnote in lnotes:
        note = []
        start = 0
        m = None
        for m in LANG_PATTERN.finditer(lnote):
            note.append(lnote[start:m.start()])
            note.append('[')
            if m.group('id') in ldict:
                in_note[m.group('id')] = 1
                lang = ldict[m.group('id')]
                note.append(link(req, lang, label=lang.id, title=lang.name))
            else:
                note.append(m.group('id'))
            note.append(']')
            start = m.end()
        if m:
            note.append(lnote[m.end():])
        yield HTML.li(*note)

    for lang in ldict.values():
        if lang.hid not in in_note:
            yield HTML.li(
                lang.name + ' [', link(req, lang, label=lang.id, title=lang.name), ']')


def format_label_link(href, label, title=None):
    return HTML.span(
        HTML.a(label, href=href, title=title or label, style='color: white;'),
        class_='label')


def format_language_header(req, ref, level=3):
    content = ['Languages']
    if ref.ca_language_trigger:
        content.append(format_ca_icon(req, ref, 'language'))
    return getattr(HTML, 'h' + str(level))(*content)


def format_ca_icon(req, ref, type_):
    trigger = getattr(ref, 'ca_' + type_ + '_trigger')
    if not trigger:
        return ''
    return icon(
        'warning-sign',
        title='computerized assignment of %ss from "%s"' % (type_, trigger))


def get_map(request, context):
    icon_map = dict(
        zip([context.pk] + [l.pk for l in context.children],
            cycle([s + c for s in SHAPES for c in COLORS])))
    for key in icon_map:
        icon_map[key] = request.registry.getUtility(IIcon, icon_map[key]).url(request)
    return dict(icon_map=icon_map, lmap=LanguoidMap(context, request, icon_map=icon_map))


def language_detail_html(request=None, context=None, **kw):
    return get_map(request, context)


def language_bigmap_html(request=None, context=None, **kw):
    return get_map(request, context)


def language_snippet_html(request=None, context=None, **kw):
    source = None
    if request.params.get('source'):
        source = Source.get(request.params['source'])
    return dict(source=source)
