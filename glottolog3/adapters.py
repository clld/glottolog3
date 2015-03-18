from six.moves import cStringIO as StringIO
from xml.etree import cElementTree as et
import codecs
from itertools import cycle

from path import path
from sqlalchemy.orm import joinedload_all
from pyramid.httpexceptions import HTTPFound

from clld.interfaces import ILanguage, IIndex
from clld.web.adapters.base import Representation, Index
from clld.web.adapters.download import CsvDump, N3Dump
from clld.web.adapters.geojson import pacific_centered_coordinates, GeoJsonLanguages
from clld.web.maps import GeoJsonSelectedLanguages, SelectedLanguagesMap
from clld.db.models.common import Language, LanguageIdentifier
from clld.web.icon import ORDERED_ICONS

import glottolog3
from glottolog3.models import Languoid, LanguoidLevel, Country
from glottolog3.interfaces import IProvider


class LanguoidCsvDump(CsvDump):

    def query(self, req):
        return Languoid.csv_query(session=req.db)

    def get_fields(self, req):
        return Languoid.csv_head()


class LanguoidN3Dump(N3Dump):

    def query(self, req):
        return req.db.query(Language).options(joinedload_all(
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
        filename = 'tree-%s-newick.txt' % languoid.id
        tree_dir = path(glottolog3.__file__).dirname().joinpath('static', 'trees')
        if tree_dir.joinpath(filename).exists():
            with codecs.open(tree_dir.joinpath(filename), encoding='utf8') as fp:
                content = fp.read()
            return content
        return ''


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
        out = StringIO()
        tree = et.ElementTree(element=e)
        tree.write(out, encoding='utf8', xml_declaration=True)
        out.seek(0)
        return out.read()

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
            ann.append(self.element(
                'desc', ' > '.join(reversed([l.name for l in lang.get_ancestors()]))))
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
    def _feature_properties(self, ctx, req, feature, language):
        res = {'language': language.__json__(req, core=True)}
        res.update(self.feature_properties(ctx, req, feature) or {})
        return res


class _GeoJsonSelectedLanguages(GeoJsonSelectedLanguages):
    def get_coordinates(self, language):
        return pacific_centered_coordinates(language)

    def _feature_properties(self, ctx, req, feature, language):
        res = {
            'icon': ctx[language.family_pk],
            'language': language.__json__(req, core=True),
        }
        res.update(self.feature_properties(ctx, req, feature) or {})
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
            icon_map[l.family_pk] = icons.next().url(req)
            family_map[l.family_pk] = l.family
    return _SelectedLanguagesMap(req, languages, icon_map), icon_map, family_map


class MapView(Index):
    extension = str('map.html')
    mimetype = str('text/vnd.clld.map+html')
    send_mimetype = str('text/html')
    template = 'language/map_html.mako'

    def template_context(self, ctx, req):
        if 'country' in req.params:
            country = Country.get(req.params['country'], default=None)
        else:
            country = None

        if country:
            languages = country.languoids
        else:
            languages = list(ctx.get_query(limit=8000))
        map_, icon_map, family_map = get_selected_languages_map(req, languages)
        return {
            'map': map_,
            'country': country,
            'icon_map': icon_map,
            'family_map': family_map,
            'languages': languages}


def includeme(config):
    config.register_adapter(Redirect, IProvider)
    config.register_adapter(Bigmap, ILanguage)
    config.register_adapter(PhyloXML, ILanguage)
    config.register_adapter(Newick, ILanguage)
    config.register_adapter(Treeview, ILanguage)
    config.register_adapter(GlottologGeoJsonLanguages, ILanguage, IIndex)
    config.register_adapter(MapView, ILanguage, IIndex)
