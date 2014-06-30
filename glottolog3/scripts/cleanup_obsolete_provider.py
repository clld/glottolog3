# -*- coding: utf-8 -*-
import json

import transaction
from clld.scripts.util import parsed_args
from clld.db.meta import DBSession
from clld.db.models.common import Config, Source

from glottolog3.models import Ref, Provider


def main(args):
    with open(args.data_file('2.3', 'obsolete_refs.json')) as fp:
        obsolete = json.load(fp)

    with transaction.manager:
        provider = Provider.get('glottolog20121')
        for ref in provider.refs:
            if ref.id in obsolete:
                Config.add_replacement(ref, None, session=DBSession, model=Source)
                DBSession.delete(ref)
            else:
                assert len(ref.providers) > 1

        DBSession.flush()
        DBSession.delete(provider)


if __name__ == '__main__':  # pragma: no cover
    main(parsed_args())