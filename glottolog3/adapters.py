import datetime
import xml.etree.ElementTree as et
from itertools import cycle
import tempfile

import sqlalchemy as sa
import sqlalchemy.orm
from pyramid.httpexceptions import HTTPFound

from clld.interfaces import IDataset, IMetadata, ILanguage, IIndex, IParameter, IRepresentation
from clld.web.adapters.base import Representation, Index
from clld.web.adapters.download import CsvDump, N3Dump, Download
from clld.web.adapters.geojson import GeoJsonLanguages, GeoJsonParameter, GeoJsonParameterFlatProperties
from clld.web.adapters.md import BibTex, ReferenceManager
from clld.web.maps import GeoJsonSelectedLanguages, SelectedLanguagesMap
from clld.db.models.common import Language, LanguageIdentifier, Identifier, DomainElement, ValueSet, Value, Parameter
from clld.web.icon import ORDERED_ICONS
from clld.lib import bibtex
from clldutils.misc import to_binary

from glottolog3.models import Languoid, LanguoidLevel
from glottolog3.interfaces import IProvider
from glottolog3 import maps
from glottolog3.util import DOI


def rec(ctx, req):
    url = '%s accessed %s' % (req.resource_url(ctx), datetime.date.today())
    return bibtex.Record(
        'book',
        req.dataset.id,
        author=[c.contributor.name for c in ctx.editors],
        title=getattr(ctx, 'citation_name', ctx.__str__()),
        url=url,
        address=req.dataset.publisher_place,
        howpublished=req.dataset.publisher_name,
        year=str(req.dataset.published.year),
        doi=DOI,
    )


class BibTexCitation(BibTex):

    def rec(self, ctx, req):
        return rec(ctx, req)


class RIS(ReferenceManager):

    def rec(self, ctx, req):
        return rec(ctx, req)


class LanguoidCsvDump(CsvDump):

    def query(self, req):
        Family = sa.orm.aliased(Language, flat=True)
        Father = sa.orm.aliased(Language, flat=True)
        _Country = sa.orm.aliased(DomainElement, name='_country')

        query = req.db.query(
                Languoid.id, Family.id.label('family_id'), Father.id.label('parent_id'),
                Languoid.name,
                Languoid.bookkeeping,
                sa.type_coerce(Languoid.level, sa.Text).label('level'),
                Languoid.latitude, Languoid.longitude,
                sa.select([Identifier.name])
                    .where(LanguageIdentifier.identifier_pk == Identifier.pk)
                    .where(LanguageIdentifier.language_pk == Language.pk)
                    .where(Identifier.type == 'iso639-3')
                    .label('iso639P3code'),
                Languoid.description, Languoid.markup_description,
                Languoid.child_family_count, Languoid.child_language_count, Languoid.child_dialect_count,
                sa.select([sa.literal_column("string_agg(_country.name, ' ' ORDER BY _country.name)")])
                    .where(Value.domainelement_pk == _Country.pk)
                    .where(Value.valueset_pk == ValueSet.pk)
                    .where(ValueSet.parameter_pk == Parameter.pk)
                    .where(Parameter.id == 'country')
                    .where(ValueSet.language_pk == Languoid.pk)
                    .label('country_ids'),
            ).select_from(Languoid).filter(Languoid.active)\
            .outerjoin(Family, Family.pk == Languoid.family_pk)\
            .outerjoin(Father, Father.pk == Languoid.father_pk)\
            .order_by(Languoid.id)
        return query

    def get_fields(self, req):
        if not self.fields:
            self.fields = [c.name for c in self.query(req).statement.columns]
        return self.fields

    def row(self, req, fd, item, index):
        return item


class TurtleDump(Download):
    ext = 'ttl'

    def dump_rendered(self, req, fp, item, index, rendered):
        header, body = rendered.split(to_binary('\n\n'), 1)
        if index == 0:
            fp.write(header)
            fp.write(to_binary('\n\n'))
        fp.write(body)


class LanguoidTurtleDump(TurtleDump):

    def query(self, req):
        return req.db.query(Language).options(sa.orm.joinedload_all(
            Language.languageidentifier, LanguageIdentifier.identifier))\
            .order_by(Language.pk)


class LanguoidN3Dump(N3Dump):

    def query(self, req):
        return req.db.query(Language).options(sa.orm.joinedload_all(
            Language.languageidentifier, LanguageIdentifier.identifier))\
            .order_by(Language.pk)


class Redirect(Representation):
    mimetype = 'text/html'
    extension = 'html'

    def render(self, ctx, req):
        raise HTTPFound(
            req.route_url('providers', _anchor='provider-' + req.matchdict['id']))


class Bigmap(Representation):
    mimetype = 'text/vnd.clld.bigmap+html'
    send_mimetype = 'text/html'
    extension = 'bigmap.html'
    template = 'language/bigmap_html.mako'


class Treeview(Representation):
    """Classification tree rooted at the current languoid rendered as svg graphic in an
    HTML page.
    """
    name = 'SVG Classification Tree'
    mimetype = 'text/vnd.clld.treeview+html'
    send_mimetype = 'text/html'
    extension = 'treeview.html'
    template = 'language/treeview_html.mako'


class Newick(Representation):
    """Classification tree represented in Newick format.
    """
    name = 'Newick format'
    mimetype = 'text/vnd.clld.newick+plain'
    send_mimetype = 'text/plain'
    extension = 'newick.txt'

    def render(self, languoid, request):
        if languoid.family:
            languoid = languoid.family
        return languoid.newick


