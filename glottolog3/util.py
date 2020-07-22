import re
from itertools import cycle, groupby

from sqlalchemy import or_
from purl import URL
import colander
from markdown import markdown
from markupsafe import Markup
from clld.db.meta import DBSession
from clld.db.models.common import Language, Source, LanguageSource, DomainElement
from clld.db.util import icontains
from clld.web.util.helpers import link, icon, button
from clld.web.util.htmllib import HTML, literal
from clld.web.icon import SHAPES
from clld.interfaces import IIcon
from clldutils.misc import format_size
from clldutils.path import Path
from clldutils.jsonlib import load
from pyglottolog.languoids import Reference

from glottolog3.models import (
    Languoid, Provider, Ref, Refprovider, TreeClosureTable, Doctype, Refdoctype,
)
from glottolog3.maps import LanguoidMap
from glottolog3.config import PartnerSite, ISOSite

DOI = "10.5281/zenodo.3754591"

LANG_PATTERN = re.compile('\[(?P<id>[^\]]+)\]')
ISO_PATTERN = re.compile(r'\[(?P<iso>[a-z]{3})\]')


def set_focus(url, focus):
    return URL(url).query_param('focus', focus).as_string()


def github_link(ctx):
    return button(
        icon('pencil'), title="see on GitHub", href=ctx.github_url, class_='btn-mini')


def languoid_link(req, languoid, active=True, classification=False):
    link_attrs = {}
    content = [link(req, languoid, **link_attrs) if active else languoid.name]
    if classification:
        if languoid.fc or languoid.sc:
            content.append(
                icon("icon-info-sign", title="classification comment available"))
    return HTML.span(*content, **dict(class_="level-" + languoid.level.value))


def linkify_iso_codes(request, text, class_=None, route_name='glottolog.iso'):
    def chunks():
        start = 0
        if not text:
            yield ''
        else:
            for match in ISO_PATTERN.finditer(text):
                yield text[start:match.start(0)]
                url = request.route_url(route_name, id=match.group('iso'))
                yield HTML.a(match.group(0), href=url, class_=class_)
                start = match.end(0)
            yield text[start:]
    return literal('').join(chunks())


def old_downloads():
    from clldmpg import cdstar

    def bitstream_link(oid, spec):
        url = cdstar.SERVICE_URL.path(
            '/bitstreams/{0}/{1}'.format(oid, spec['bitstreamid'])).as_string()
        return HTML.a(
            '{0} [{1}]'.format(spec['bitstreamid'], format_size(spec['filesize'])),
            href=url)

    for number, spec in sorted(
            load(Path(__file__).parent.joinpath('static', 'downloads.json')).items()):
        yield number, [bitstream_link(spec['oid'], bs) for bs in spec['bitstreams']]


class ModelInstance(object):
    def __init__(self, cls, attr='id', collection=None, alias=None):
        self.cls = cls
        self.attr = attr
        self.alias = alias
        self.collection = collection

    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        if self.cls and not isinstance(appstruct, self.cls):
            raise colander.Invalid(node, '%r is not a %s' % (appstruct, self.cls))
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
            value = self.cls.get(cstruct, key=self.attr, default=None) if self.cls else cstruct
            if self.alias and value is None:
                value = self.cls.get(cstruct, key=self.alias, default=None) if self.cls else cstruct
        if value is None:
            raise colander.Invalid(node, 'no single result found')
        return value

    def cstruct_children(self, node, cstruct):  # pragma: no cover
        return []


def get_params(params, **kw):
    """
    :return: pair (appstruct, request params dict)
    """
    def default_params():
        return {
            'biblio': {
                n: '' for n
                in 'author year title editor journal address publisher'.split()}}

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
            languoid=Languoid,
            doctype=Doctype,
            macroarea=None,
    ).items():
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
            cstruct[plural] = [p for p in params.get(plural, '').split(',') if p]
            if cstruct[plural]:
                reqparams[plural] = params[plural]
    schema.add(biblio)
    try:
        return schema.deserialize(cstruct), reqparams
    except colander.Invalid:  # pragma: no cover
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
        names = [getattr(ma, 'name', None) or DomainElement.get(ma).name for ma in params['macroareas']]
        query = query.filter(or_(*[Ref.macroareas.contains(n) for n in names]))

    if not filtered:
        return DBSession.query(Ref).filter(Ref.pk == -1)

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
    for match in Reference.pattern.finditer(comment):
        preceding = comment[pos:match.start()]
        parts.append(preceding)
        parts.append(match.group('key'))
        sources[match.group('key')] = None
        if match.group('pages'):
            parts.append(': {0}'.format(match.group('pages')))
        pos = match.end()
    parts.append(comment[pos:])

    for rp in DBSession.query(Refprovider).filter(Refprovider.id.in_(sources.keys())):
        sources[rp.id] = rp.ref

    return ' '.join(
        link(req, sources[p]) if sources.get(p) else p for p in parts).replace(' : ', ': ')


