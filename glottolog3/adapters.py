from cStringIO import StringIO
from xml.etree import cElementTree as et
import codecs

from path import path
from sqlalchemy.orm import joinedload_all
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render as pyramid_render

from clld.web.adapters.base import Representation, Index
from clld.web.adapters.download import CsvDump, N3Dump
from clld.db.meta import DBSession
from clld.db.models.common import Language, LanguageIdentifier

import glottolog3
from glottolog3.models import LanguoidLevel


def _lang_query():
    return DBSession.query(Language)\
        .options(
            joinedload_all(Language.languageidentifier, LanguageIdentifier.identifier))\
        .order_by(Language.pk)


class LanguoidCsvDump(CsvDump):
    def query(self, req):
        return _lang_query()


class LanguoidN3Dump(N3Dump):
    def query(self, req):
        return _lang_query()


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


class Jit(Representation):
    mimetype = 'application/vnd.clld.jit+json'
    send_mimetype = 'application/json'
    extension = 'jit.json'

    @staticmethod
    def node(l, depth, limit=None):
        return {
            'id': l.id,
            'name': l.name,
            'data': {'level': l.level.value},
            'children':
            [Jit.node(c, depth + 1, limit=limit) for c in l.children]
            if depth < limit else []}

    def render(self, root, req, dump=True):
        depth_limit = req.params.get('depth')
        if depth_limit:
            depth_limit = int(depth_limit)

        res = Jit.node(root, 0, limit=depth_limit or 5)
        return pyramid_render('json', res, request=req) if dump else res
