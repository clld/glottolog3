# -*- coding: utf-8 -*-
from collections import Counter

import transaction
from clld.db.meta import DBSession
from clld.db.models.common import Config, Source

from glottolog3.scripts.util import match_obsolete_refs, get_args


def main(args):
    stats = Counter(hits=0, misses=0)
    delete = []
    with transaction.manager:
        for ref, repl in match_obsolete_refs(args):
            if repl:
                print '%s --> %s' % (ref.id, repl.id)
                delete.append((ref.id, repl.id))
                stats.update(['hits'])
            else:
                stats.update(['misses'])
    with transaction.manager:
        for ref_id, repl_id in delete:
            ref = Source.get(ref_id, default=None)
            if ref:
                Config.add_replacement(ref, repl_id, session=DBSession, model=Source)
                DBSession.delete(ref)
    args.log.info('%s' % stats)


if __name__ == '__main__':  # pragma: no cover
    main(get_args())
