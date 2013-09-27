# -*- coding: utf-8 -*-
import sys
import transaction
import json

from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from clld.scripts.util import parsed_args
from clld.db.meta import DBSession

from glottolog3.models import Ref, Languoid


def main(args):  # pragma: no cover
    with transaction.manager:
        for ref in DBSession.query(Ref):
            ref.doctypes_str = ', '.join(o.id for o in ref.doctypes)
            ref.providers_str = ', '.join(o.id for o in ref.providers)


if __name__ == '__main__':
    main(parsed_args())
