# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

import pytz
import transaction
from clld.scripts.util import parsed_args
from clld.db.models.common import Dataset
from clld.db.meta import DBSession


def main(args):
    with transaction.manager:
        dataset = DBSession.query(Dataset).one()
        dataset.name = 'Glottolog %s' % args.version
        dataset.updated = datetime.utcnow().replace(tzinfo=pytz.utc)


if __name__ == '__main__':  # pragma: no cover
    main(parsed_args((("--version",), dict(default=""))))
