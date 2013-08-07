# -*- coding: utf-8 -*-
import sys
import transaction

from clld.scripts.util import parsed_args
from clld.db.meta import DBSession

from glottolog3.models import Languoid


def main(args):  # pragma: no cover
    with transaction.manager:
        for l in DBSession.query(Languoid).filter(Languoid.father_pk != None):
            family = None
            for ll in l.get_ancestors():
                family = ll
            if family:
                l.family = family


if __name__ == '__main__':
    main(parsed_args())
    sys.exit(0)
