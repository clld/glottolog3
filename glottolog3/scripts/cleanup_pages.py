# -*- coding: utf-8 -*-
from copy import copy

import transaction

from clld.scripts.util import parsed_args
from clld.db.models.common import Source
from clld.db.meta import DBSession

from glottolog3.models import Ref
from glottolog3.scripts.util import compute_pages


def main(args):  # pragma: no cover
    with transaction.manager:
        for source in DBSession.query(Ref)\
                .filter(Source.pages_int == None)\
                .filter(Source.pages != ''):
            if source.pages:
                start, end, number = compute_pages(source.pages)
                if start is not None:
                    source.startpage_int = start
                if end is not None:
                    source.endpage_int = end
                if number:
                    source.pages_int = number


if __name__ == '__main__':
    main(parsed_args())