class PhyloXML(Representation):
    """Classification tree rooted at the current languoid represented in PhyloXML.
    """
    name = 'PhyloXML'
    mimetype = 'application/vnd.clld.phyloxml+xml'
    send_mimetype = 'application/xml'
    extension = 'phylo.xml'
    namespace = 'http://www.phyloxml.org'

    def render(self, root, req):
        self.depth_limit = 2 if root.child_language_count > 350 else 100
        et.register_namespace('', self.namespace)
        e = self.element('phyloxml')
        phylogeny = self.element('phylogeny', rooted="true")
        phylogeny.append(self.element('name', root.name))
        phylogeny.append(self.element('description', root.name))
        clade = self.clade(root, req)
        self.append_children(clade, root, req, 0)
        phylogeny.append(clade)
        e.append(phylogeny)
        tree = et.ElementTree(element=e)
        with tempfile.TemporaryFile() as fp:
            tree.write(fp, encoding='utf8', xml_declaration=True)
            fp.seek(0)
            return fp.read()

    def element(self, name, text=None, **kw):
        e = et.Element('{%s}%s' % (self.namespace, name), **kw)
        if text:
            e.text = text
        return e

    def clade(self, lang, req, level=0):
        e = self.element('clade', branch_length="0.2")
        if lang.level == LanguoidLevel.language or level == self.depth_limit:
            e.append(self.element('name', lang.name))
            ann = self.element('annotation')
            ann.append(self.element('desc', ' > '.join(reversed([l.name for l in lang.get_ancestors()]))))
            ann.append(self.element('uri', req.resource_url(lang)))
            e.append(ann)
        return e

    def append_children(self, clade, lang, req, level):
        if level > self.depth_limit:
            return
        children = [l for l in lang.children if
                    l.level in [LanguoidLevel.language, LanguoidLevel.family]]
        for child in sorted(children, key=lambda l: l.name):
            subclade = self.clade(child, req, level)
            if child.children:
                self.append_children(subclade, child, req, level + 1)
            clade.append(subclade)


class GlottologGeoJsonLanguages(GeoJsonLanguages):
    def feature_properties(self, ctx, req, feature):
        res = GeoJsonLanguages.feature_properties(self, ctx, req, feature)
        language = self.get_language(ctx, req, feature)
        res.update(language=language.__json__(req, core=True))
        return res


class _GeoJsonSelectedLanguages(GeoJsonSelectedLanguages):
    def feature_properties(self, ctx, req, feature):
        res = GeoJsonSelectedLanguages.feature_properties(self, ctx, req, feature)
        language = self.get_language(ctx, req, feature)
        res.update(
            icon=ctx[language.family_pk],
            language=language.__json__(req, core=True))
        return res


class _SelectedLanguagesMap(SelectedLanguagesMap):
    def __init__(self, req, languages, icon_map):
        SelectedLanguagesMap.__init__(
            self, icon_map, req, languages, geojson_impl=_GeoJsonSelectedLanguages)

    def get_options(self):
        opts = SelectedLanguagesMap.get_options(self)
        opts['max_zoom'] = 12
        return opts


def get_selected_languages_map(req, languages):
    icon_map = {}
    family_map = {}
    icons = cycle(ORDERED_ICONS)
    for l in languages:
        if l.family_pk not in icon_map:
            icon_map[l.family_pk] = next(icons).url(req)
            family_map[l.family_pk] = l.family
    return _SelectedLanguagesMap(req, languages, icon_map), icon_map, family_map


class MapView(Index):
    extension = str('map.html')
    mimetype = str('text/vnd.clld.map+html')
    send_mimetype = str('text/html')
    template = 'language/map_html.mako'

    def template_context(self, ctx, req):
        if 'country' in req.params:
            country = DomainElement.get('country-' + req.params['country'], default=None)
        else:
            country = None

        if country:
            languages = [v.valueset.language for v in country.values]
        else:
            languages = list(ctx.get_query(limit=8000))
        map_, icon_map, family_map = get_selected_languages_map(req, languages)
        return {
            'map': map_,
            'country': country,
            'icon_map': icon_map,
            'family_map': family_map,
            'languages': languages}


class GeoJsonFeature(GeoJsonParameter):
    def feature_iterator(self, ctx, req):
        if ctx.id in ['aes', 'med']:
            return GeoJsonParameter.feature_iterator(self, ctx, req)
        return []

    def get_language(self, ctx, req, valueset):
        l = valueset.language
        return maps.Language(l.pk, l.name, l.longitude, l.latitude, l.id)


class GeoJsonFeatureFlat(GeoJsonParameterFlatProperties):
    def feature_iterator(self, ctx, req):
        return []



def includeme(config):
    config.register_adapter(GeoJsonFeatureFlat, IParameter)
    config.register_adapter(GeoJsonFeature, IParameter)
    config.register_adapter(BibTexCitation, IDataset, IMetadata)
    config.register_adapter(BibTexCitation, IDataset, IRepresentation)
    config.register_adapter(RIS, IDataset, IMetadata)
    config.register_adapter(RIS, IDataset, IRepresentation)
    config.register_adapter(Redirect, IProvider)
    config.register_adapter(Bigmap, ILanguage)
    config.register_adapter(PhyloXML, ILanguage)
    config.register_adapter(Newick, ILanguage)
    config.register_adapter(Treeview, ILanguage)
    config.register_adapter(GlottologGeoJsonLanguages, ILanguage, IIndex)
    config.register_adapter(MapView, ILanguage, IIndex)
