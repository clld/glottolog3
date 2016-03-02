# -*- coding: utf-8 -*-
import sys
import transaction

from newick import Node, write

from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.models.common import Language

from glottolog3.models import Languoid, LanguoidStatus, LanguoidLevel


def node(lang, descendants_):
    # replace , and () in language names.
    label = '%s [%s]' % (
        lang.name.replace(',', '/').replace('(', '{').replace(')', '}').replace(':', ' '),
        lang.id)
    if lang.hid and len(lang.hid) == 3:
        label += '[%s]' % lang.hid
    return Node.create(
        name="'" + label.replace("'", "\\'") + "'", length='1', descendants=descendants_)


def descendants(lang):
    for child in sorted(lang.children, key=lambda l: l.name):
        yield node(child, descendants(child))


def main(args):  # pragma: no cover
    trees = []

    with transaction.manager:
        # loop over top-level families and isolates
        for l in DBSession.query(Languoid)\
                .filter(Language.active)\
                .filter(Languoid.status == LanguoidStatus.established)\
                .filter(Languoid.father_pk == None)\
                .order_by(Languoid.name):
            tree = node(l, descendants(l))
            if l.level != LanguoidLevel.family:
                tree = node(l, [tree])
            trees.append(tree)

    write(trees, 'tree-glottolog-newick.txt')


if __name__ == '__main__':
    main(parsed_args(bootstrap=True))
    sys.exit(0)
