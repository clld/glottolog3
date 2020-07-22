"""
Change modification date of newly added languoids
"""
from datetime import datetime

from sqlalchemy import create_engine
from clldutils.apilib import assert_release

from glottolog3.cli_util import get_releases


def register(parser):  # pragma: no cover
    parser.add_argument('--previous', help='previous version to compare against', default=None)


def run(args):  # pragma: no cover
    version = assert_release(args.repos.repos)
    if args.previous:
        last = args.previous
    else:
        rels = get_releases(args)
        last = sorted(set(rel.tag for rel in rels) - {version}, key=lambda s: float(s[1:]))[-1][1:]
    print('previous version: {0}'.format(last))

    cdb = create_engine('postgresql://postgres@/glottolog3')
    ldb = create_engine('postgresql://postgres@/glottolog-{0}'.format(last))
    sql = "select id from language as l, languoid as ll where l.pk = ll.pk and ll.level = 'language'"

    current = set(r[0] for r in cdb.execute(sql))
    last = set(r[0] for r in ldb.execute(sql))
    for gc in sorted(current - last):
        cdb.execute(
            "update language set updated = %s where id = %s", (datetime.utcnow(), gc))
