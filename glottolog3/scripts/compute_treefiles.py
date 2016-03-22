# -*- coding: utf-8 -*-
import sys
import transaction
import codecs
from xml.etree import cElementTree as et

try:
    from Bio.Phylo import write
    from Bio.Phylo.BaseTree import Tree, Clade
except ImportError:
    print('BioPython is required to create tree files.')
    raise
from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.models.common import Language

from glottolog3.models import Languoid, LanguoidStatus, LanguoidLevel


def add_children(clade, lang, label_func):
    for child in sorted(lang.children, key=lambda l: l.name):
        subclade = Clade(branch_length=1, name=label_func(child))
        clade.clades.append(subclade)
        if child.children:
            add_children(subclade, child, label_func)


def newick(args, trees, lang=None):
    p = args.module_dir.joinpath(
        'static', 'trees', 'tree-%s-newick.txt' % (lang.id if lang else 'glottolog',))
    with codecs.open(p, 'w', 'utf8') as fp:
        write(trees, fp, 'newick')


class PhyloXML(object):
    namespace = 'http://www.phyloxml.org'

    def __init__(self, root, req):
        """
        <phyloxml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.phyloxml.org http://www.phyloxml.org/1.10/phyloxml.xsd" xmlns="http://www.phyloxml.org">
        002	<phylogeny rooted="false">
        """
        et.register_namespace('', self.namespace)
        self.req = req
        self.e = self.element('phyloxml')
        phylogeny = self.element('phylogeny', rooted="true")
        #rect = self.element('rectangular')
        #rect.append(self.element('alignRight', 'true'))
        #params = self.element('parameters')
        #params.append(rect)
        #render = self.element('render')
        #render.append(params)
        #phylogeny.append(render)
        """
        <render>
        <parameters>
                <rectangular>
                        <alignRight>true</alignRight>
                </rectangular>
        </parameters>
        </render>
        """
        phylogeny.append(self.element('name', root.name))
        phylogeny.append(self.element('description', root.name))
        clade = self.clade(root)
        self.append_children(clade, root)
        phylogeny.append(clade)
        self.e.append(phylogeny)

    def element(self, name, text=None, **kw):
        e = et.Element('{%s}%s' % (self.namespace, name), **kw)
        if text:
            e.text = text
        return e

    def clade(self, lang):
        e = self.element('clade', branch_length="0.2")
        if lang.level == LanguoidLevel.language:
            e.append(self.element('name', lang.name))
            ann = self.element('annotation')
            ann.append(self.element('desc', ' > '.join(reversed([l.name for l in lang.get_ancestors()]))))
            ann.append(self.element('uri', self.req.resource_url(lang)))
            e.append(ann)
        return e

    def append_children(self, clade, lang):
        children = [l for l in lang.children if
                    l.level in [LanguoidLevel.language, LanguoidLevel.family]]
        for child in sorted(children, key=lambda l: l.name):
            subclade = self.clade(child)
            if child.children:
                self.append_children(subclade, child)
            clade.append(subclade)

    def write(self, p):
        tree = et.ElementTree(element=self.e)
        with open(str(p), 'w') as fp:
            tree.write(fp, encoding='utf8', xml_declaration=True)


def main(args):  # pragma: no cover
    trees = []

    def label_func(lang):
        # replace , and () in language names.
        label = '%s [%s]' % (
            lang.name.replace(',', '/').replace('(', '{').replace(')', '}'), lang.id)
        if lang.hid and len(lang.hid) == 3:
            label += '[%s]' % lang.hid
        if lang.level == LanguoidLevel.language:
            label += '-l-'
        return label

    with transaction.manager:
        # loop over top-level families and isolates
        for l in DBSession.query(Languoid)\
                .filter(Language.active)\
                .filter(Languoid.status == LanguoidStatus.established)\
                .filter(Languoid.father_pk == None):
            tree = Tree(
                root=Clade(name=label_func(l), branch_length=1),
                id=l.id,
                name=label_func(l))

            if l.level != LanguoidLevel.family:
                # put isolates into a dummy family of their own!
                subclade = Clade(branch_length=1, name=label_func(l))
                tree.root.clades.append(subclade)
            else:
                subclade = tree.root

            add_children(subclade, l, label_func)

            #phyloxml = PhyloXML(l, args.env['request'])
            #phyloxml.write(args.module_dir.joinpath('static', 'trees', 'tree-%s-phylo.xml' % l.id))

            trees.append(tree)
            newick(args, tree, l)

    newick(args, trees)


if __name__ == '__main__':
    main(parsed_args(bootstrap=True))
    sys.exit(0)
