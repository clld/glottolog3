"""
Download the SQL dump of a specified Glottolog release
"""
from glottolog3.cli_util import get_release


def register(parser):  # pragma: no cover
    parser.add_argument('version', nargs='+', metavar='VERSION')


def run(args):  # pragma: no cover
    for version in args.version:
        get_release(args, version).download_sql_dump(args.log)
