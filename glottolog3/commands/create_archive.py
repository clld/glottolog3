"""
Create the static HTML archive to lookup old Glottolog releases

https://doi.org/10.5281/zenodo.23421523

"""
import pathlib

from glottolog3.cli_util import get_releases
from glottolog3 import static_archive


def register(parser):  # pragma: no cover
    parser.add_argument('version')
    parser.add_argument('glottocode2version', type=pathlib.Path)
    parser.add_argument(
        '--output',
        type=pathlib.Path,
        default=pathlib.Path('archive'),
    )


def run(args):  # pragma: no cover
    rel, older = None, []
    for rel in get_releases(args):
        if rel.version == args.version:
            break
        older.append(rel)
    else:
        raise ValueError(args.version)
    assert rel
    rel.load_sql_dump(args.log, out=args.output)

    static_archive.create(rel.version, list(reversed(older)), args.glottocode2version, args.output)
    args.log.info('static archive created in %s', args.output)
