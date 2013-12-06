from cStringIO import StringIO
from xml.etree import cElementTree as et

from pyramid.httpexceptions import HTTPFound

from clld.web.adapters.base import Representation, Index

from glottolog3.models import LanguoidLevel


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
    mimetype = 'text/vnd.clld.treeview+html'
    send_mimetype = 'text/html'
    extension = 'treeview.html'
    template = 'language/treeview_html.mako'


class PhyloXML(Representation):
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
