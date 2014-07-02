# -*- coding: utf-8 -*-
from collections import defaultdict

import transaction

from clld.scripts.util import parsed_args
from clld.db.models.common import Language
from clld.db.meta import DBSession

from glottolog3.models import Languoid


def main(args):  # pragma: no cover
    diff = []
    with transaction.manager:
        for l in DBSession.query(Languoid):
            try:
                l.jqtree(icon_map=defaultdict(list))
            except ValueError:
                print 'problems:', l.pk, l.id, l.name
        #for l in DBSession.query(Language):
        #    hname = l.jsondatadict.get('hname')
        #    if hname and hname != l.name:
        #        diff.append((l.id, l.name, hname))

    #maxlname = max(len(n[1]) for n in diff)
    #print 'abcd1234', '|', 'name'.ljust(maxlname), '|', 'hname'
    #print '---------+-' + '-' * maxlname + '-+---------'
    #for id, name, hname in diff:
    #    print id, '|', name.ljust(maxlname), '|', hname
    #print '(%s rows)' % len(diff)


if __name__ == '__main__':
    main(parsed_args())