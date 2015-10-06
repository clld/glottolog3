# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import transaction
from clld.util import jsonload
from clld.db.meta import DBSession
from clld.db.models.common import Config, Source

from glottolog3.scripts.util import get_args


def main(args):
    repls = set((i['id'], i['replacement']) for i in
                jsonload(args.data_dir.joinpath('scripts', 'monster-replacements.json')))

    with transaction.manager:
        for ref_id, repl_id in repls:
            ref = Source.get('%s' % ref_id, default=None)
            if ref:
                Config.add_replacement(
                    ref, '%s' % repl_id, session=DBSession, model=Source)
                DBSession.delete(ref)
    args.log.info('%s replacements' % len(repls))


if __name__ == '__main__':  # pragma: no cover
    main(get_args())
