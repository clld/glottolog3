"""
Create the static HTML archive to lookup old Glottolog releases

Archived and made available as version of https://doi.org/10.5281/zenodo.23421523

This command creates a subdirectory <version> of the output directory and places two files in it:
- glottolog-<version>.zip
- glottocode2version.json
"""
import pathlib

from glottolog3.cli_util import get_release
from glottolog3 import static_archive


def register(parser):  # pragma: no cover
    parser.add_argument('version')
    parser.add_argument('--output', type=pathlib.Path, default=pathlib.Path('archive'))


def run(args):  # pragma: no cover
    args.output.mkdir(exist_ok=True, parents=True)
    rel = get_release(args, args.version)
    assert rel
    rel.load_sql_dump(args.log, out=args.output)

    static_archive.create(rel.version, args.output)
    args.log.info('static archive created in %s', args.output)