def format_justifications(req, refs):
    seen = set()
    r = []
    for ref in refs:
        if ref.source:
            key = (ref.source.pk, ref.description)
            if key in seen:
                continue
            seen.add(key)
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
    if '[' in chunk and not chunk.endswith(']'):
        chunk += ']'
    chunk = chunk.strip()
    if '=' not in chunk:
        return chunk
    chunks = chunk.split('=')
    left = '='.join(chunks[:-1]).strip()
    right = chunks[-1].strip()
    if right.startswith('"') and right.endswith('"') and '[' not in right and '[' in left:
        # case ii)
        return right[1:-1].strip() + ' [' + left.split('[', 1)[1]
    if '[' in right and '[' not in left:
        # case iii)
        return left + ' [' + right.split('[', 1)[1]
    return chunk


def format_languages(req, ref):
    ldict = {l.hid: l for l in ref.languages}
    ldict.update({l.id: l for l in ref.languages})
    in_note = set()
    lnotes = map(normalize_language_explanation, (ref.jsondata.get('lgcode', '')).split('],'))
    for lnote in lnotes:
        note = []
        start = 0
        m = None
        for m in LANG_PATTERN.finditer(lnote):
            note.append(lnote[start:m.start()])
            note.append('[')
            if m.group('id') in ldict:
                in_note.add(m.group('id'))
                lang = ldict[m.group('id')]
                note.append(link(req, lang, label=lang.id, title=lang.name))
            else:
                note.append(m.group('id'))
            note.append(']')
            start = m.end()
        if m:
            note.append(lnote[m.end():])
        yield HTML.li(*note)

    for lang in set(ldict.values()):
        if (lang.hid not in in_note) and (lang.id not in in_note):
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


def format_external_link_in_label(url, label=None):
    label = label or URL(url).domain()
    return HTML.span(
        HTML.a(
            HTML.i('', class_="icon-share icon-white"),
            label,
            href=url,
            style="color: white"),
        class_="label label-info")


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
    return dict(
        source=Source.get(request.params['source'])
        if request.params.get('source') else None)


def md(req, s, small=False):
    s = s.replace('``', '\u201c')
    s = s.replace("''", '\u201d')
    res = linkify_iso_codes(req, s)
    res = format_comment(req, res)
    res = markdown(res, extensions=['markdown.extensions.tables'])
    if small:
        res = res.replace('<p>', '<p><small>').replace('</p>', '</small></p>')
    return Markup(res.replace('<table>', '<table class="table">'))


def infobox(*content):
    return HTML.div(
        HTML.button(
            '\xd7', **{'type': "button", 'class': "close", 'data-dismiss': "alert"}),
        *content,
        **{'class': "alert alert-success"})


def format_ethnologue_comment(req, lang):
    return infobox(md(req, lang.jsondata['ethnologue_comment']['comment']))


def format_iso_retirement(req, lang):
    ir = lang.jsondata['iso_retirement']
    _md, comment = [], ''
    if ir['comment']:
        comment = HTML.div(
            HTML.p(HTML.strong("Excerpt from change request document:")),
            HTML.blockquote(md(req, ir['comment'], small=True)))

    if ir['change_request']:
        _md.append((
            'Change request:',
            link(
                req,
                Refprovider.get('iso6393:{0}'.format(ir['change_request'])).ref,
                label=ir['change_request'])))
    _md.append(('ISO 639-3:', ir['code']))
    _md.append(('Name:', ir['name']))
    if ir['reason']:
        _md.append(('Reason:', ir['reason']))
    _md.append(('Effective:', ir['effective']))

    return infobox(
        HTML.p(
            HTML.strong("Retired in ISO 639-3: "),
            linkify_iso_codes(req, ir['remedy'], class_='iso639-3')),
        HTML.ul(
            *[HTML.li(HTML.strong(dt), Markup('&nbsp;'), dd)
              for dt, dd in _md], **{'class': 'inline'}),
        comment)


def format_links(req, lang):
    def link(href, label, img, alt=None):
        return HTML.li(
            HTML.a(
                HTML.img(
                    src=req.static_url('glottolog3:static/' + img),
                    height="20",
                    width="20",
                    alt=alt or label),
                ' ',
                label,
                href=href,
                target = "_blank",
                title=label,
            )
        )

    links = []
    if lang.iso_code:
        for isosite in ISOSite.__subclasses__():
            isosite = isosite()
            links.append(link(*isosite.href_label_img_alt(lang.iso_code)))
    pss = [ps() for ps in PartnerSite.__subclasses__()]
    for domain, _links in groupby(lang.jsondata['links'], lambda l: URL(l['url']).domain()):
        for ps in pss:
            if ps.match(domain):
                links.extend([link(*ps.href_label_img_alt(l)) for l in _links])
    return HTML.ul(*links, **{'class': "nav nav-tabs nav-stacked"})


def dataset_detail_html(request=None, context=None, **kw):
    return {'numrefs': '{0:,}'.format(DBSession.query(Source).count())}
