# -*- coding: utf-8 -*-
from copy import copy

import transaction

from clld.scripts.util import parsed_args
from clld.db.models.common import Source
from clld.db.meta import DBSession

from glottolog3.scripts.import_refs import FIELD_MAP


def main(args):  # pragma: no cover
    with transaction.manager:
        for source in DBSession.query(Source).filter(Source.jsondata != None):
            d = copy(source.jsondata)
            for s, t in FIELD_MAP.items():
                if t is None and s in d:
                    del d[s]
            source.jsondata = d


if __name__ == '__main__':
    main(parsed_args())
