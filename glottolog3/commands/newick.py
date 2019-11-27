"""
Create the newick download file
"""
import collections


def run(args):
    nodes = collections.OrderedDict((l.id, l) for l in args.repos.languoids())
    trees = []
    for lang in nodes.values():
        if not lang.lineage and not lang.category.startswith('Pseudo '):
            ns = lang.newick_node(nodes=nodes).newick
            if lang.level == args.repos.languoid_levels.language and not ns.startswith('('):
                # an isolate without dialects: we wrap it in a pseudo-family with the
                # same name and ID.
                ns = '({0}){0}'.format(ns)
            trees.append('{0};'.format(ns))
    fname = args.pkg_dir.joinpath('static', 'download', 'tree-glottolog-newick.txt')
    fname.write_text('\n'.join(trees), encoding='utf8')
    args.log.info('{0} written'.format(fname))
