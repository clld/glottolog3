"""
Create the static HTML archive to lookup old Glottolog releases
"""
import pathlib

from glottolog3.cli_util import get_releases
from glottolog3 import static_archive


def register(parser):
    parser.add_argument(
        '--output',
        type=pathlib.Path,
        default=pathlib.Path('archive'),
    )


def run(args):
    rels = get_releases(args)
    for rel in rels:
        rel.load_sql_dump(args.log)

    static_archive.create([rel.version for rel in rels], args.output)
    args.log.info('static archive created in {0}'.format(args.output))
